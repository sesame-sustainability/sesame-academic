import os

import pandas as pd
import numpy as np

import math

from core import validators, conditionals
from core.inputs import ContinuousInput, OptionsInput, Default, CategoricalInput

PATH = os.getcwd() + '/analysis/system/onecar/'

class OneCar:

    @classmethod
    def user_inputs(self):
        inputs = pd.read_csv(PATH + 'inputs.csv')
        print("Enter Powertrain type:")
        print(inputs['Vehicle Type'][~pd.isna(inputs['Vehicle Type'])].to_string(header=None))
        self.car_type = inputs['Vehicle Type'].iloc[int(input())]
        print("Enter Region:")
        print(inputs['Region'][~pd.isna(inputs['Region'])].to_string(header=None))
        self.region = inputs['Region'].iloc[int(input())]
        print("Enter City:")
        print(inputs[self.region][~pd.isna(inputs[self.region])].to_string(header=None))
        self.city = inputs[self.region].iloc[int(input())]
        if self.car_type == 'BEV':
            print("Choose Charging Profile:")
            print(inputs['Charge Profile'][~pd.isna(inputs['Charge Profile'])].to_string(header=None))
            self.cptype = inputs['Charge Profile'].iloc[int(input())]
        print("Enter Vehicle Size:")
        print(inputs['Vehicle Size'][~pd.isna(inputs['Vehicle Size'])].to_string(header=None))
        self.size = inputs['Vehicle Size'].iloc[int(input())]
        print("Enter Vehicle MPG:")
        print(inputs['Vehicle MPG'][~pd.isna(inputs['Vehicle MPG'])].to_string(header=None))
        x = int(input())
        if x == 0:
            self.vehicle_mpg = 'Custom'
            print("Enter city MPG:")
            self.mpg_c = float(input())
            print("Enter highway MPG:")
            self.mpg_hw = float(input())
        else:
            models_list = pd.read_csv(self.size + '_' + self.car_type + '.csv')
            print("Choose Vehicle Model:")
            print(models_list['Vehicle Model'].to_string(header=None))
            x = int(input())
            row = models_list.iloc[x, :]
            self.vehicle_mpg = row['Vehicle Model']
            self.mpg_c = row['MPG_city']
            self.mpg_hw = row['MPG_hw']
        print("Enter fraction driven in city:")
        self.f_city = float(input())

    def read_vars(self):
        self.location_matrix = pd.read_csv(PATH + self.region + '.csv')
        self.T = pd.read_csv(PATH + 'Temperatures' + '.csv', usecols=[self.city]).rename(columns={self.city: 'T'})

        self.p = self.location_matrix.filter(['dy', 'coal', 'hydro', 'gas', 'nuclear', 'petroleum', 'wind', 'solar', 'other'])
        self.p.loc[:, 'solar'] = self.p.loc[:, 'solar'] * (1.476)
        self.I_f = self.location_matrix.filter(['I_f'])

        self.final = pd.read_csv(PATH + 'final.csv', index_col='dy')
        self.time = self.location_matrix.filter(['hd', 'dw'])

    def emission_intensity(self):
        hours = 8760
        p_total = self.p.iloc[:, 1:8].sum(axis=1)

        p_fossil = np.multiply((self.p['coal'] + self.p['petroleum'] + self.p['gas']).values,
                               1 + np.divide(self.p['other'].values, p_total.values))
        p_fossil_fraction = np.divide(p_fossil, p_total.values)
        I = self.I_f.div(1 - self.td_loss).mul(p_fossil_fraction, axis=0)

        return I

    def cp(self):
        charge_profile = pd.read_csv('charge_profile.csv', index_col=['hd'])
        dist_profile = pd.read_csv('dist_profile.csv', index_col=['hd'])
        epsilon = pd.DataFrame(columns=['e', 'd'], index=self.time.index)
        cp_weekday = self.cptype + '_weekday'
        cp_weekend = self.cptype + '_weekend'

        for h in range(1, 25):
            epsilon.loc[((self.time['dw'] == 1) | (self.time['dw'] == 7)) & (self.time['hd'] == h), 'e'] = charge_profile.loc[
                h, cp_weekend]
            epsilon.loc[(self.time['dw'] != 1) & (self.time['dw'] != 7) & (self.time['hd'] == h), 'e'] = charge_profile.loc[
                h, cp_weekday]
            epsilon.loc[((self.time['dw'] == 1) | (self.time['dw'] == 7)) & (self.time['hd'] == h), 'd'] = dist_profile.loc[
                h, 'weekend']
            epsilon.loc[(self.time['dw'] != 1) & (self.time['dw'] != 7) & (self.time['hd'] == h), 'd'] = dist_profile.loc[h, 'weekday']

        return epsilon

    def F_calc(self):

        F = pd.DataFrame(columns=['F'], index=self.T.index)
        k_c = {'BEV': 2.385, 'ICEV': 1.305, 'HEV': 0.63, 'PHEV': 1.53};
        k_h = {'BEV': 2.05714285714286, 'ICEV': 1.23428571428571, 'HEV': 1.64571428571429, 'PHEV': 1.8};
        k_cold = k_c[self.car_type]
        k_hot = k_h[self.car_type]
        Th = 23.9;
        Tc = 15.5;
        if (self.car_type == 'ICEV' or self.car_type == 'HEV'):
            F_city_OR_ICEV = 33.7 / self.mpg_c;
            F_HW_OR_ICEV = 33.7 / self.mpg_hw;
            F_city = F_city_OR_ICEV * 0.9606 - 0.04248;
            F_hw = F_HW_OR_ICEV * 0.9171 - 0.04812;
        else:
            F_city_OR_ICEV = 33.7 / 29;
            F_HW_OR_ICEV = 33.7 / 41;
            F_city_OR = 33.7 / self.mpg_c;
            F_HW_OR = 33.7 / self.mpg_hw;
            h_city = (0.96 * F_city_OR_ICEV + 0.43) / (1.29 * F_city_OR_ICEV + 0.79);
            h_hw = (0.92 * F_HW_OR_ICEV + 0.43) / (1.35 * F_HW_OR_ICEV + 0.18);
            F_city = F_city_OR * (0.7 + 0.3 * h_city);
            F_hw = F_HW_OR * (0.7 + 0.3 * h_hw);

        F0 = self.f_city * F_city + (1 - self.f_city) * F_hw;
        for lab, row in F.iterrows():
            if self.T.loc[lab, 'T'] < Tc:
                T0 = Tc
                k = k_cold
            elif self.T.loc[lab, 'T'] > Th:
                T0 = Th
                k = k_hot
            else:
                T0 = 0
                k = 0
            row.F = F0 * (1 + k * abs(self.T.loc[lab, 'T'] - T0) / 100);

        return F

    def main(self):
        self.td_loss = 0.049
        self.read_vars()
        if self.car_type == 'BEV':
            I = self.emission_intensity()
        else:
            I = pd.DataFrame(columns=['I_f'], index=self.I_f.index)
            I.loc[:, :] = 262.8
        epsilon = self.cp();
        F = self.F_calc();
        intermediate = pd.DataFrame(columns=['IE', 'FD', 'dy'])
        intermediate.dy = self.location_matrix.dy
        intermediate.IE = I.multiply(epsilon['e'], axis=0)
        intermediate.FD = F.multiply(epsilon['d'], axis=0)
        days = int(intermediate.shape[0] / 24)
        intermediate = intermediate.groupby('dy')

        for i in range(1, days + 1):
            group = intermediate.get_group(i)
            self.final.loc[i, 'IE_day'] = group.IE.sum()
            self.final.loc[i, 'FD_day'] = group.FD.sum()

        self.final.loc[:, 'Total'] = ((self.final.IE_day.multiply(self.final.FD_day)).multiply(self.final.day_contribution)).values
        emissions = self.final['Total'].sum()
        print(emissions)
        return emissions

onecar = OneCar()
onecar.user_inputs()
emissions = onecar.main()
