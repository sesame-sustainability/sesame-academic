import os
import json
import os
import pandas as pd
from core.pathway import Step, Pathway
from core.utils import yes_no
import analysis.lca as lca_analysis
import argparse
import numpy as np
import math
import matplotlib.pyplot as plt

# make sure the topology registries are loaded
import pathway.topology

from core import validators, conditionals
from core.common import InputSource, Versioned
from core.inputs import ContinuousInput, OptionsInput, Default, InputSet, Option, InputGroup, ShareTableInput, Tooltip

PATH = os.getcwd() + '/analysis/system/grid/'

DEFAULT_DATA = D_table = pd.read_csv(PATH + 'Defaults.csv', index_col=['year'])

power_sources = ['Coal', 'Natural gas', 'Solar', 'Wind', 'Nuclear', 'Hydro', 'Other']
regions = ['US, California', 'US, Florida', 'US, New York', 'US, Northeast', 'US, Texas']

def percentage(val, f=None):
    if f is None:
        f = lambda x: x
    if np.isnan(val):
        return 0
    else:
        return f(val * 100)

def generation_share_defaults(power_source, year):
    region_keys = {
        'US, California': 'US_CA',
        'US, New York': 'US_NY',
        'US, Texas': 'US_TX',
        'US, Northeast': 'US_NPCC',
        'US, Florida': 'US_FL',
    }

    def column_name(region, power_source, pgm):
        return f'{power_source}_{region_keys[region]}_{pgm}'

    def default_value(region, power_source, pgm):
        return int(percentage(DEFAULT_DATA[column_name(power_source, region, pgm)][year], f=round))

    return [
        Default(
            default_value(power_source, region, pgm),
            conditionals=[
                conditionals.input_equal_to('region', region),
                conditionals.input_equal_to('PGM', pgm),
            ],
        )
        for region in regions
        for pgm in ['AEO20']
        if column_name(region, power_source, pgm) in DEFAULT_DATA.columns
    ]

