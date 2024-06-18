import json
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
import math
import time
import json

from core import validators, conditionals
from core.common import DataSource, InputSource, Versioned
from core.inputs import PercentInput, OptionsInput, Default, InputSet, Option, ShareTableInput, CategoricalInput, Tooltip, InputGroup, ContinuousInput

import pyomo.environ as pe
import pyomo.opt as po

PATH = os.path.dirname(__file__)
DATA = {
    'D_data': pd.read_csv(os.path.join(PATH, 'D_data.csv')),
}

class PPS(DataSource, InputSource, Versioned):
    table = os.path.join(PATH, 'data_source.csv')

    @classmethod
    def user_inputs(cls):
        return [
            CategoricalInput(
                'region', 'Region',
                defaults=[Default('Texas')],
                tooltip=Tooltip(
                    'Region determines where renewable generation sites (solar & wind farms) are centered. If there is only 1 site, it is located at the region center.'),
            ),
            #OptionsInput(
            #    'optimize_shares', 'Optimize energy breakdown',
            #    options=['yes', 'no'],
            #    defaults=[Default('yes')],
            #),
            OptionsInput(
                'D_year', 'Demand year',
                options=[
                    Option('2007', conditionals=[conditionals.input_equal_to('region', 'Texas')]),
                    Option('2008', conditionals=[conditionals.input_equal_to('region', 'Texas')]),
                    Option('2009', conditionals=[conditionals.input_equal_to('region', 'Texas')]),
                    Option('2010', conditionals=[conditionals.input_equal_to('region', 'Texas')]),
                    Option('2011', conditionals=[conditionals.input_equal_to('region', 'Texas')]),
                    Option('2012', conditionals=[conditionals.input_equal_to('region', 'Texas')]),
                    Option('2013', conditionals=[conditionals.input_equal_to('region', 'Texas')]),
                    Option('2007', conditionals=[conditionals.input_equal_to('region', 'Atlantic')]),
                    Option('2008', conditionals=[conditionals.input_equal_to('region', 'Atlantic')]),
                    Option('2009', conditionals=[conditionals.input_equal_to('region', 'Atlantic')]),
                    Option('2010', conditionals=[conditionals.input_equal_to('region', 'Atlantic')]),
                    Option('2011', conditionals=[conditionals.input_equal_to('region', 'Atlantic')]),
                    Option('2012', conditionals=[conditionals.input_equal_to('region', 'Atlantic')]),
                    Option('2013', conditionals=[conditionals.input_equal_to('region', 'Atlantic')]),
                    '2016', '2017', '2018', '2019', '2020', '2021',
                ],
                defaults=[Default('2021')],
                tooltip=Tooltip('Year of demand profile shape.')
            ),
            ShareTableInput(
                'demand', '% of power supply from',
                columns=[None],
                rows=[
                    ShareTableInput.Row(
                        'Solar',
                        cells=[
                            ShareTableInput.Cell(defaults=[Default(30)]),
                        ],
                    ),
                    ShareTableInput.Row(
                        'Wind',
                        cells=[
                            ShareTableInput.Cell(defaults=[Default(30)]),
                        ],
                    ),
                    ShareTableInput.Row(
                        'Nuclear',
                        cells=[
                            ShareTableInput.Cell(
                                defaults=[Default(30)],
                            ),
                        ],
                    ),
                    ShareTableInput.Row(
                        'Natural gas',
                        cells=[
                            ShareTableInput.Cell(
                                defaults=[Default(10)],
                                remainder=True,
                                column_total=100,
                            ),
                        ],
                    ),

                ],
                #conditionals=[conditionals.input_equal_to('optimize_shares', 'no')],
            ),
            OptionsInput(
                'storage_type', 'Energy storage type',
                #options=['thermal', 'lithium ion battery', 'compressed air'],
                options=['lithium ion battery'],
                defaults=[Default('lithium ion battery')],
            ),
            ContinuousInput(
                'd_cG', 'Change in renewable generation cost, vs. today (%)',
                defaults=[Default(0)],
                validators=[validators.numeric(), validators.gte(-100)]
            ),
            ContinuousInput(
                'd_cS', 'Change in storage costs, vs. today (%)',
                defaults=[Default(0)],
                validators=[validators.numeric(), validators.gte(-100)]
            ),
            ContinuousInput(
                'd_c_NGfuel', 'Change in natural gas price, vs. today (%)',
                defaults=[Default(0)],
                validators=[validators.numeric(), validators.gte(-100)]
            ),
            PercentInput(
                'M', 'Monthly self discharge (%)',
                defaults=[Default(5)],
            ),
# @Scott, I (Ian) temporarily moved categorical inputs below outside of group, because categorical ones did not work inside group.
            InputGroup('renewable_profiles','Renewable Profiles', children=[
                OptionsInput(
                    'year', 'Weather year',
                    options=['2007', '2008', '2009', '2010', '2011', '2012', '2013'],
                    defaults=[Default('2013')],
                    tooltip=Tooltip('Year of hourly weather data used to estimate hourly solar & wind generation.')
                ),
                CategoricalInput(
                    'area_width', 'Generation area width', unit="mi",
                    defaults=[Default(240)],
                    tooltip=Tooltip(
                        'Width of area containing renewable generation sites (solar & wind farms). Distance between furthest apart sites, west to east, or north to south. The area is ~square, such that area ~ width^2. For reference, the contiguous US is ~2800 miles wide.'),
                ),
                CategoricalInput(
                    'sites', 'Generation sites',
                    defaults=[Default(4)],
                    tooltip=Tooltip(
                        'Number of renewable generation sites (solar/wind farms) in the generation area. Sites are spaced evenly on a ~square grid with center = the region center. Solar & wind farms are co-located.'),
                ),
                CategoricalInput(
                    'spacing', 'Site spacing',
                    unit='mi',
                    tooltip=Tooltip(
                        'Distance between adjacent renewable generation sites (solar/wind farms). Sites are spaced evenly on a ~square grid with center = the region center. Solar & wind farms are co-located.'),
                ),
            ]),

            #emissions related inputs
            InputGroup('emissions_limits', 'Emissions limits', children=[
            #    OptionsInput(
            #        'cap', 'Include an emissions intensity cap?',
            #        options=['yes', 'no'],
            #        defaults=[Default('no')],
            #        conditionals=[conditionals.input_equal_to('optimize_shares', 'yes')],
            #    ),
            #    ContinuousInput(
            #        'e_cap', 'Emissions intensity cap (g/kWh)',
            #        defaults=[Default(100)],
            #        validators=[validators.numeric(), validators.gte(50)],
            #        conditionals=[conditionals.input_equal_to('cap', 'yes')],
            #    ),
                ContinuousInput(
                    'e_tax', 'Tax on emitted carbon ($/ton)',
                    defaults=[Default(40)],
                    validators=[validators.numeric(), validators.gte(0)],
                ),
            ]),
        ]

    def __init__(self):
        #self.G_data = DATA['G_data']
        self.D_data = DATA['D_data']

    def prepare(self, input_set):
        super().prepare(input_set)

        # these values are percents
        self.f_solar = self.demand[0] / 100.0
        self.f_wind = self.demand[1] / 100.0
        self.f_nuclear = self.demand[2] / 100.0
        self.f_ng = self.demand[3] / 100.0
        self.d_cG /= 100.0
        self.d_cS /= 100.0
        self.d_c_NGfuel /= 100.0
        self.M /= 100
        self.hourly_storage_efficiency = math.exp(-self.M * 1/730)
        self.e_tax /= 1000000 # $/g

    def run(self):
        return self.get_output_values()


    def collecting_D(self):

        region_year = self.region + '_' + self.D_year
        D_underlined = self.D_data[region_year]
        D_underlined = D_underlined.reset_index(drop=True)

        return (D_underlined)


    def collecting_G_and_CF_for_VRE(self, VRE_type):
        if self.region != 'North Central':
            self.G_data = pd.read_csv(os.path.join(PATH, 'gen_profiles_with_site_number_' + self.region + '.csv'), dtype = 'unicode')
        elif self.region == 'North Central':
            self.G_data = pd.read_csv(os.path.join(PATH, 'gen_profiles_with_site_number_North_Central.csv'), dtype = 'unicode')

        if self.area_width == 0: # temp hack cuz 1 row bugs categorical input ops
             self.sites = 1

        if VRE_type == 'solar':
            G_data = self.G_data[f'solararea_width{self.area_width}sites{self.sites}year{self.year}{self.region}']
        elif VRE_type =='wind':
            G_data = self.G_data[f'windarea_width{self.area_width}sites{self.sites}year{self.year}{self.region}']

        CF = float(G_data[9])

        G_data_hour_trend = G_data.iloc[11:]
        G_data_hour_trend = G_data_hour_trend.reset_index(drop=True)
        G_data_hour_trend = pd.to_numeric(G_data_hour_trend)

        G = G_data_hour_trend * CF #kWh/kW
        return (G, CF, G_data_hour_trend)


    def do_optimization(self):
        (D_underlined) = self.collecting_D()
        self.D_total = sum(D_underlined)
        (G_solar_perkW, CF_solar, Gs_shape) = self.collecting_G_and_CF_for_VRE('solar')
        (G_wind_perkW, CF_wind, Gw_shape) = self.collecting_G_and_CF_for_VRE('wind')

        # placeholder data:
        self.TD_losses = 4.7/100 #percent loss
        #self.TD_losses = 0

        # storage costs if power capacity (PC) & energy capacity (EC) capex are unbundled
        c_CPC = 0
        c_DPC = 0 # power capacity cost is now included/bundled with energy capacity (EC) cost in 1 cost per EC, assuming EC/DPC (duration) is fixed
        self.c_CPC = c_CPC * (1 + self.d_cS)
        self.c_DPC = c_DPC * (1 + self.d_cS)
        c_E = 3/1000  # $/kWh. c_E = cost of energy charged = storage VOM. source = Mallapragad et al 2020. can update later to better reflect degradation. and/or make storage life depend on use.
        self.c_E = c_E * (1 + self.d_cS)
        self.OCC_EC = 287 * (1 + self.d_cS) # $/kWh. 2022 installed capex of utility-scale LIB w/ duration = 4hr. source = 2021 ATB advanced case. LIB pack is roughly half of capex. rest includes: inverter, BOS, install labor, profit.
        self.FOMstorage = 29/4 * (1 + self.d_cS)  # $/kWh/yr. source = above. source link = https://atb.nrel.gov/electricity/2021/utility-scale_battery_storage

        #wind costs main source = 2021 ATB - 2022 advanced case. source link = https://atb.nrel.gov/electricity/2021/residential_pv
        self.OCCw = 1235 * (1 + self.d_cG) # $/kW, land based wind
        self.FOMw = 41 * (1 + self.d_cG)  # $/kW/yr

        #solar costs
        f_util = .65 # share of US PV that is utility scale in ~2020. source = https://dirt.asla.org/2021/05/17/utility-scale-solar-energy-will-need-land-the-size-of-connecticut/#:~:text=Utility%2Dscale%20solar%20now%20accounts,of%20big%20solar%20power%20facilities.
        f_res = 1 - f_util # share of PV that is residential
        OCCutil = 1229
        OCCres = 2369
        FOMutil = 22
        FOMres = 25
        self.OCCs = (f_util * OCCutil + f_res * OCCres) * (1 + self.d_cG)
        self.FOMs = (f_util * FOMutil + f_res * FOMres) * (1 + self.d_cG) # $/kW/yr

        #ng costs
        fCC = .6 # frxn of NG that is combined cycle. for 2016, EIA reports 53%, and CC deployments since have exceeded that share. source link = https://www.eia.gov/todayinenergy/detail.php?id=34172
        fSC = 1 - fCC #frxn of NG that is simple cycle
        OCC_CC = 1042  # $/kW. source = ATB. avg CF
        OCC_SC = 915  # $/kW. source = ATB. avg CF
        self.OCCng = fCC * OCC_CC + fSC * OCC_SC  # $/kW
        FOM_CC = 27 # $/kW/yr. source = ATB. avg CF
        FOM_SC = 21  # $/kW/yr. source = ATB. avg CF
        self.FOMng = fCC * FOM_CC + fSC * FOM_SC   # $/kW/yr
        VOM_CC = 5/1000 # $/kWh. source = ATB. avg CF. non-fuel VOM.
        VOM_SC = 2/1000  # $/kWh. source = ATB. avg CF. non-fuel VOM.
        self.VOMng = fCC * VOM_CC + fSC * VOM_SC   # $/kWh

        #nuclear costs 2021 ATB - 2022 moderate case
        self.OCCnuclear = 7257 # $/kWh
        self.FOMnuclear = 145 # $/kW/yr
        VOMnuclear = 2 # $/MWh
        self.VOMnuclear = VOMnuclear / 1000 # $/kWh

        #setting lifetimes (years)
        self.Lw = 20
        self.Ls = 30
        self.Lng = 20
        self.Lec = 15
        self.Lnuclear = 60

        # combine costs that are proportional to capacity, into single [cost of capacity] numbers.
        self.c_GCw = (self.OCCw / self.Lw + self.FOMw) # $/kW/yr
        self.c_GCs = (self.OCCs / self.Ls + self.FOMs) # $/kW/yr
        self.c_GC_ng = self.OCCng / self.Lng + self.FOMng # $/kW/yr
        self.c_EC = self.OCC_EC / self.Lec + self.FOMstorage # $/kWh/yr
        self.c_GCnuclear = self.OCCnuclear / self.Lnuclear + self.FOMnuclear

        #ATB fuel costs
        self.ng_fuel_cost = 2.99 * (1 + self.d_c_NGfuel) #$/MMBtu
        ng_heat_rate = 6.741061411 #MMBtu/MWh
        self.ng_heat_rate = ng_heat_rate / 1000 #MMBtu/kWh

        self.nuclear_fuel_cost = 0.68 #$/MMBtu
        nuclear_heat_rate = 10.46 # MMBtu/MWh
        self.nuclear_heat_rate = nuclear_heat_rate / 1000 #MMBtu/kWh

        #emisions values
        #emissions values
        self.e_CPC = 0 # gCO2/kW
        self.e_DPC = 0 # gCO2/kW
        self.e_EC = 70  # gCO2/Wh moz-extension://a8633502-bc18-4aff-8d22-0e845d8b90fd/enhanced-reader.html?openApp&pdf=https%3A%2F%2Fmdpi-res.com%2Fd_attachment%2Fenergies%2Fenergies-14-02047%2Farticle_deploy%2Fenergies-14-02047.pdf
        #self.e_EC = 0
        self.e_EC *= 1000 #gCO2/kWh
        self.e_E = 0  # gCO2/kWh

        #self.e_GCw = 0
        #self.e_GCs = 0
        self.e_GCw = 520862 #g CO2/kWp from SESAME backend
        self.e_GCs = 7.23 * pow(10, 5) / 570 #gCO2/Wp from SESAME backend
        self.e_GCs *= 1000 #gCO2/kWp

        #normalizing by lifetime:
        self.e_EC /= self.Lec # g CO2 / kWh / yr
        self.e_CPC /= self.Lec
        self.e_DPC /= self.Lec
        self.e_E /= self.Lec
        self.e_GCs /= self.Ls # g CO2 / kWp / yr
        self.e_GCw /= self.Lw # g CO2 / kWp / yr

        self.e_ng = 567 #gCO2/kWh. source = sesame NG defaults. includes upstream methane leakage.
        self.e_nuclear = 8.4 #gCO2/kWh. source = sesame nuclear defaults (LWR). does not include plant construction and retirement

        eta_c = 0.92
        eta_d = 0.92

        #setting nuclear hourly output
        self.CF_nuclear = .927 #https://www.statista.com/statistics/191201/capacity-factor-of-nuclear-power-plants-in-the-us-since-1975/

        #these calculations are to see if the system classifies as "high dispatchables"
        Gs1 = self.f_solar * Gs_shape
        Gw1 = self.f_wind * Gw_shape
        Gnuclear1 = self.f_nuclear
        Gnondispatchable1 = Gs1 + Gw1 + Gnuclear1
        G_minus_D = Gnondispatchable1 - D_underlined
        G_minus_D[G_minus_D < 0] = 0
        Ge1y = G_minus_D.sum()

        #do this if you have a system of high-dispatchables
        #if self.f_ng > 1:
        if Ge1y == 0:# and self.optimize_shares == 'no':
            print('high dispatchable branch')
            D = D_underlined
            G_ng = (D - Gnondispatchable1) / (1 - self.TD_losses)
            GC_ng = G_ng.max()

            GC_wind = self.f_wind / CF_wind / (1 - self.TD_losses)
            GC_solar = self.f_solar / CF_solar / (1 - self.TD_losses)
            GC_nuclear = self.f_nuclear / self.CF_nuclear / (1 - self.TD_losses)

            capacity_and_FOM_costs = self.c_GCs * GC_solar + self.c_GCw * GC_wind + self.c_GC_ng * GC_ng + self.c_GCnuclear * GC_nuclear # $/year CAPEX and FOM are baked into this calcualtion
            VOM_costs = self.VOMng * G_ng.sum() + self.VOMnuclear * GC_nuclear * self.CF_nuclear * 8760 # $/year
            fuel_costs = self.ng_fuel_cost * self.ng_heat_rate * G_ng.sum() + self.nuclear_fuel_cost * self.nuclear_heat_rate * GC_nuclear * self.CF_nuclear * 8760 # $/year
            cost = capacity_and_FOM_costs + VOM_costs + fuel_costs # $/yr

            f_curt = 0
            f_DD = 1
            f_DVS = 0
            f_LIS = 0
            EC = 0
            DPC = 0
            CPC = 0
            E = 0
            G_demand = D
            G_storage = pd.DataFrame(np.zeros((8760, 1))).squeeze()
            G_curtailed = pd.DataFrame(np.zeros((8760, 1))).squeeze()
            G_SW_2_D = Gw1 + Gs1 #solar and wind to demand
            D_storage = pd.DataFrame(np.zeros((8760, 1))).squeeze()
            G_wind = Gw1
            G_solar = Gs1
            d = 0
            E_storage = pd.DataFrame(np.zeros((8760, 1))).squeeze()
            P_storage = pd.DataFrame(np.zeros((8760, 1))).squeeze()
            G = D
            G_minus_D = pd.DataFrame(np.zeros((8760, 1))).squeeze()
            G_nuclear = pd.DataFrame(np.ones((8760, 1))).squeeze() * self.CF_nuclear * self.f_nuclear

            renewable_total_b4_TD_losses = 8760 * (1 - self.f_ng) / (1 - self.TD_losses)

            # calculating gen flow normalized by demand
            G_2_curt_over_D = 0
            G_2_demand_over_D = self.D_total * (1 -self.TD_losses) / self.D_total
            G_2_TD_loss_over_D = self.D_total * self.TD_losses / self.D_total
            G_2_LIS_over_D = 0
            G_2_S_2_D_over_D = 0

            if renewable_total_b4_TD_losses == 0:
                # calculating renewable flow normalized by demand
                f_ren_curt = 0
                f_ren_demand = 0
                f_ren_LIS = 0
                f_ren_storage = 0
                f_ren_TD_loss = 0
            else:
                # calculating renewable flow normalized by demand
                f_ren_curt = 0
                f_ren_demand = renewable_total_b4_TD_losses * (1 - self.TD_losses) / self.D_total
                f_ren_LIS = 0
                f_ren_storage = 0
                f_ren_TD_loss = renewable_total_b4_TD_losses * self.TD_losses / self.D_total


            return (f_curt, f_DD, f_DVS, f_LIS, EC, DPC, CPC, GC_wind, GC_solar, GC_ng, GC_nuclear, cost, E, G_demand, G_storage, G_curtailed, G_SW_2_D, D_storage, G_wind, G_solar, G_nuclear, d, E_storage, P_storage, G, D, G_minus_D, G_ng, G_2_curt_over_D, G_2_demand_over_D, G_2_TD_loss_over_D, G_2_LIS_over_D, G_2_S_2_D_over_D, f_ren_curt, f_ren_demand, f_ren_LIS, f_ren_storage, f_ren_TD_loss)

        else:
            print('low dispatchable branch')
            #do this if you do not have a system of high disbatchables
            model = pe.ConcreteModel()

            hour = range(8760)
            model.hour = pe.Set(initialize=hour)

            model.D = dict(D_underlined)

            # setting all variables required for objective function
            model.GC_wind = pe.Var(domain=pe.NonNegativeReals)
            model.GC_solar = pe.Var(domain=pe.NonNegativeReals)
            model.CPC = pe.Var(domain=pe.NonNegativeReals)
            model.DPC = pe.Var(domain=pe.NonNegativeReals)
            model.EC = pe.Var(domain=pe.NonNegativeReals)
            model.total_energy_sent_to_storage = pe.Var(domain=pe.NonNegativeReals)
            model.G_total = pe.Var(domain=pe.NonNegativeReals)
            model.NG_total = pe.Var(domain = pe.NonNegativeReals)
            model.nuclear_total = pe.Var(domain = pe.NonNegativeReals)
            model.GC_ng = pe.Var(domain=pe.NonNegativeReals)
            model.GC_nuclear = pe.Var(domain=pe.NonNegativeReals)

            model.G_2_S = pe.Var(model.hour, domain=pe.NonNegativeReals)
            model.S_2_D = pe.Var(model.hour, domain=pe.NonNegativeReals)
            model.G_2_D = pe.Var(model.hour, domain=pe.NonNegativeReals)
            model.G_2_C = pe.Var(model.hour, domain=pe.NonNegativeReals)
            model.E_level = pe.Var(model.hour, domain=pe.NonNegativeReals)
            model.D_from_S = pe.Var(model.hour, domain=pe.NonNegativeReals)
            model.S_from_G = pe.Var(model.hour, domain=pe.NonNegativeReals)
            model.G = pe.Var(model.hour, domain=pe.NonNegativeReals)
            model.NG_output = pe.Var(model.hour, domain=pe.NonNegativeReals)
            model.nuclear_output = pe.Var(model.hour, domain = pe.NonNegativeReals)

            capacity_and_FOM_costs = self.c_GCs * model.GC_solar + self.c_GCw * model.GC_wind + self.c_GC_ng * model.GC_ng + self.c_GCnuclear * model.GC_nuclear
            VOM_costs = self.VOMng * model.NG_total + self.VOMnuclear * model.GC_nuclear * self.CF_nuclear * 8760
            fuel_costs = self.ng_fuel_cost * self.ng_heat_rate * model.NG_total + self.nuclear_fuel_cost * self.nuclear_heat_rate * model.nuclear_total
            battery_costs = self.c_EC * model.EC + self.c_E * model.total_energy_sent_to_storage
            emissions = (self.e_GCs * model.GC_solar + self.e_GCw * model.GC_wind + (self.e_EC * model.EC + self.e_CPC * model.CPC + self.e_DPC * model.DPC + self.e_E * model.total_energy_sent_to_storage) + self.e_ng * model.NG_total + self.e_nuclear * model.nuclear_total) * self.e_tax
            objective_function = capacity_and_FOM_costs + VOM_costs + fuel_costs + battery_costs + emissions
            model.cost = pe.Objective(sense=pe.minimize, expr=objective_function)

            # setting all variables required for constraints
            model.G_underlined = pe.Param(model.hour, domain=pe.NonNegativeReals)

            model.all_power_must_be_served = pe.ConstraintList()
            model.all_G_goes_somewhere = pe.ConstraintList()
            model.all_increase_in_E_lte_CPC = pe.ConstraintList()
            model.all_decrease_in_E_lte_DPC = pe.ConstraintList()
            model.finding_G = pe.ConstraintList()
            model.E_storage_limit = pe.ConstraintList()
            model.NG_output_constraint = pe.ConstraintList()
            model.nuclear_output_constraint = pe.ConstraintList()
            for hour_number in model.hour:
                model.all_power_must_be_served.add(model.G_2_D[hour_number] + model.S_2_D[hour_number] * eta_d == model.D[hour_number])
                model.all_G_goes_somewhere.add(model.G_2_D[hour_number] + model.G_2_S[hour_number] + model.G_2_C[hour_number] == model.G[hour_number])
                model.all_increase_in_E_lte_CPC.add(model.G_2_S[hour_number] <= model.CPC)
                model.all_decrease_in_E_lte_DPC.add(model.S_2_D[hour_number] * eta_d <= model.DPC)
                model.finding_G.add(model.G[hour_number] == (model.GC_solar * G_solar_perkW[hour_number] + model.GC_wind * G_wind_perkW[hour_number] + model.NG_output[hour_number] + model.nuclear_output[hour_number]) * (1 - self.TD_losses))
                model.E_storage_limit.add(model.E_level[hour_number] <= model.EC)
                model.NG_output_constraint.add(model.GC_ng >= model.NG_output[hour_number])
                model.nuclear_output_constraint.add(model.GC_nuclear * self.CF_nuclear == model.nuclear_output[hour_number])

            model.E_level_constraint = pe.ConstraintList()
            for hour_number in model.hour:
                if hour_number == 0:
                    continue
                model.E_level_constraint.add(model.E_level[hour_number] == model.E_level[hour_number - 1] * self.hourly_storage_efficiency + model.G_2_S[hour_number] * eta_c - model.S_2_D[hour_number])

            model.total_energy_sent_to_storage_constraint = pe.Constraint(expr = sum(model.G_2_S[i] for i in model.hour) == model.total_energy_sent_to_storage)
            model.matching_CPC_and_DPC = pe.Constraint(expr = model.CPC == model.DPC)
            model.setting_E_0_equal_to_E_last = pe.Constraint(expr = model.E_level[0] == model.E_level[8759])
            model.G_sum = pe.Constraint(expr = sum(model.G[i] for i in model.hour) == model.G_total)
            model.nuclear_sum = pe.Constraint(expr=sum(model.nuclear_output[i] for i in model.hour) == model.nuclear_total)
            model.NG_sum = pe.Constraint(expr = sum(model.NG_output[i] for i in model.hour) == model.NG_total)
            model.NG_fraction = pe.Constraint(expr = self.D_total - model.NG_total * (1 - self.TD_losses) == (1 - self.f_ng) * self.D_total)
            model.wind_fraction = pe.Constraint(expr = self.f_wind / (1 - self.f_ng) * (CF_wind * model.GC_wind + CF_solar * model.GC_solar + self.CF_nuclear * model.GC_nuclear) == CF_wind * model.GC_wind)
            model.solar_fraction = pe.Constraint(expr=self.f_solar / (1 - self.f_ng) * (CF_wind * model.GC_wind + CF_solar * model.GC_solar + self.CF_nuclear * model.GC_nuclear) == CF_solar * model.GC_solar)
            #model.solar_fraction = pe.Constraint(expr= 0 == model.GC_solar)
            #model.NG_fraction = pe.Constraint(expr=self.D_total - model.NG_total == 0)

            #model.CO2_cap = pe.Constraint(expr = (self.e_GCs * model.GC_solar + self.e_GCw * model.GC_wind + (self.e_EC * model.EC + self.e_CPC * model.CPC + self.e_DPC * model.DPC + self.e_E * model.total_energy_sent_to_storage) + self.e_ng * model.NG_total + self.e_nuclear * model.nuclear_total) <= 0 * self.D_total)

            model.battery_duration = pe.Constraint(expr = model.EC == model.CPC * 4)

            solver = po.SolverFactory('gurobi', solver_io='python')
            result = solver.solve(model)#, tee=True)

            #data post-processing
            G_2_S_df = pd.DataFrame.from_dict(model.G_2_S.extract_values(), orient='index', columns=[str(model.hour)]) / (1 - self.TD_losses)
            G_2_D_df = pd.DataFrame.from_dict(model.G_2_D.extract_values(), orient='index', columns=[str(model.hour)]) / (1 - self.TD_losses)
            G_2_C_df = pd.DataFrame.from_dict(model.G_2_C.extract_values(), orient='index', columns=[str(model.hour)]) / (1 - self.TD_losses)
            S_2_D_df = pd.DataFrame.from_dict(model.S_2_D.extract_values(), orient='index', columns=[str(model.hour)])
            D_from_S_df = S_2_D_df * eta_d

            G_df = pd.DataFrame.from_dict(model.G.extract_values(), orient='index', columns=[str(model.hour)]) / (1 - self.TD_losses)
            E_level_df = pd.DataFrame.from_dict(model.E_level.extract_values(), orient='index', columns=[str(model.hour)])

            D_df = D_underlined.to_frame()
            D_df.columns = ['hour']

            # calculating gen breakdown normalized by generation
            total_curtailed = G_2_C_df.sum()[0]
            total_G_2_S = G_2_S_df.sum()[0]
            total_D_from_S = D_from_S_df.sum()[0]
            total_LIS = total_G_2_S - total_D_from_S
            total_G_2_D = G_2_D_df.sum()[0]
            total_G = G_df.sum()[0]

            f_curt = total_curtailed / total_G
            f_DVS = total_D_from_S / total_G
            f_LIS = total_LIS / total_G
            f_DD = total_G_2_D / total_G

            G_solar_output = G_solar_perkW * pe.value(model.GC_solar)
            G_wind_output = G_wind_perkW * pe.value(model.GC_wind)

            G_solar_output_df = pd.DataFrame(G_solar_output)
            G_wind_output_df = pd.DataFrame(G_wind_output)
            G_nuclear_output_df = pd.DataFrame.from_dict(model.nuclear_output.extract_values(), orient='index', columns=[str(model.hour)])

            G_solar_output_df.columns = ['solar']
            G_wind_output_df.columns = ['wind']
            G_nuclear_output_df.columns = ['nuclear']

            NG_output_df = pd.DataFrame.from_dict(model.NG_output.extract_values(), orient='index', columns=[str(model.hour)])
            NG_output_df.columns = ['ng']
            renewable_G_2_D = D_df['hour'] - NG_output_df['ng'] * (1-self.TD_losses) - D_from_S_df['hour']
            renewable_G_2_D_total = renewable_G_2_D.sum()

            if pe.value(model.EC) == 0:
                d = 0
            else:
                d = pe.value(model.EC) / pe.value(model.DPC)

            # calculating gen tech breakdown normalized by demand
            NG_output_total = NG_output_df['ng'].sum()
            nuclear_output_total = G_nuclear_output_df['nuclear'].sum()
            solar_output_total = G_solar_output_df['solar'].sum()
            wind_output_total = G_wind_output_df['wind'].sum()

            gen_total_b4_TD_losses = NG_output_total + nuclear_output_total + solar_output_total + wind_output_total
            used_total_b4_TD_losses = gen_total_b4_TD_losses - total_curtailed
            renewable_total_b4_TD_losses = nuclear_output_total + solar_output_total + wind_output_total
            ren_used_total_b4_TD_losses = renewable_total_b4_TD_losses - total_curtailed

            # calculating gen flow normalized by demand
            G_2_curt_over_D = total_curtailed / self.D_total
            G_2_demand_over_D = total_G_2_D / self.D_total
            G_2_TD_loss_over_D = used_total_b4_TD_losses * self.TD_losses / self.D_total
            G_2_LIS_over_D = total_LIS / self.D_total
            G_2_S_2_D_over_D = total_D_from_S / self.D_total

            # calculating renewable flow normalized by demand
            f_ren_curt = total_curtailed / self.D_total
            f_ren_demand = renewable_G_2_D_total / self.D_total
            f_ren_LIS = total_LIS / self.D_total
            f_ren_storage = total_D_from_S / self.D_total
            f_ren_TD_loss = ren_used_total_b4_TD_losses * self.TD_losses / self.D_total

            return (f_curt, f_DD, f_DVS, f_LIS, pe.value(model.EC), pe.value(model.DPC), pe.value(model.CPC), pe.value(model.GC_wind), pe.value(model.GC_solar), pe.value(model.GC_ng), pe.value(model.GC_nuclear), pe.value(model.cost), pe.value(model.total_energy_sent_to_storage), G_2_D_df['hour'], G_2_S_df['hour'], G_2_C_df['hour'], renewable_G_2_D, D_from_S_df['hour'], G_wind_output_df['wind'], G_solar_output_df['solar'], G_nuclear_output_df['nuclear'], d, E_level_df['hour'], (G_2_S_df - D_from_S_df)['hour'], G_df['hour'], D_df['hour'], (G_df - D_df)['hour'], NG_output_df['ng'], G_2_curt_over_D, G_2_demand_over_D, G_2_TD_loss_over_D, G_2_LIS_over_D, G_2_S_2_D_over_D, f_ren_curt, f_ren_demand, f_ren_LIS, f_ren_storage, f_ren_TD_loss)

    def get_output_values(self):
        f_curt, f_DD, f_DVS, f_LIS, EC, DPC, CPC, GC_wind, GC_solar, GC_ng, GC_nuclear, cost, E, G_demand, G_storage, G_curtailed, G_SW_2_D, D_storage, G_wind, G_solar, G_nuclear, d, E_storage, P_storage, G, D, G_minus_D, G_ng, G_2_curt_over_D, G_2_demand_over_D, G_2_TD_loss_over_D, G_2_LIS_over_D, G_2_S_2_D_over_D, f_ren_curt, f_ren_demand, f_ren_LIS, f_ren_storage, f_ren_TD_loss = self.do_optimization()

        NG_total = G_ng.sum()
        nuclear_total = G_nuclear.sum()
        solar_total = G_solar.sum()
        wind_total = G_wind.sum()

        self.f_ng = NG_total / self.D_total
        nondispatchable_total_generation = nuclear_total + wind_total + solar_total
        nondispatchable_total_demand = self.D_total - NG_total

        if self.f_ng >= 1:
            self.f_wind = 0
            self.f_solar = 0
            self.f_nuclear = 0
        else:
            self.f_wind = wind_total / nondispatchable_total_generation * (1 - self.f_ng)
            self.f_solar = solar_total / nondispatchable_total_generation * (1 - self.f_ng)
            self.f_nuclear = nuclear_total / nondispatchable_total_generation * (1 - self.f_ng)

        # placeholder data:
        delivery_cost = 47/1000 #$/kWh
        #delivery_cost = 0
        tax = 1.0635 #multiplier
        #tax = 1

        #emissions calculations
        emissions_solar = self.e_GCs * GC_solar
        emissions_wind = self.e_GCw * GC_wind
        emissions_battery = (self.e_EC * EC + self.e_CPC * CPC + self.e_DPC * DPC + self.e_E * E)
        emissions_ng = self.e_ng * G_ng.sum() #emissions are only for operation, not construction
        emissions_nuclear = self.e_nuclear * G_nuclear.sum() #emissions are only for operation, not construction
        yearly_emissions_total = emissions_solar + emissions_wind + emissions_battery + emissions_ng + emissions_nuclear

        emissions_intensity = yearly_emissions_total / 8760 # gCO2/kWh

        #LCOE cost calculations
        LCOE_before_tax = cost / 8760  # $/kWh
        LCOE = (LCOE_before_tax + delivery_cost) * tax  # $/kWh
        LCOE = LCOE * 1000  # $/MWh

        # breaking into the tech parts of the objective function
        solar_cost = self.c_GCs * GC_solar
        wind_cost = self.c_GCw * GC_wind
        transmission_costs = self.c_CPC * CPC + self.c_DPC * DPC
        battery_costs = (self.c_EC * EC + self.c_E * E) + transmission_costs
        ng_costs = self.c_GC_ng * GC_ng + self.VOMng * NG_total + self.ng_fuel_cost * self.ng_heat_rate * NG_total
        nuclear_costs = self.c_GCnuclear * GC_nuclear + self.VOMnuclear * nuclear_total + self.nuclear_fuel_cost * self.nuclear_heat_rate * nuclear_total
        total_cost_before_postprocessing = solar_cost + wind_cost + battery_costs + ng_costs + nuclear_costs

        #print('nuclear cost check ($/year/kW)= ' + str((self.OCCnuclear / self.Lnuclear + self.FOMnuclear) + (self.VOMnuclear + self.nuclear_heat_rate * self.nuclear_fuel_cost)*8760*self.CF_nuclear))
        #print('nuclear cost check 2 ($/year/kW)= ' + str(nuclear_costs/ GC_nuclear))

        #print('solar cost = ' + str(solar_cost))
        #print('wind cost = ' + str(wind_cost))
        #print('nuclear cost = ' + str(nuclear_costs))
        #print('ng cost = ' + str(ng_costs))
        #print('battery cost = ' + str(battery_costs))

        solar_LCOE_cost = (solar_cost / 8760 + delivery_cost * solar_cost / total_cost_before_postprocessing) * 1000 * tax + emissions_solar * self.e_tax / 8760 * 1000
        wind_LCOE_cost = (wind_cost / 8760 + delivery_cost * wind_cost / total_cost_before_postprocessing) * 1000 * tax + emissions_wind * self.e_tax / 8760 * 1000
        battery_LCOE_cost = (battery_costs / 8760 + delivery_cost * battery_costs / total_cost_before_postprocessing) * 1000 * tax + emissions_battery * self.e_tax / 8760 * 1000
        ng_LCOE_cost = (ng_costs / 8760 + delivery_cost * ng_costs / total_cost_before_postprocessing) * 1000 * tax + emissions_ng * self.e_tax / 8760 * 1000
        nuclear_LCOE_cost = (nuclear_costs / 8760 + delivery_cost * nuclear_costs / total_cost_before_postprocessing) * 1000 * tax + emissions_nuclear * self.e_tax / 8760 * 1000

        # breaking objective function into categories
        OCC_wind_segment = self.OCCw / self.Lw * GC_wind
        OCC_solar_segment = self.OCCs / self.Ls * GC_solar
        OCC_battery_segment = EC * self.OCC_EC / self.Lec + transmission_costs
        OCC_ng_segment = GC_ng * self.OCCng / self.Lng
        OCC_nuclear_segment = GC_nuclear * self.OCCnuclear / self.Lnuclear
        FOM_battery_segment = self.FOMstorage * EC
        FOM_solar_segment = self.FOMs * GC_solar
        FOM_wind_segment = self.FOMw * GC_wind
        FOM_ng_segment = self.FOMng * GC_ng
        FOM_nuclear_segment = self.FOMnuclear * GC_nuclear
        VOM_battery_segment = self.c_E * E
        VOM_ng_segment = self.VOMng * NG_total
        VOM_nuclear_segment = self.VOMnuclear * nuclear_total
        fuel_ng_segment = self.ng_fuel_cost * self.ng_heat_rate * NG_total
        fuel_nuclear_segment = self.nuclear_fuel_cost * self.nuclear_heat_rate * nuclear_total

        # breaking objective function into categories
        OCC_segment = (OCC_wind_segment + OCC_solar_segment + OCC_battery_segment + OCC_ng_segment + OCC_nuclear_segment ) / 8760 * 1000
        FOM_segment = (FOM_battery_segment + FOM_solar_segment + FOM_wind_segment + FOM_ng_segment + FOM_nuclear_segment) / 8760 * 1000
        VOM_segment = (VOM_battery_segment + VOM_nuclear_segment + VOM_ng_segment) / 8760 * 1000
        fuel_segment = (fuel_nuclear_segment + fuel_ng_segment) / 8760 * 1000
        delivery_segment = delivery_cost * 1000
        emissions_tax_segment = yearly_emissions_total * self.e_tax / 8760 * 1000
        tax_segment = (OCC_segment + FOM_segment + delivery_segment + VOM_segment + fuel_segment) * (tax - 1) + emissions_tax_segment


        #generation from normalized by demand
        NG_gen_over_D = NG_total/self.D_total
        nuclear_gen_over_D = nuclear_total/self.D_total
        solar_gen_over_D = solar_total/self.D_total
        wind_gen_over_D = wind_total/self.D_total

        return {
            'f_curtail': f_curt,
            'f_DD': f_DD,
            'f_DVS': f_DVS,
            'f_LIS': f_LIS,
            'EC': EC,
            'DPC': DPC,
            'CPC': CPC,
            'GCsolar': GC_solar,
            'GCwind': GC_wind,
            'GCnuclear': GC_nuclear,
            'GCd': GC_ng,
            'cost': cost,
            'E': E,
            'G_demand': G_demand,
            'G_storage': G_storage,
            'G_curtailed': G_curtailed,
            'G_SW_2_D': G_SW_2_D,
            'D_storage': D_storage,
            'G_wind': G_wind,
            'G_solar': G_solar,
            'd': d,
            'E_storage': E_storage,
            'P_storage': P_storage,
            'G': G,
            'D': D,
            'G_minus_D': G_minus_D,
            'G_ng': G_ng,
            'G_nuclear': G_nuclear,
            'emissions_solar': emissions_solar / 8760,
            'emissions_wind': emissions_wind / 8760,
            'emissions_battery': emissions_battery / 8760,
            'emissions_ng': emissions_ng / 8760,
            'emissions_nuclear': emissions_nuclear / 8760,
            'LCOE': LCOE,
            'CAPEX': OCC_segment,
            'FOM': FOM_segment,
            'VOM': VOM_segment,
            'fuel': fuel_segment,
            'tax': tax_segment,
            'delivery': delivery_segment,
            #'carbon tax': emissions_tax_segment,
            'solar cost': solar_LCOE_cost,
            'wind cost': wind_LCOE_cost,
            'battery cost': battery_LCOE_cost,
            'ng cost': ng_LCOE_cost,
            'nuclear cost': nuclear_LCOE_cost,
            'NG_gen_over_D': NG_gen_over_D,
            'nuclear_gen_over_D': nuclear_gen_over_D,
            'solar_gen_over_D': solar_gen_over_D,
            'wind_gen_over_D': wind_gen_over_D,
            'G_2_curt_over_D': G_2_curt_over_D,
            'G_2_demand_over_D': G_2_demand_over_D,
            'G_2_TD_loss_over_D': G_2_TD_loss_over_D,
            'G_2_LIS_over_D': G_2_LIS_over_D,
            'G_2_S_2_D_over_D': G_2_S_2_D_over_D,
            'f_ren_curt': f_ren_curt,
            'f_ren_demand': f_ren_demand,
            'f_ren_LIS': f_ren_LIS,
            'f_ren_storage': f_ren_storage,
            'f_ren_TD_loss': f_ren_TD_loss
        }

    def plot(self, results):

        x_start = 1000
        x_end = 1100
        plt.stackplot(
            range(x_start, x_end),
            np.array(results['G_demand'][x_start:x_end], dtype = float),
            np.array(results['G_storage'][x_start:x_end], dtype = float),
            np.array(results['G_curtailed'][x_start:x_end], dtype = float),
            labels = ['Demand', 'Storage', 'Curtailment'],
        )
        plt.plot(range(x_start, x_end), results['G'][x_start:x_end], color='black', linestyle='dashed', linewidth=2)
        plt.legend(loc = 'upper left')
        plt.title('Generation to (Gurobi version)')
        plt.xlim(x_start, x_end)
        #plt.ylim(8, 12)
        plt.show()

        plt.stackplot(
            range(x_start, x_end),
            np.array(results['G_nuclear'][x_start:x_end], dtype=float),
            np.array(results['G_wind'][x_start:x_end], dtype = float),
            np.array(results['G_solar'][x_start:x_end], dtype = float),
            np.array(results['G_ng'][x_start:x_end], dtype = float),
            labels = ['nuclear', 'wind', 'Solar', 'ng'],
        )
        plt.plot(range(x_start, x_end), results['G'][x_start:x_end], color='black', linestyle='dashed', linewidth=2)
        plt.legend(loc = 'upper left')
        plt.title('Generation from (Gurobi version)')
        plt.xlim(x_start, x_end)
        #plt.ylim(8, 12)
        plt.show()

        """
        plt.stackplot(
            range(x_start, x_end),
            np.array(results['G_demand'][x_start:x_end], dtype = float),
            np.array(results['D_storage'][x_start:x_end], dtype = float),
            labels = ['Generation', 'Storage'],
        )
        plt.legend(loc = 'upper left')
        plt.title('Demand from (Gurobi version))')
        plt.show()

        #emissions breakdown
        x = ['emissions breakdown (g/kWh)']
        y1 = np.array([results['emissions_solar']])
        y2 = np.array([results['emissions_wind']])
        y3 = np.array([results['emissions_battery']])
        y4 = np.array([results['emissions_ng']])
        y5 = np.array([results['emissions_nuclear']])
        plt.bar(x, y1, color='y', label = 'solar')
        plt.bar(x, y2, bottom=y1, color='b', label = 'wind')
        plt.bar(x, y3, bottom=y1+y2, color='purple', label = 'battery')
        plt.bar(x, y4, bottom=y3 + y2 + y1, color='grey', label = 'natural gas')
        plt.bar(x, y5, bottom=y4 + y3 + y2 + y1, color='pink', label = 'nuclear')
        plt.legend(fontsize = 20)
        plt.xticks(fontsize = 20)
        plt.yticks(fontsize = 20)
        #plt.ylim(0, 560)
        plt.show()

        cost_plot_max = 95
        #cost breakdown by tech
        x = ['tech cost breakdown']
        y1 = np.array([results['solar cost']])
        y2 = np.array([results['wind cost']])
        y3 = np.array([results['battery cost']])
        y4 = np.array([results['ng cost']])
        y5 = np.array([results['nuclear cost']])
        plt.bar(x, y1, color='y', label = 'solar')
        plt.bar(x, y2, bottom=y1, color='b', label = 'wind')
        plt.bar(x, y3, bottom=y1+y2, color='purple', label = 'battery')
        plt.bar(x, y4, bottom=y3 + y2 + y1, color='grey', label = 'natural gas')
        plt.bar(x, y5, bottom=y4 + y3 + y2 + y1, color='pink', label = 'nuclear')
        plt.legend(fontsize = 20)
        plt.xticks(fontsize = 20)
        plt.yticks(fontsize = 20)
        #plt.ylim(0, cost_plot_max)
        plt.show()
        print('tech total = ' + str(results['solar cost'] + results['wind cost'] + results['battery cost'] + results['ng cost'] + results['nuclear cost']))


        #cost breakdown by category
        x = ['categorical cost breakdown']
        y1 = np.array([results['CAPEX']])
        y2 = np.array([results['FOM']])
        y3 = np.array([results['VOM']])
        y4 = np.array([results['fuel']])
        y5 = np.array([results['delivery']])
        y6 = np.array([results['tax']])
        #y7 = np.array([results['carbon tax']])
        plt.bar(x, y1, label = 'CAPEX')
        plt.bar(x, y2, bottom=y1, label = 'FOM')
        plt.bar(x, y3, bottom=y1+y2, label = 'VOM')
        plt.bar(x, y4, bottom=y3 + y2 + y1, label = 'fuel')
        plt.bar(x, y5, bottom=y4 + y3 + y2 + y1, label = 'delivery')
        plt.bar(x, y6, bottom=y4 + y5 + y3 + y2 + y1, label = 'tax')
        #plt.bar(x, y7, bottom=y6 + y4 + y5 + y3 + y2 + y1, label = 'carbon tax')
        plt.legend(fontsize = 20)
        plt.xticks(fontsize = 20)
        plt.yticks(fontsize = 20)
        #plt.ylim(0, cost_plot_max)
        plt.show()
        print('type total = ' + str(results['CAPEX'] + results['FOM'] + results['VOM'] + results['fuel'] + results['delivery'] + results['tax']))

        #generation breakdown by flow
        x = ['renewable generation flow']
        y1 = np.array([results['f_ren_curt']])
        y2 = np.array([results['f_ren_demand']])
        y3 = np.array([results['f_ren_LIS']])
        y4 = np.array([results['f_ren_storage']])
        y5 = np.array([results['f_ren_TD_loss']])

        plt.bar(x, y1, label='f_ren_curt')
        plt.bar(x, y2, bottom=y1, label='f_ren_demand')
        plt.bar(x, y3, bottom=y1 + y2, label='f_ren_LIS')
        plt.bar(x, y4, bottom=y3 + y2 + y1, label='f_ren_storage')
        plt.bar(x, y5, bottom=y3 + y2 + y1, label='f_ren_TD_loss')
        plt.legend(fontsize=20)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        # plt.ylim(0, cost_plot_max)
        plt.show()


        #generation breakdown by tech
        x = ['generation breakdown by tech']
        y1 = np.array([results['NG_gen_over_D']])
        y2 = np.array([results['nuclear_gen_over_D']])
        y3 = np.array([results['solar_gen_over_D']])
        y4 = np.array([results['wind_gen_over_D']])

        plt.bar(x, y1, color='grey', label = 'ng generation')
        plt.bar(x, y2, color='pink', bottom=y1, label = 'nuclear generation')
        plt.bar(x, y3, color='y', bottom=y1+y2, label = 'solar generation')
        plt.bar(x, y4, color='b', bottom=y3 + y2 + y1, label = 'wind generation')
        plt.legend(fontsize = 20)
        plt.xticks(fontsize = 20)
        plt.yticks(fontsize = 20)
        #plt.ylim(0, cost_plot_max)
        plt.show()

        #generation breakdown by flow
        x = ['categorical cost breakdown']
        y1 = np.array([results['G_2_curt_over_D']])
        y2 = np.array([results['G_2_demand_over_D']])
        y3 = np.array([results['G_2_TD_loss_over_D']])
        y4 = np.array([results['G_2_LIS_over_D']])
        y5 = np.array([results['G_2_S_2_D_over_D']])

        plt.bar(x, y1, label = 'Generation curtailed')
        plt.bar(x, y2, bottom=y1, label = 'Generation to demand')
        plt.bar(x, y3, bottom=y1+y2, label = 'Generation lost through T and D')
        plt.bar(x, y4, bottom=y3 + y2 + y1, label = 'Generation lost in storage')
        plt.bar(x, y5, bottom=y4 + y3 + y2 + y1, label = 'Generation through storage')
        plt.legend(fontsize = 20)
        plt.xticks(fontsize = 20)
        plt.yticks(fontsize = 20)
        #plt.ylim(0, cost_plot_max)
        plt.show()

        #print capacity values
        print('EC = ' + str(results['EC']))
        print('CPC = ' + str(results['CPC']))
        print('GCw = ' + str(results['GCwind']))
        print('GCs = ' + str(results['GCsolar']))
        print('GCng = ' + str(results['GCd']))
        print('GCnuclear = ' + str(results['GCnuclear']))
        print('LCOE = ' + str(results['LCOE']))
        """


# run with:
#   python -m analysis.system.pps.power_plus_storage
if __name__ == '__main__':
    pps = PPS.instantiate({
        #'optimize_shares': 'yes',
        'demand': json.dumps([40, 40, 10, 10]), # solar, wind, nuclear, ng
        'region': 'Texas',
        'storage_type': 'lithium ion battery',
        'year': '2013',
        'D_year': '2013',
        'd_cG': '0',
        'd_cS': '0',
        'M': '5',
        'area_width': '240',
        'sites': '4',
        #'cap': 'no',
        #'ecap': '5',
        'e_tax': '50'

    })

    start_time = time.time()
    results = pps.run()
    end_time = time.time()
    pps.plot(results)