class Grid(InputSource, Versioned):
    version = 1

    @classmethod
    def user_inputs(cls, fleet = False):
        if fleet:
            return [
                OptionsInput(
                    'evmethod', 'Method to determine shape of EV power demand ',
                    options=['Direct input', 'Determine by charger access & power pricing', 'Flatten demand', 'Minimize storage, then flatten demand', 'Minimize storage, then flatten dispatchable generation'],
                    defaults=[Default('Direct input')],
                    conditionals=[conditionals.input_equal_to('fgi', 'No')],
                ),
                ContinuousInput(
                    'O',
                    '% of charging in overnight (12am-8am) ',
                    validators=[validators.integer(), validators.gte(0), validators.lte(100)],
                    conditionals=[conditionals.input_equal_to('evmethod', 'Direct input')],
                    defaults=[Default(20)],
                ),
                ContinuousInput(
                    'D',
                    '% of charging in day (8am-4pm) ',
                    validators=[validators.integer(), validators.gte(0), validators.lte(100)],
                    conditionals=[conditionals.input_equal_to('evmethod', 'Direct input')],
                    defaults=[Default(30)],
                ),
                # ContinuousInput(
                #     'E',
                #     '% of charging in evening (4pm-12am) ',
                #     validators=[validators.integer(), validators.gte(0), validators.lte(100)],
                #     conditionals=[conditionals.input_equal_to('evmethod', 'Direct Input')],
                # ),
                ContinuousInput(
                    'fhw',
                    '% of EVs w/ charger access at home & work',
                    validators=[validators.integer(), validators.gte(0), validators.lte(100)],
                    conditionals=[
                        conditionals.input_equal_to('evmethod', 'Determine by charger access & power pricing'),
                    ],
                    defaults=[Default(10)],
                ),
                ContinuousInput(
                    'fh',
                    '% of EVs w/ charger access at home only',
                    validators=[validators.integer(), validators.gte(0), validators.lte(100)],
                    conditionals=[
                        conditionals.input_equal_to('evmethod', 'Determine by charger access & power pricing'),
                    ],
                    defaults=[Default(80)],
                ),
                ContinuousInput(
                    'fw',
                    '% of EVs w/ charger access at work only',
                    validators=[validators.integer(), validators.gte(0), validators.lte(100)],
                    conditionals=[
                        conditionals.input_equal_to('evmethod', 'Determine by charger access & power pricing')],
                    defaults=[Default(10)],
                ),
                ContinuousInput(
                    'Hd',
                    '% of home-charged EVs with overnight power discounts ',
                    validators=[validators.integer(), validators.gte(0), validators.lte(100)],
                    conditionals=[
                        conditionals.input_equal_to('evmethod', 'Determine by charger access & power pricing')],
                    defaults=[Default(0)],
                ),
                ContinuousInput(
                    'ap_gas', 'Longterm marginal power mix, % gas(remainder=50:50::solar: wind)',
                    validators=[validators.integer(), validators.gte(0), validators.lte(100)],
                    conditionals=[conditionals.input_equal_to('fgi', 'No')],
                    defaults=[Default(30)],
                ),

            ]
        else:
            return [
                OptionsInput(
                    'region', 'Region ',
                    options=regions,
                    defaults=[Default(regions[0])],
                ),
                InputGroup('demand_general', 'Demand, General', children=[
                    OptionsInput(
                        'PBD', 'Projection for: Power Demand (non-EV) ',
                        options=['AEO20', 'User'],
                        defaults=[Default('AEO20')],
                    ),
                    ContinuousInput(
                        'delta_DnEV_P',
                        '% Change in Power Demand Per Person (non-EV), 2019-50 ',
                        conditionals=[conditionals.input_equal_to('PBD', 'User')],
                        defaults=[Default(10)],
                    ),
                ]),
                InputGroup('supply', 'Supply', children=[
                    OptionsInput(
                        'PGM', 'Projection for: Generation Mix ',
                        options=['AEO20', 'User'],
                        defaults=[Default('AEO20')],
                    ),
                    ShareTableInput(
                        'generation_shares', 'Generation Shares (%)',
                        columns=['2019', '2050'],
                        rows=[
                            ShareTableInput.Row(
                                power_source,
                                cells=[
                                    ShareTableInput.Cell(
                                        defaults=generation_share_defaults(power_source, 2019),
                                    ),
                                    ShareTableInput.Cell(
                                        defaults=generation_share_defaults(power_source, 2050),
                                    ),
                                ]
                            )
                            for power_source in power_sources
                        ],
                        on_change_actions=[
                            {
                                'type': 'set_input_to',
                                'target': 'PGM',
                                'value': 'User',
                            }
                        ],
                    ),
                    OptionsInput(
                        'PGM_speed', 'Speed of Generation Mix Change ',
                        options=['Slow', 'Medium', 'Fast'],
                        conditionals=[conditionals.input_equal_to('PGM', 'User')],
                        defaults=[Default('Medium')],
                    ),
                ]),
                InputGroup('demand_evs', 'Demand, EVs', children=[
                    OptionsInput(
                        'DEVf_D0', 'EV power demand in 2050, as % of demand today ',
                        options=[1, 10, 20, 30, 40, 50],  # can make numbers, as as well as default
                        defaults=[Default(20)],
                    ),
                    OptionsInput(
                        'evmethod', 'Method for shape of EV power demand ',
                        options=['Direct input', 'Determine by charger access & power pricing', 'Flatten demand', 'Minimize storage, then flatten demand', 'Minimize storage, then flatten dispatchable generation'],
                        defaults=[Default('Direct input')],
                    ),

                #### NEW OPTION FOR GRID OPTIMIZER (will be a drop down on front end)
                    #OptionsInput(
                    #    'D_EV_objective', 'Method for shape of EV power demand ',
                    #    options=['Flatten demand', 'Minimize storage, then flatten demand', 'Minimize storage, then flatten dispatchable generation'],
                    #    conditionals=[conditionals.input_equal_to('evmethod', 'Optimize')],
                    #    defaults=[Default('Minimize Storage')],
                    #),
                    ####

                ContinuousInput(
                    'O',
                    '% Charging Overnight (12am-8am) ',
                    validators=[validators.integer(), validators.gte(0), validators.lte(100)],
                    conditionals=[conditionals.input_equal_to('evmethod', 'Direct input')],
                    defaults=[Default(20)],
                ),
                    ContinuousInput(
                        'D',
                        '% Charging Midday (8am-4pm) ',
                        validators=[validators.integer(), validators.gte(0), validators.lte(100)],
                        conditionals=[conditionals.input_equal_to('evmethod', 'Direct input')],
                        defaults=[Default(30)],
                    ),
                    # ContinuousInput(
                    #     'E',
                    #     '% of charging in evening (4pm-12am) ',
                    #     validators=[validators.integer(), validators.gte(0), validators.lte(100)],
                    #     conditionals=[conditionals.input_equal_to('evmethod', 'Direct input')],
                    # ),
                ContinuousInput(
                    'fhw',
                    '% of EVs w/ charger access at home & work ',
                    validators=[validators.integer(), validators.gte(0), validators.lte(100)],
                    conditionals=[conditionals.input_equal_to('evmethod', 'Determine by charger access & power pricing')],
                    defaults=[Default(10)],
                ),
                    ContinuousInput(
                        'fh',
                        '% of EVs w/ charger access at home only ',
                        validators=[validators.integer(), validators.gte(0), validators.lte(100)],
                        conditionals=[conditionals.input_equal_to('evmethod', 'Determine by charger access & power pricing')],
                        defaults=[Default(80)],
                    ),
                    ContinuousInput(
                        'fw',
                        '% of EVs w/ charger access at work only ',
                        validators=[validators.integer(), validators.gte(0), validators.lte(100)],
                        conditionals=[conditionals.input_equal_to('evmethod', 'Determine by charger access & power pricing')],
                        defaults=[Default(10)],
                    ),
                    ContinuousInput(
                        'Hd',
                        '% of home chargers with Power discounts overnight ',
                        validators=[validators.integer(), validators.gte(0), validators.lte(100)],
                        conditionals=[conditionals.input_equal_to('evmethod', 'Determine by charger access & power pricing')],
                        defaults=[Default(0)],
                    ),
                ]),
            ]

    def __init__(self):
        self.smokestack_data = pd.read_csv(PATH + 'intensity_proj.csv', index_col = ['year'])
        self.cp = pd.read_csv(PATH + 'charging_profiles.csv', index_col = ['hour'])
        self.cp_parameters = pd.read_csv(PATH + 'cp_parameters.csv', index_col=['name'])
        self.powertypes = ["Coal", "Natural gas", "Solar", "Wind", "Nuclear", "Hydro"]
        self.lca_defaults = pd.DataFrame(0, index=self.powertypes, columns=['S', 'F', 'P_S'])
        # self.lca_defaults = pd.read_csv(PATH + 'lca_defaults.csv', index_col = ['Source'])

    def prepare(self, input_set, fleet=False):
        super().prepare(input_set)

        if fleet:
            self.Sps = "AEO20"
            self.PGM = "AEO20"
            self.F_Pps = "Proportional to general energy emission intensity"
            self.delta_F_P = 0
            self.f_country = 0.5
            self.initial_year = 2020
            self.final_year = 2050
            self.PBGM = "AEO20"
            self.PBD = "AEO20"
            if self.evmethod == "Direct input":
                self.E = 100 - self.O - self.D
            self.ap_gas = self.ap_gas/100
            self.ap_coal = self.ap_hydro = self.ap_other= self.ap_nuc = 0
            self.ap_solar = self.ap_wind = (1 - self.ap_gas)/2

            self.model = "fleet"
        else:
            self.Sps = "AEO20"
            self.F_Pps = "Proportional to general energy emission intensity"
            self.delta_F_P = 0
            self.f_country = 0.5
            self.initial_year = 2020
            self.final_year = 2050
            regions_abbr = ['US_CA','US_FL','US_NY','US_NPCC','US_TX']
            self.region = regions_abbr[regions.index(self.region)]
            if self.evmethod == "Direct input":
                self.E = 100 - self.O - self.D
            self.model = "power"
            self.DEVf_D0 = int(self.DEVf_D0)
            if self.PGM == 'User':
                shares_dict = {}
                shares_array = self.generation_shares[str(self.final_year)]
                if shares_array is not None:
                    for i in range(len(shares_array)):
                        shares_dict[power_sources[i]] = shares_array[i]
                    self.yf_PGM = shares_dict

    def run(self):
        return self.power_grid_integrator()

    def run_lca_module(self, source, powerplant = False):
        generation_regions = {
            'US_CA': 'WECC',
            'US_FL': 'FRCC',
            'US_NY': 'NPCC',
            'US_NPCC': 'NPCC',
            'US_TX': 'TRE',
        }

        if source == 'Coal':
            pathway = Pathway.build([
                'enduse-electricity-default',
                'gatetoenduse-transmission-literaturereview',
                ('process-coalpowerproduction-greet', {
                    'infrastructure_emission_inclusion': yes_no(powerplant),
                    'generation_region': generation_regions[self.region],
                }),
                'midstream-coaltransportation-greet',
                'upstream-coal-greet',
            ])
        elif source == 'Natural gas':
            pathway = Pathway.build([
                'enduse-electricity-default',
                'gatetoenduse-transmission-literaturereview',
                ('process-ngpowerproduction-greet', {
                    'infrastructure_emission_inclusion': yes_no(powerplant),
                    'generation_region': generation_regions[self.region],
                }),
                'midstream-ngelectricitytransportation-greet',
                'upstream-naturalgas-greet',
            ])
        elif source == 'Hydro':
            pathway = Pathway.build([
                'enduse-electricity-default',
                'gatetoenduse-transmission-literaturereview',
                ('process-hydropowerproduction-greet', {
                    'generation_region': generation_regions[self.region],
                }),
                'upstream-hydropower-default',
            ])
        elif source == 'Solar':
            locations = {
                'US_CA': 'US W (San Francisco)',
                'US_FL': 'US SE (Miami)',
                'US_NY': 'US NE (Boston)',
                'US_NPCC': 'US NE (Boston)',
                'US_TX': 'US SE (Miami)',
            }

            pathway = Pathway.build([
                'enduse-electricity-default',
                'gatetoenduse-transmission-literaturereview',
                ('process-solarpowerproduction-default', {
                    'location': locations[self.region],
                }),
                'upstream-solar-default',
            ])
        elif source == 'Wind':
            pathway = Pathway.build([
                'enduse-electricity-default',
                'gatetoenduse-transmission-literaturereview',
                'process-windpowerproduction-default',
                'upstream-wind-default',
            ])
        else:
            raise Exception(f'grid: no LCA pathway defined for source: {source}')

        data = lca_analysis.run([pathway])
        data['data'] = data['data'].groupby(['pathway', 'stage']).agg({'value': 'sum'}).reset_index()
        return data['data']

    def get_base_values(self):
        for source in self.powertypes:
            if source == "Coal" or source == "Natural gas":
                data = self.run_lca_module(source)
                data2 = self.run_lca_module(source, powerplant = True)
                self.lca_defaults.loc[source,'S'] = data[data.stage == "Process"][["value"]].values[0][0]
                self.lca_defaults.loc[source, 'F'] = data[data.stage == "Upstream"][["value"]].values[0][0] + data[data.stage == "Midstream"][["value"]].values[0][0]
                self.lca_defaults.loc[source, 'P_S'] = data2[data2.stage == "Process"][["value"]].values[0][0]
            elif source == "Nuclear":
                self.lca_defaults.loc[source,'F'] =  8.32
                self.lca_defaults.loc[source, 'P_S'] = 0.8
            else:
                data = self.run_lca_module(source)
                self.lca_defaults.loc[source, 'P_S'] = data[data.stage == "Upstream"][["value"]].values[0][0]

    def projection(self, base, projection_var, projection_col, delta, y0 = 2019, yf = 2050, flag = False):
        years = self.smokestack_data.loc[self.initial_year:self.final_year].index
        projected_data = pd.DataFrame(index=years, columns=[projection_col])
        if projection_var =='Static':
            projected_data.loc[years, projection_col] = base
        elif projection_var != "User":
            projected_data.loc[years, projection_col] = base * self.smokestack_data.loc[years, projection_col]
        else:
            projected_data.loc[years, projection_col] = base * (
                    1 + delta/100 * (years.values - y0) / (yf - y0))

        return projected_data

    def smokestack_em(self, source):
        if source == "Coal" or source == "Natural gas":
            projection_col ="(S/S_19)_" + source.lower() + "_" + "US" + "_" + self.Sps
            base = self.lca_defaults.loc[source, 'S']
            smoke = self.projection(base, self.Sps, projection_col, delta = 0)
        else:
            years = self.smokestack_data.loc[self.initial_year:self.final_year].index
            smoke = pd.DataFrame(0, index = years, columns = ['S_' + source])
        return smoke

    def general_energy_emission_intensity(self, f_coal, f_gas, f_other, region, S_coal, S_gas):
        base_coal = self.lca_defaults.loc['Coal', 'S']
        base_gas = self.lca_defaults.loc['Natural gas', 'S']
        base_power = 433 #(.2 * base_coal + .5 * base_gas )

        years = self.smokestack_data.loc[self.initial_year:self.final_year].index
        vals = np.divide((f_coal.multiply(S_coal, axis=0).values + f_gas.multiply(S_gas, axis=0).values),(base_power*(1-f_other)).values).flatten()
        energy_intensity = pd.DataFrame(vals, index=years, columns = ['(Spower_Spower19)_'+ region])
        return energy_intensity

    def fuel_production_em(self, source):
        if source == "Coal" or source == "Natural gas" or source == "Nuclear":
            base = self.lca_defaults.loc[source, 'F']
            if self.F_Pps == "User" or self.F_Pps == "Static" :
                fuel = self.projection(base, self.F_Pps, 'not_applicable', delta=self.delta_F_P)
            else:
                fuel = base * self.energy_intensity
        else:
            years = self.smokestack_data.loc[self.initial_year:self.final_year].index
            fuel = pd.DataFrame(0, index = years, columns = ['S_' + source])

        return fuel

    def powerplant_production_em(self, source):
        base = self.lca_defaults.loc[source, 'P_S'] - self.lca_defaults.loc[source, 'S']
        if self.F_Pps == "User" or self.F_Pps == "Static" :
            powerplant = self.projection(base, self.F_Pps, 'not_applicable', delta=self.delta_F_P)
        else:
            powerplant = base * self.energy_intensity
        return powerplant

    def grid_intensity(self, f_coal, f_gas, f_other):
        years = self.smokestack_data.loc[self.initial_year:self.final_year].index
        emissions = pd.DataFrame(index=years)
        self.get_base_values()

        for source in self.powertypes:
            emissions['S_' + source] = self.smokestack_em(source)
            emissions['Total_' + source] = emissions['S_' + source]

        if 'Fuel Production' in self.counted:
            if self.F_Pps == "Proportional to general energy emission intensity":
                # f_coal = pd.DataFrame(0.2, index=years, columns=['f_coal'])
                # f_gas = pd.DataFrame(0.5, index=years, columns=['f_gas'])
                energy_intensity_c = self.general_energy_emission_intensity(f_coal, f_gas, f_other, "US",
                                                                            emissions['S_Coal'],
                                                                            emissions['S_Natural gas']
                )
                energy_intensity_w = self.general_energy_emission_intensity(f_coal, f_gas, f_other, "world",
                                                                            emissions['S_Coal'],
                                                                            emissions['S_Natural gas'])
                self.energy_intensity = self.f_country * energy_intensity_c.values + (1 - self.f_country) * energy_intensity_w.values

            for source in self.powertypes:
                emissions['F_' + source] = self.fuel_production_em(source)
                emissions['Total_' + source] = emissions['Total_' + source] + emissions['F_' + source]

        if 'Powerplant' in self.counted:
            for source in self.powertypes:
                emissions['P_' + source] = self.powerplant_production_em(source)
                emissions['Total_' + source] = emissions['Total_' + source] + emissions['P_' + source]

        #Overrides emissions value for 'other' if modeling California emissions (where 'other' is largely geothermal, rather than assorted mix)

        #if self.region == 'US_CA':
        #    emissions['S_Other'] = 0
        #    emissions['F_Other'] = 0
        #    emissions['P_Other'] = 36.7
        #    emissions['Total_Other'] = 36.7


        # for source in self.powertypes:
        #     emissions['Total_' + source] = emissions['S_' + source] + emissions['F_' + source] + emissions['P_' + source]

        return emissions

    def charging_profile(self):
        epsilon = pd.DataFrame(index = np.arange(1,25),columns=['demand'])

        if self.evmethod == "Direct input":
            # self.E = 1 - self.O - self.D
            A = [[22,1,1],[1,22,1],[1,1,22]]
            B = [[0.03*self.O],[0.03*self.D],[0.03*self.E]]
            x = np.linalg.inv(A).dot(B)
            epsilon.loc[2:7,'demand'] = x[0,0]
            epsilon.loc[10:15,'demand'] = x[1,0]
            epsilon.loc[18:23,'demand'] = x[2,0]
            epsilon.loc[1, 'demand'] = x[2,0]/3 + 2* x[0,0]/3
            epsilon.loc[8, 'demand'] = x[1,0]/3 + 2* x[0,0]/3
            epsilon.loc[9, 'demand'] = x[0,0]/3 + 2* x[1,0]/3
            epsilon.loc[16, 'demand'] = x[2,0]/3 + 2* x[1,0]/3
            epsilon.loc[17, 'demand'] = x[1,0]/3 + 2* x[2,0]/3
            epsilon.loc[24, 'demand'] = x[0,0]/3 + 2* x[2,0]/3
        else:
            self.Hnd = 100 - self.Hd
            self.fp = 100 - self.fhw - self.fw - self. fh
            fhdw = self.Hd*self.fhw/10000
            fhnw = (self.fhw - fhdw*100)/100
            fhd = self.Hd * self.fh/10000
            fhnd = (self.fh - fhd*100)/100
            fw = self.fw/100
            fp = self.fp/100
            #o	Ɛ = fHdw (HwH ƐHd + Hww Ɛw + Hwp Ɛp)
            #    + fHnw (HwH ƐHn + Hww Ɛw + Hwp Ɛp)
            #    + fHd (HH ƐHd + Hp Ɛp)
            #    + fHn (HH ƐHn + Hp Ɛp)
            #    + fw (ww Ɛw + wp Ɛp)
            #    + fp Ɛp
            vals = fhdw * (self.cp_parameters.loc['Hw_H', 'fraction'] * self.cp['home, discount 12am-7am'].values.flatten()
                           + self.cp_parameters.loc['Hw_w', 'fraction'] * self.cp['work'].values.flatten()
                           + self.cp_parameters.loc['Hw_p', 'fraction'] * self.cp['public'].values.flatten()) +\
                   fhnw * (self.cp_parameters.loc['Hw_H', 'fraction'] * self.cp['home, no discount constant price'].values.flatten()
                           + self.cp_parameters.loc['Hw_w', 'fraction'] * self.cp['work'].values.flatten()
                           + self.cp_parameters.loc['Hw_p', 'fraction'] * self.cp['public'].values.flatten()) + \
                   fhd * (self.cp_parameters.loc['H_H', 'fraction'] * self.cp['home, discount 12am-7am'].values.flatten()
                           + self.cp_parameters.loc['Hp_p', 'fraction'] * self.cp['public'].values.flatten()) + \
                   fhnd * (self.cp_parameters.loc['H_H', 'fraction'] * self.cp['home, no discount constant price'].values.flatten()
                           + self.cp_parameters.loc['Hp_p', 'fraction'] * self.cp['public'].values.flatten()) + \
                   fw * (self.cp_parameters.loc['w_w', 'fraction'] * self.cp['work'].values.flatten()
                           + self.cp_parameters.loc['w_p', 'fraction'] * self.cp['public'].values.flatten()) + \
                   fp * (self.cp_parameters.loc['p_p', 'fraction'] * self.cp['public'].values.flatten())
            epsilon['demand'] = vals

        return epsilon

    def hourly_generation_mix(self, Dh_vals, fp = 0):
        # self.D_source = "Historical"
        # if self.D_source == "Historical":
        #     Dh = pd.read_csv(PATH + 'Dhist.csv', index_col=['hour'])

        # fph = pd.DataFrame(index=np.arange(1, 25))
        Dh = pd.DataFrame(index = np.arange(1,25), columns = [self.region])
        Dh[self.region] = Dh_vals

        nuclear = np.divide((np.ones((24)) * 1 / 24), Dh[self.region].values.flatten()) * fp[
            'Nuclear']
        self.solar_gen = pd.read_csv(PATH + 'Solar_gen.csv', index_col=['hour'])
        self.wind_gen = pd.read_csv(PATH + 'Wind_gen.csv', index_col=['hour'])
        solar = self.solar_gen[self.region].divide(Dh[self.region]).values.flatten() * fp['Solar']
        wind = self.wind_gen[self.region].divide(Dh[self.region]).values.flatten() * fp['Wind']
        f_nondisp_h = solar + wind + nuclear
        ## Storage
        f_temp = np.multiply((f_nondisp_h - 1), Dh_vals)
        f_s = sum(f for f in f_temp if f > 0)
        fdisp_h = np.ones((24)) - f_nondisp_h
        fdisp_h[fdisp_h<0] = 0
        fdispatch_total = fp['Coal'] + fp['Natural gas'] + fp['Hydro'] + fp['Other'] + f_s
        coal = fdisp_h * fp['Coal'] / fdispatch_total
        ng = fdisp_h * fp['Natural gas'] / fdispatch_total
        hydro = fdisp_h* fp['Hydro'] / ( fdispatch_total)
        other = fdisp_h* fp['Other'] / (fdispatch_total)
        storage = fdisp_h* f_s / ( fdispatch_total)
        total = coal + ng + solar + wind + nuclear + hydro + other
        return {"Coal":coal,"Natural gas":ng,"Solar":solar,"Wind":wind,
                "Nuclear": nuclear,"Hydro": hydro,"Other": other,"Total":total}

    def yearly_hourly_generation_mix(self, output_demand,):
        years = self.smokestack_data.loc[self.initial_year:self.final_year].index
        f_ph = pd.DataFrame(index=years,
                            columns=["Coal", "Natural gas", "Solar", "Wind", "Nuclear", "Hydro", "Other", "Total"])

        for year, row in output_demand.iterrows():
            f_ph.loc[year, :] = self.hourly_generation_mix(row['Dh'], row.filter(
                items=["Coal", "Natural gas", "Solar", "Wind", "Nuclear", "Hydro", "Other"]))
        return f_ph

    def hourly_demand(self, D_EV_vals, y0, yc, yf):
        ''' This function_________________________
        INPUTS:
            y0,yc,yf: years
            D_EV_vals: projection of EV demand by year, yc to yf

        OUTPUTS:
            output: annual demand share by power source
            D: annual Total, non-EV, and EV demands
            D_EV_h: fractional share of total EV demand by hour of day

        '''
        #D_table = pd.read_csv(PATH + 'D_' + self.region + '_' +self.PBD + '.csv', index_col = ['year'])
        years = self.smokestack_data.loc[self.initial_year:self.final_year].index
        f_p = pd.DataFrame(0, index = years, columns = ["Coal","Natural gas","Solar","Wind","Nuclear","Hydro","Other"])

        #Projection of non-EV power demand
        if self.PBD == "AEO20":
            #Looks up data
            D_table = pd.read_csv(PATH + 'D_' + self.region + '_' + self.PBD + '.csv', index_col=['year'])
            D = D_table.copy().filter(items = ['D','D_nEV','D_EV'])
            D['D_EV'] = D_EV_vals
        elif self.PBD == "User":
            #Calls extrapolation function that takes user inputs
            Db, DnEV = self.user_PBD(self.region, y0, yc, yf, self.delta_DnEV_P)
            D = pd.DataFrame(0, index=years, columns=["D", "D_nEV", "D_EV"])
            D['D'] = Db
            D['D_nEV'] = DnEV
            D['D_EV'] = D_EV_vals

        PBGM = self.PGM
        if PBGM == "AEO20": # if self.PBGM == "AEO20":
            D_table = pd.read_csv(PATH + 'D_' + self.region + '_' + PBGM + '.csv', index_col=['year'])
            f_p = D_table.loc[:,["Coal","Natural gas","Solar","Wind","Nuclear","Hydro","Other"]].copy()
            if self.model == "fleet":
                ap = pd.DataFrame(
                    {"Coal": self.ap_coal, "Natural gas": self.ap_gas, "Solar": self.ap_solar, "Wind": self.ap_wind,
                     "Nuclear": self.ap_nuc, "Hydro": self.ap_hydro, "Other": self.ap_other}, index=years)
            else:
                ap = f_p
        elif self.PGM == 'User':
            #f_p = self.fp_b
            f_p = self.user_PGM(self.region, y0, yc, yf, self.yf_PGM, self.PGM_speed)
            ap = f_p #check location of this...needs to be compatible with EV case

        self.f_p = f_p #to access outside this function

        D['D_updated'] = D['D_EV'].add(D['D_nEV'])
        #updated fp equation, double check it
        delta_D = D['D_updated'] - D['D']
        output = (f_p.multiply(D['D'], axis=0) + ap.multiply(delta_D, axis=0)).divide(D['D_updated'], axis=0)

        #output = (f_p.multiply(D['D'], axis = 0) + ap.multiply(D['D_EV'], axis = 0)).divide(D['D_updated'], axis = 0)
        D_nEV_h = pd.read_csv(PATH + 'Dhist.csv', index_col=['hour']).filter([self.region])

        D_EV_h_y = pd.DataFrame(0, index=np.arange(1,25), columns=years)
        Dh = pd.Series(data=0,index=years,dtype=object)

        #print(output)

        if self.evmethod in ['Flatten demand', 'Minimize storage, then flatten demand', 'Minimize storage, then flatten dispatchable generation']:

            objective = self.evmethod

            #need to loop over and apply for each year
            for y in years:

                #y = 2050

                D_nEV = D['D_nEV'][y]
                D_EV = D['D_EV'][y]

                f_sol = output['Solar'][y] #ap['Solar'][y]
                f_wind = output['Wind'][y]
                f_nuc = output['Nuclear'][y]


                D_EV_h = self.D_EV_h_optimizer(D_nEV, D_EV, D_nEV_h, f_sol, f_wind, f_nuc, objective)
                D_EV_h_y[y] = D_EV_h #store for each year
                Dh[y] = (( D['D_nEV'][y] * D_nEV_h + D['D_EV'][y] * D_EV_h ) /  D['D_updated'][y]).values.flatten()

        else: #compute as usual

            D_EV_h_y = pd.DataFrame(0, index=np.arange(1, 25), columns=years)
            D_EV_h = self.charging_profile().rename(columns={'demand': self.region})
            for y in years:
                D_EV_h_y[y] = D_EV_h
                Dh[y] = ((D['D_nEV'][y] * D_nEV_h + D['D_EV'][y] * D_EV_h) / D['D_updated'][y]).values.flatten()

        #####

        output['Dh'] = Dh
        output['D'] = D['D']

        return output, D, D_EV_h_y

    def hourly_intensity(self, I_p,  f_ph):

        years = self.smokestack_data.loc[self.initial_year:self.final_year].index
        I_h = pd.DataFrame(0, index=years, columns=['S', 'F', 'P', 'Total'])

        #powertypes = self.powertypes.copy()
        #if self.region == 'US_CA':
        #    powertypes.append('Other')
        #    denominator = 1
        #else:
        #    denominator = 1-f_ph['Other']
        if self.region == 'US_CA':
            denominator = 1
            extra = 36.7 # g/kWh
            #denominator = 1 - f_ph['Other']
            #extra = 0
        else:
            denominator = 1 - f_ph['Other']
            extra = 0


        for source in self.powertypes: #powertypes:

            #I_h['S'] += (I_p['S_' + source].multiply(f_ph[source])).divide(f_ph['Total'])
            I_h['S'] += (I_p['S_' + source].multiply(f_ph[source])).divide(denominator)
            if 'Fuel' in self.counted:
                #I_h['F'] += (I_p['F_' + source].multiply(f_ph[source])).divide(f_ph['Total'])
                I_h['F'] += (I_p['F_' + source].multiply(f_ph[source])).divide(denominator)
            if 'Powerplant' in self.counted:
                #I_h['P'] += (I_p['S_' + source].multiply(f_ph[source])).divide(f_ph['Total'])
                I_h['P'] += (I_p['P_' + source].multiply(f_ph[source])).divide(denominator) + (extra * f_ph['Other'])
            #I_h['Total'] += (I_p['Total_' + source].multiply(f_ph[source])).divide(f_ph['Total'])
            #I_h['Total'] += I_h['S'] + I_h['F'] + I_h['P']
            #I_h['Total'] += (I_p['Total_' + source].multiply(f_ph[source])).divide(denominator)

        I_h['Total'] = I_h['S'] + I_h['F'] + I_h['P']

        S_h = I_h['S'].apply(pd.Series)
        S_h.columns = S_h.columns + 1
        F_h = I_h['F'].apply(pd.Series)
        F_h.columns = F_h.columns + 1
        P_h = I_h['P'].apply(pd.Series)
        P_h.columns = P_h.columns + 1
        Total_h = I_h['Total'].apply(pd.Series)
        Total_h.columns = Total_h.columns + 1

        return I_h, S_h, Total_h

    def hourly_generation_and_demand(self, f_ph, D_h, D, year):
        years = self.smokestack_data.loc[self.initial_year:self.final_year].index
        S_ph = pd.DataFrame(index=np.arange(1,25),
                            columns=["Coal", "Natural gas", "Solar", "Wind", "Nuclear", "Hydro", "Other", "Total"])
        D_h_year = D_h.loc[year].T * D[year] * 1000/365

        for source in self.powertypes:
            S_ph[source] = D_h_year.multiply(f_ph[source].loc[year].T)

        S_ph = S_ph.drop(columns = ['Total'])
        S_ph = S_ph.rename(columns = {'Natural gas':'Gas'})
        D_h_year = pd.DataFrame(np.insert(D_h_year.values, 0, values=D_h_year.loc[24], axis=0))
        S_ph = pd.DataFrame(np.insert(S_ph.values, 0, values=S_ph.loc[24].values, axis=0), columns=["Coal", "Gas", "Solar", "Wind", "Nuclear", "Hydro", "Other"])
        return D_h_year, S_ph

    def aggregator(self, variable, demand, weight = False):
        if weight:
            final = variable * demand * weight
            final = final.groupby(lambda idx: idx).agg(sum).sum(axis=1)
        else:
            final = variable * demand
            final = final.groupby(lambda idx: idx).agg(sum).sum(axis=1)

        return final

    def fleet_grid_integrator(self,D_EV_vals, region, counted ):

        if "Fuel" in counted:
            self.counted = 'Smokestack + Fuel Production + Powerplant Production'
        else:
            self.counted = 'Smokestack'
        self.region = region

        output_demand, D, D_EV_h_y = self.hourly_demand(D_EV_vals.values.flatten(), 'y0', 'yc','yf')

        #print('print output_demand --')
        #print(output_demand)

        f_ph =  self.yearly_hourly_generation_mix(output_demand)
        I_p = self.grid_intensity(f_coal = output_demand['Coal'], f_gas = output_demand['Natural gas'], f_other= output_demand['Other'] )
        I_h, S_h, Total_h = self.hourly_intensity(I_p, f_ph)
        D_h = output_demand.Dh.apply(pd.Series)
        D_h.columns = D_h.columns + 1
        f_ph_n = {}
        for source in self.powertypes:
            f_ph_n[source] = f_ph[source].apply(pd.Series)
            f_ph_n[source].columns = f_ph_n[source].columns + 1

        #print('fph 2035 print')
        #print(f_ph_n['Nuclear'])

        ## Data for plots
        D_2020 = pd.DataFrame(index = np.arange(0,25))
        D_2035 = pd.DataFrame(index =np.arange(0,25))
        D_2050 = pd.DataFrame(index =np.arange(0,25))

        D_h_2020, S_h_2020 = self.hourly_generation_and_demand(f_ph_n, D_h,D.D_updated, 2020)
        D_2020['EV'] = D_EV_h_y[2020]* D_EV_vals.loc[2020,:].values * 1000/365
        D_2020.loc[0,'EV'] = D_2020.loc[24,'EV']
        D_2020['non-EV'] = -D_2020['EV'].subtract(D_h_2020.values.flatten())

        D_h_2035, S_h_2035 = self.hourly_generation_and_demand(f_ph_n, D_h,D.D_updated, 2035)
        D_2035['EV'] = D_EV_h_y[2035] * D_EV_vals.loc[2035, :].values * 1000 / 365
        D_2035.loc[0, 'EV'] = D_2035.loc[24, 'EV']
        D_2035['non-EV'] = -D_2035['EV'].subtract(D_h_2035.values.flatten())

        #print('D_h 2035 print')
        #print(D.loc[2035,:])


        D_h_2050, S_h_2050 = self.hourly_generation_and_demand(f_ph_n, D_h,D.D_updated, 2050)
        D_2050['EV'] = D_EV_h_y[2050] * D_EV_vals.loc[2050, :].values * 1000 / 365
        D_2050.loc[0, 'EV'] = D_2050.loc[24, 'EV']
        D_2050['non-EV'] = -D_2050['EV'].subtract(D_h_2050.values.flatten())
        if 'Fuel' in self.counted:
            grid_CI = self.aggregator(Total_h, D_h)
        else:
            grid_CI = self.aggregator(S_h, D_h)

        return grid_CI, D_2020,D_2035,D_2050,S_h_2020,S_h_2035,S_h_2050

    ##JIM's FUNCTIONS AND INTEGRATOR (also modified inputs as necessary)

    def D_EV_interpolator(self, region, y0, yc, yf, DEVf_D0 ):
        '''This function projects annualized EV power demand a sa function of region and a fraction of present overall demand

        INPUTS:
            y0, yc, yf: years
            region: region, used to look up present demand values
            DEVf_DO: EV power demand in yf, as % of demand today


        OUTPUT:
            D_EV: df of annual EV demand for each year
        '''

        # Reads data
        self.D_past = pd.read_csv(PATH + 'D_past.csv', index_col=['year']) #Total demand
        self.D_EV_past = pd.read_csv(PATH + 'D_EV_past.csv', index_col=['year']) #EV damand

        D0 = self.D_past[region][y0] #Total non-EV demand for specicif regi0on in year y0
        D_EV0 = self.D_EV_past[region][y0] #Total EV demand for specicif regi0on in year y0
        self.D_EV0 = D_EV0

        y = np.arange(yc, yf+1) #vector of years

        #Linear extrapolation
        D_EVf = DEVf_D0/100 * D0
        EV_demand =  D_EV0 + (D_EVf + D_EV0)*(y-y0)/(yf-y0)

        D_EV = pd.DataFrame(EV_demand, index=y)

        return D_EV

    def user_PBD(self, region, y0, yc, yf, delta_DnEV_P):
        ''' This function projects non-EV energy demand based on user input for how per capita demand will change between y0 and yf
        INPUTS:
            region: region
            y0,yc,yf: years
            delta_DnEV_P: % Change in Power Demand Per Person (non-EV), y0 to yf
        OUTPUTS:
            Db: Total projected demand (EV + nEV)
            DnEV: Total non-EV demand
        '''

        #Looks up population data since computed on per capita basis, see equations
        self.pop_past = pd.read_csv(PATH + 'pop_past.csv', index_col=['year'])
        self.P_P0 = pd.read_csv(PATH + 'pop_future.csv', index_col=['year'])

        P0 = self.pop_past[region][y0]
        P = self.P_P0[region].values * P0

        D0 = self.D_past[region][y0]
        D_EV = self.D_EV
        #D_EV0 = D_EV.loc[y0].values
        DnEV0 = D0 - self.D_EV0

        #Extrapolation
        y = np.arange(yc, yf+1)
        DnEV_P = ( (DnEV0/P0) * ( 1 + (delta_DnEV_P/100)*(y-y0)/(yf-y0) ) )
        DnEV = DnEV_P * P
        Db = D_EV.values + DnEV.reshape(31,1)

        Db = pd.DataFrame(Db, index=y)
        DnEV = pd.DataFrame(DnEV, index=y)

        return Db, DnEV

    def user_PGM(self, region, y0, yc, yf, yf_PGM, speed):
        ''' This function projects fractional generation shares of different power sources over time, based on user inputs
        INPUTS:
            y0, yc, yf: years
            yf_PGM: user input for fractional generation mix in the year yf
            speed: string ('Slow', 'Medium', 'Fast') that determines speed of transition to yf_PGM values

        OUTPUTS:
            fp_b: fractional generate shares by year, yc to yf
        '''

        years = np.arange(yc,yf+1)
        fp_b = pd.DataFrame(0, index=years, columns=["Coal", "Natural gas", "Solar", "Wind", "Nuclear", "Hydro", "Other"])

        #sources = ['coal', 'gas', 'nuc', 'hydro', 'wind', 'solar', 'other'
        # sources = ['coal', 'gas', 'solar', 'wind', 'nuc', 'hydro', 'other']

        # VERY IMPORTANT THAT THESE LISTS REMAIN IN THE SAME ORDER
        # sources = ["Coal", "Natural gas", "Solar", "Wind", "Nuclear", "Hydro", "Other"]
        sources = ["coal", "gas", "solar", "wind", "nuc", "hydro", "other"]
        col_header = ["Coal", "Natural gas", "Solar", "Wind", "Nuclear", "Hydro", "Other"] #to keep consistent with other code headers

        i_col = 0


        fpb0 = pd.read_csv(PATH + 'fpb0_' + self.region + '.csv', index_col=['year'])

        if speed == 'Slow':
            s = -1
        elif speed == 'Medium':
            s = 0.75
        elif speed == 'Fast':
            s = 2.5

        #Based on equation sheet
        k = 2*np.log(19)
        a = 1/0.9
        x = (years - y0)/(yf - y0)
        b = s * np.square(x-1) + 1
        y = a * ( 1 / ( 1 + np.exp( -k*(x-0.5)) ) - 0.05 ) * b

        #Iterations over power types for calculation
        for source in sources:

            fp_b[ col_header[i_col] ] = y * ( (yf_PGM[col_header[i_col]]/100) - fpb0['f_' + source][y0] ) + fpb0['f_' + source][y0]

            i_col += 1

        return fp_b

    def yearly_hourly_demand(self, D_tot_y, D_EV_y , D_tot_h, D_EV_h_shares_y, yc, yf):
        '''
        :param D_tot_y: Annual energy demand, by year
        :param D_EV_y: Annual EV energy demand, by year
        :param D_tot_h: Fractional total energy demand 24h profile, by year
        :param D_EV_h_shares_y: Fractional EV energy demand 24h profile, varies by year
        :return: Hourly demand values (total, non-EV, and EV) for each year, yc to yf
        '''

        years = np.arange(yc,yf+1)
        D_h_y = pd.DataFrame(0, index=years, columns=np.arange(1, 25))
        DEV_h_y = pd.DataFrame(0, index=years, columns=np.arange(1, 25))

        for year in years:
            D_h_y.loc[year] = D_tot_h.loc[year] * D_tot_y[year]/365
            DEV_h_y.loc[year] = (D_EV_h_shares_y[year] * D_EV_y[year]/365).values.flatten()

        DnEV_h_y = D_h_y.subtract(DEV_h_y)

        return 1000*D_h_y, 1000*DnEV_h_y, 1000*DEV_h_y

    def D_EV_h_optimizer(self, D_nEV, D_EV, D_nEV_h, f_sol, f_wind, f_nuc, objective):
        #for a single year
        # must add conditional inputs up top

        #Normalize total demand to 1
        D_tot = D_nEV + D_EV
        D_nEV = D_nEV / D_tot
        D_EV = D_EV / D_tot

        D_nEV_h_vals = D_nEV*D_nEV_h

        f_nd_gen = f_sol + f_wind + f_nuc

        if objective == 'Flatten demand':

            #max_DnEVh = D_nEV_h[self.region].max()
            max_DnEVh = D_nEV_h_vals[self.region].max()

            if (1/24) > max_DnEVh:
                # Can divide total demand evenly across 24 horus (perfectly flat)

                D_EV_h = (1/24)*np.ones((24,1)) - D_nEV_h_vals
                D_EV_h = (D_EV_h / D_EV).values

            else:
                # Cannot evenly divide
                k_D = D_EV / ( 24*max_DnEVh - D_nEV )

                D_EV_h = k_D*(max_DnEVh - D_nEV_h_vals )
                D_EV_h = (D_EV_h / D_EV).values

        elif objective == 'Minimize storage, then flatten demand':

            solar_gen = pd.read_csv(PATH + 'Solar_gen.csv', index_col=['hour'])
            wind_gen = pd.read_csv(PATH + 'Wind_gen.csv', index_col=['hour'])

            solar = solar_gen[self.region].values.flatten() * f_sol
            wind = wind_gen[self.region].values.flatten() * f_wind
            nuclear = (np.ones((24)) * 1 / 24) * f_nuc

            G_nd_shape = (solar + wind + nuclear) / f_nd_gen

            G_soak =  ( (G_nd_shape * f_nd_gen) > np.transpose(D_nEV_h_vals.values) ) * ( (G_nd_shape * f_nd_gen) - np.transpose(D_nEV_h_vals.values) )
            G_soak_tot = np.sum(G_soak,axis=1)

            if G_soak_tot == 0 or D_EV / G_soak_tot >= 1:
                f_soak = 1
                D_EV_remaining = np.maximum(D_EV-G_soak_tot,0)

            else:
                f_soak = D_EV / G_soak_tot
                D_EV_remaining = np.maximum(D_EV-G_soak_tot,0)

            D_EV_soak = G_soak * f_soak

            D_nEV_pseudo = D_nEV_h_vals[self.region].values + D_EV_soak
            D_nEV_pseudo_tot = np.sum(D_nEV_pseudo,axis=1)

            #Now flatten demand
            max_DnEVh = D_nEV_pseudo.max()

            if (1 / 24) > max_DnEVh:
                # Can divide total demand evenly across 24 horus (perfectly flat)

                D_EV_h = (1 / 24) * np.ones((1, 24)) - D_nEV_pseudo
                D_EV_h = (D_EV_h + D_EV_soak) / D_EV
                D_EV_h = np.transpose(D_EV_h)

            else:
                # Cannot evenly divide
                k_D = D_EV_remaining / (24 * max_DnEVh - D_nEV_pseudo_tot)

                D_EV_h = k_D * (max_DnEVh - D_nEV_pseudo)
                D_EV_h = (D_EV_h + D_EV_soak) / D_EV
                D_EV_h = np.transpose(D_EV_h)

        elif objective == 'Minimize storage, then flatten dispatchable generation':

            solar_gen = pd.read_csv(PATH + 'Solar_gen.csv', index_col=['hour'])
            wind_gen = pd.read_csv(PATH + 'Wind_gen.csv', index_col=['hour'])

            solar = solar_gen[self.region].values.flatten() * f_sol
            wind = wind_gen[self.region].values.flatten() * f_wind
            nuclear = (np.ones((24)) * 1 / 24) * f_nuc

            G_nd_shape = (solar + wind + nuclear) / f_nd_gen

            G_soak = ((G_nd_shape * f_nd_gen) > np.transpose(D_nEV_h_vals.values)) * (
                        (G_nd_shape * f_nd_gen) - np.transpose(D_nEV_h_vals.values))
            G_soak_tot = np.sum(G_soak, axis=1)

            if G_soak_tot == 0 or D_EV / G_soak_tot >= 1:
                f_soak = 1
                D_EV_remaining = np.maximum(D_EV - G_soak_tot, 0)

            else:
                f_soak = D_EV / G_soak_tot
                D_EV_remaining = np.maximum(D_EV - G_soak_tot, 0)

            D_EV_soak = G_soak * f_soak

            D_nEV_pseudo = D_nEV_h_vals[self.region].values + D_EV_soak
            D_nEV_pseudo_tot = np.sum(D_nEV_pseudo, axis=1)

            # Now flatten dispatchable gen
            G_d = D_nEV_pseudo - (G_nd_shape * f_nd_gen) #pseudo nd demand - nd gen, results in d gen that must be made up at each hour
            G_d_tot = np.sum(G_d,axis=1)

            max_G_d = G_d.max()
            k_gd = D_EV_remaining / (24 * max_G_d - G_d_tot)

            D_EV_h = k_gd * (max_G_d - G_d)
            D_EV_h = (D_EV_h + D_EV_soak) / D_EV
            D_EV_h = np.transpose(D_EV_h)

        return D_EV_h

    def power_grid_integrator(self):

        #timeline
        y0 = 2019 #we currently extrapolate/project out from 2019 since that is the most recent historical data we have
        yc = y0+1 #current year, we report results from yc to yf
        yf = 2050
        years = np.arange(yc,yf+1)

        # type of emissions being accounted for
        self.counted = 'Smokestack + Fuel Production + Powerplant Production'

        # Generate projection of annual EV demand, name it D_EV_vals
        D_EV_vals = self.D_EV_interpolator(self.region, y0, yc, yf, self.DEVf_D0)
        self.D_EV = D_EV_vals

        #Runs hourly demand and generation functions
        output_demand, D, D_EV_h_y = self.hourly_demand(D_EV_vals.values.flatten(),y0,yc,yf)
        DEV = D['D_EV']
        DnEV = D['D_nEV']

        #Converts annual demand fractional shares to hourly fraction shares by year (series stored within dataframe)
        f_ph =  self.yearly_hourly_generation_mix(output_demand)

        #Computes hourly emissions intensities based on demand (Ragini's code)
        I_p = self.grid_intensity(f_coal = output_demand['Coal'], f_gas = output_demand['Natural gas'], f_other= output_demand['Other'] )
        I_h, S_h, Total_h = self.hourly_intensity(I_p, f_ph)

        #Computes hourly demand values (total, non-EV, and EV) for each year
        D_h = output_demand.Dh.apply(pd.Series)
        D_h.columns = D_h.columns + 1

        D_h_y, DnEV_h_y, DEV_h_y = self.yearly_hourly_demand(D['D_updated'], D['D_EV'], D_h, D_EV_h_y, yc, yf)

        #Hourly fractional demand shares by power type
        sources = ["Coal", "Natural gas", "Solar", "Wind", "Nuclear", "Hydro", "Other"]
        f_ph_n = {}
        for source in sources: #self.powertypes:
            f_ph_n[source] = f_ph[source].apply(pd.Series)
            f_ph_n[source].columns = f_ph_n[source].columns + 1

        #Computes hourly generation by power type for each year
        S_p_h = {}  # pd.DataFrame(0, index= self.powertypes, columns = [1])
        for source in sources:
            S_p_h[source] = f_ph_n[source] * D_h_y

        # Initializing dataframes (dfs) to store annual results segmented by stage,end use, and power type
        S_avg = pd.DataFrame(0, index=years, columns=['Value'])
        F_avg = pd.DataFrame(0, index=years, columns=['Value'])
        P_avg = pd.DataFrame(0, index=years, columns=['Value'])
        L_avg = pd.DataFrame(0, index=years, columns=['Value'])
        e_stage = pd.DataFrame(0, index=years, columns=['e_smokestack', 'e_fuel_prod', 'e_powerplant_prod', 'e_tot'], dtype='float')
        e_enduse = pd.DataFrame(0, index=years, columns=['e_EV', 'e_nEV'], dtype='float')
        e_powertype = pd.DataFrame(0, index=years, columns=["Coal", "Natural gas", "Solar", "Wind", "Nuclear", "Hydro", "Other"], dtype='float')
        e_cum_ss = pd.DataFrame(0, index=years, columns=['cum_ss'], dtype='float')
        e_cum_lc = pd.DataFrame(0, index=years, columns=['cum_ss'], dtype='float')

        # Generation by power type each year
        G_p = pd.DataFrame(0, index=years, columns=["Coal", "Natural gas", "Solar", "Wind", "Nuclear", "Hydro", "Other"], dtype='float')
        sources = ["Coal", "Natural gas", "Solar", "Wind", "Nuclear", "Hydro"]

        #Changed for consistency with front end name convention
        S = S_avg
        L = L_avg

        #Compuute to/from storage values
        hours = np.arange(1, 25)
        to_storage = pd.DataFrame(0, index=years, columns=np.arange(1, 25))
        from_storage = pd.DataFrame(0, index=years, columns=np.arange(1, 25))
        fraction_gen_stored = pd.DataFrame(0, index=years, columns=['Value'])

        #Iterates over years and hours to compute relevant values
        for year in years:

            for h in hours:

                #Computes total generation for given hour (Gh) and looks up Dh, makes comparison to determine whether energy is stored or drawn from storage
                Gh = S_p_h['Coal'][h].loc[year] + S_p_h['Natural gas'][h].loc[year] + S_p_h['Solar'][h].loc[year] + S_p_h['Wind'][h].loc[year] + S_p_h['Nuclear'][h].loc[year] + S_p_h['Hydro'][h].loc[year] + S_p_h['Other'][h].loc[year]
                Dh =  D_h_y[h].loc[year]

                if Dh > Gh: #draw from storage
                    to_storage.loc[year,h] = 0
                    from_storage.loc[year,h] = Dh-Gh
                elif Dh < Gh: #curtail to storage
                    to_storage.loc[year,h] = Gh-Dh
                    from_storage.loc[year,h] = 0
                else: #perfect balance between generation and demand
                    to_storage.loc[year,h] = 0
                    from_storage.loc[year,h] = 0

            fraction_gen_stored.loc[year] = to_storage.loc[year].sum() / D_h_y.loc[year].sum() * 100

            #Computes emissions values based on demand and associated emissions constants on

            #Avg for lifecycle segments
            S_avg.loc[year] = sum( D_h.loc[year] * S_h.loc[year] )
            F_avg.loc[year] = sum( D_h.loc[year] * I_h['F'].loc[year] )
            P_avg.loc[year] = sum( D_h.loc[year] * I_h['P'].loc[year] )
            L_avg.loc[year] = sum(D_h.loc[year] * Total_h.loc[year])

            #By stage
            e_stage['e_smokestack'][year] = (S_avg.loc[year] * D['D_updated'][year]) /1000.0
            e_stage['e_fuel_prod'][year] = F_avg.loc[year] * D['D_updated'][year] /1000.0
            e_stage['e_powerplant_prod'][year] = P_avg.loc[year] * D['D_updated'][year] /1000.0 #100000.0, confirm that this change is correct

            e_stage['e_tot'][year] = e_stage['e_smokestack'][year] + e_stage['e_fuel_prod'][year] + e_stage['e_powerplant_prod'][year]

            #Cummulative smokestack and total
            e_cum_ss['cum_ss'][year] = e_stage['e_smokestack'].sum()
            e_cum_lc['cum_ss'][year] = e_stage['e_tot'].sum()

            #End use
            e_enduse['e_EV'][year] = L_avg.loc[year] * D['D_EV'][year] /1000
            e_enduse['e_nEV'][year] = e_stage['e_tot'][year] - e_enduse['e_EV'][year]

            #print(self.f_p['Other'])

            for source in sources:
                e_powertype[source].loc[year] = ( self.f_p[source].loc[year] * D['D_updated'][year] * I_p['Total_'+source].loc[year] )/1000
                G_p[source].loc[year] = self.f_p[source].loc[year] * D['D_updated'][year]

            G_p['Other'].loc[year] = self.f_p['Other'].loc[year] * D['D_updated'][year]
            e_powertype['Other'].loc[year] = e_stage['e_tot'][year] - sum(e_powertype.loc[year])

            #if self.region == 'US_CA':
            #    e_powertype['Other'].loc[year] = (self.f_p['Other'].loc[year] * D['D_updated'][year] * I_p['Total_Other'].loc[year]) / 1000
            #else:
            #    e_powertype['Other'].loc[year] = e_stage['e_tot'][year] - sum ( e_powertype.loc[year] )

        if 'Fuel' in self.counted:
            grid_CI = self.aggregator(Total_h, D_h)
        else:
            grid_CI = self.aggregator(S_h, D_h)

        return {
            'S_p_h': S_p_h,
            'G_p': G_p,
            'DnEV': DnEV,
            'DEV': DEV,
            'D_h_y': D_h_y,
            'DnEV_h_y': DnEV_h_y,
            'DEV_h_y': DEV_h_y,
            'e_stage': e_stage,
            'e_enduse': e_enduse,
            'e_powertype': e_powertype,
            'S': S,
            'L': L,
            'e_cumulative_lc':e_cum_lc,
            'e_cumulative_ss':e_cum_ss,
            'to_storage':to_storage,
            'from_storage':from_storage,
            'fraction_gen_stored':fraction_gen_stored,
        }

if __name__ == '__main__':
    input_set = InputSet.build_default(Grid)
    model = Grid()
    model.prepare(input_set)
    results = model.run()
    print(results)
