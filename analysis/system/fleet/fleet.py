import os
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from analysis.system.grid.grid import Grid
from core import validators, conditionals
from core.common import InputSource, Versioned
from core.inputs import ContinuousInput, OptionsInput, Default, InputSet, Option, InputGroup, ShareTableInput, Tooltip

PATH = os.getcwd() + '/analysis/system/fleet/'
POWERTRAINS = ['FCEV', 'BEV', 'PHEV', 'HEV', 'ICED', 'ICEG']
SIZES = [
    { 'name': 'sedan', 'label': 'Sedan' },
    { 'name': 'LT', 'label': 'Light Truck' },
]
REGIONS = ['US', 'US, California', 'US, Texas', 'US, New York', 'Norway']
FLEET_DATA = pd.read_csv(PATH + "fleet_data.csv", index_col='year')

base_year, projected_year = [2019, 2050]

def percent_value(x):
    if np.isnan(x):
        return 0
    else:
        return int(x * 100)

def sales_share_defaults(powertrain, size, year):
    region_keys = {
        'US': 'US',
        'US, California': 'US_CA',
        'US, Texas': 'US_TX',
        'US, New York': 'US_NY',
        'Norway': 'Norway',
    }

    def column_name(region, msps):
        return f'f_{powertrain}_{size}_{region_keys[region]}_{msps}'

    def default_value(region):
        return percent_value(FLEET_DATA[column_name(region, 'default')][base_year])

    def projected_value(region, msps):
        return percent_value(FLEET_DATA[column_name(region, msps)][projected_year])

    if year == base_year:
        return [
            Default(
                default_value(region),
                conditionals=[conditionals.input_equal_to('region', region)],
            )
            for region in REGIONS
        ]
    else:
        return [
            Default(
                projected_value(region, msps),
                conditionals=[
                    conditionals.input_equal_to('region', region),
                    conditionals.input_equal_to('msps2', msps),
                ],
            )
            for region in REGIONS
            for msps in ['AEO20', '2035_ICE_ban', '~BNEF20']
            if column_name(region, msps) in FLEET_DATA.columns
        ] + [
            Default(
                default_value(region),
                conditionals=[
                    conditionals.input_equal_to('region', region),
                    conditionals.input_equal_to('msps2', 'Static'),
                ],
            )
            for region in REGIONS
        ]

class FleetModel(InputSource, Versioned):

    @classmethod
    def user_inputs(cls):
        powertrain_tooltips = {
            'FCEV': Tooltip(
                'Fuel Cell Electric Vehicle, e.g., Toyota Mirai. Fuel = hydrogen.'
            ),
            'BEV': Tooltip(
                'Battery Electric Vehicle, e.g., Tesla Model 3. Fuel = electricity. Often called an EV.'
            ),
            'PHEV': Tooltip(
                'Plug-in Hybrid Electric Vehicle, e.g., Toyota Prius Prime. Fuels = electricity & gasoline. Often called a plug-in hybrid.'
            ),
            'HEV': Tooltip(
                'Hybrid Electric Vehicle, e.g., Toyota Prius. Fuel = gasoline. Often called a hybrid.'
            ),
            'ICED': Tooltip(
                'Internal Combustion Engine vehicle - Diesel. Often called a diesel.'
            ),
            'ICEG': Tooltip(
                'Internal Combustion Engine vehicle - Gasoline. Often called a gas car.'
            ),
        }

        return [
            OptionsInput(
                'region',
                'Region',
                options=REGIONS,
                defaults=[Default('US')],
            ),
            InputGroup('sales', 'Sales', children=[
                OptionsInput(
                    'msps2',
                    'Projection for: Sales Share by Powertrain',
                    options=[
                        Option('~BNEF20', conditionals=[conditionals.input_equal_to('region', 'US')]),
                        Option('AEO20', conditionals=[conditionals.input_not_equal_to('region', 'Norway')]),
                        Option('Static'),
                        Option('User'),
                        Option('2035_ICE_ban',
                               conditionals=[conditionals.input_equal_to('region', 'US, California')]),
                    ],
                    defaults=[
                        Default('~BNEF20', conditionals=[conditionals.input_equal_to('region', 'US')]),
                        Default('AEO20', conditionals=[conditionals.input_not_equal_to('region', 'Norway')]),
                        Default('Static'),
                    ],
                ),
                ShareTableInput(
                    'sedan_sales_shares', 'Sedan Sales Shares (%)',
                    columns=[str(base_year), str(projected_year)],
                    rows=[
                        ShareTableInput.Row(
                            powertrain,
                            tooltip=powertrain_tooltips.get(powertrain),
                            cells=[
                                ShareTableInput.Cell(
                                    defaults=sales_share_defaults(powertrain, 'sedan', base_year),
                                ),
                                ShareTableInput.Cell(
                                    defaults=sales_share_defaults(powertrain, 'sedan', projected_year),
                                ),
                            ]
                        )
                        for powertrain in POWERTRAINS
                    ],
                    on_change_actions=[
                        {
                            'type': 'set_input_to',
                            'target': 'msps2',
                            'value': 'User',
                        }
                    ],
                ),
                ShareTableInput(
                    'LT_sales_shares', 'Light Truck Sales Shares (%)',
                    columns=[str(base_year), str(projected_year)],
                    rows=[
                        ShareTableInput.Row(
                            powertrain,
                            tooltip=powertrain_tooltips.get(powertrain),
                            cells=[
                                ShareTableInput.Cell(
                                    defaults=sales_share_defaults(powertrain, 'LT', base_year),
                                ),
                                ShareTableInput.Cell(
                                    defaults=sales_share_defaults(powertrain, 'LT', projected_year),
                                ),
                            ]
                        )
                        for powertrain in POWERTRAINS
                    ],
                    on_change_actions=[
                        {
                            'type': 'set_input_to',
                            'target': 'msps2',
                            'value': 'User',
                        }
                    ],
                ),
                OptionsInput(
                    'msps1',
                    'Projection for: Sales Mix by Size',
                    options=['Static', 'VIS20', 'User'],
                    defaults=[Default('Static')],
                ),
                ContinuousInput(
                    'size_share',
                    'Light Truck Sales Share, 2050',
                    conditionals=[conditionals.input_equal_to('msps1', 'User')],
                ),
                OptionsInput(
                    'spp',
                    'Projection for: Sales/Person ',
                    options=[
                        Option('AEO20', conditionals=[conditionals.input_not_equal_to('region', 'Norway')]),
                        Option('Static'),
                        Option('User'),
                    ],
                    defaults=[
                        Default('AEO20', conditionals=[conditionals.input_not_equal_to('region', 'Norway')]),
                        Default('Static'),
                    ],
                ),
                OptionsInput(
                    'growth_curve',
                    'New Tech Growth:',
                    options=['s curve', 'linear'],
                    defaults=[Default('s curve')],
                    conditionals=[conditionals.input_equal_to('msps2', 'User')],
                ),
                ContinuousInput(
                    'delta_spp',
                    '% Change in Sales Per Person, 2019-50',
                    conditionals=[conditionals.input_equal_to('spp', 'User')],
                ),
            ]),
            InputGroup('fuel_economy', 'Fuel Economy', children=[
                OptionsInput(
                    'fuel_int',
                    'Projection for: Fuel Economy',
                    options=['MIT15', 'Static', 'User'],
                    defaults=[Default('MIT15')],
                ),
                ShareTableInput(
                    'fuel_int_values', '% Drop in Fuel/Distance, 2019-2050',
                    columns=[None],
                    rows=[
                        ShareTableInput.Row(
                            'FCEV',
                            tooltip=powertrain_tooltips['FCEV'],
                            cells=[
                                ShareTableInput.Cell(defaults=[
                                    Default(38, conditionals=[conditionals.input_equal_to('fuel_int', 'MIT15')]),
                                    Default(0, conditionals=[conditionals.input_equal_to('fuel_int', 'Static')]),
                                ]),
                            ]
                        ),
                        ShareTableInput.Row(
                            'BEV',
                            cells=[
                                ShareTableInput.Cell(defaults=[
                                    Default(31, conditionals=[conditionals.input_equal_to('fuel_int', 'MIT15')]),
                                    Default(0, conditionals=[conditionals.input_equal_to('fuel_int', 'Static')]),
                                ]),
                            ]
                        ),
                        ShareTableInput.Row(
                            'PHEV',
                            cells=[
                                ShareTableInput.Cell(defaults=[
                                    Default(46, conditionals=[conditionals.input_equal_to('fuel_int', 'MIT15')]),
                                    Default(0, conditionals=[conditionals.input_equal_to('fuel_int', 'Static')]),
                                ]),
                            ]
                        ),
                        ShareTableInput.Row(
                            'HEV',
                            cells=[
                                ShareTableInput.Cell(defaults=[
                                    Default(46, conditionals=[conditionals.input_equal_to('fuel_int', 'MIT15')]),
                                    Default(0, conditionals=[conditionals.input_equal_to('fuel_int', 'Static')]),
                                ]),
                            ]
                        ),
                        ShareTableInput.Row(
                            'ICED',
                            cells=[
                                ShareTableInput.Cell(defaults=[
                                    Default(41, conditionals=[conditionals.input_equal_to('fuel_int', 'MIT15')]),
                                    Default(0, conditionals=[conditionals.input_equal_to('fuel_int', 'Static')]),
                                ]),
                            ]
                        ),
                        ShareTableInput.Row(
                            'ICEG',
                            cells=[
                                ShareTableInput.Cell(defaults=[
                                    Default(41, conditionals=[conditionals.input_equal_to('fuel_int', 'MIT15')]),
                                    Default(0, conditionals=[conditionals.input_equal_to('fuel_int', 'Static')]),
                                ]),
                            ]
                        ),
                    ],
                    on_change_actions=[
                        {
                            'type': 'set_input_to',
                            'target': 'fuel_int',
                            'value': 'User',
                        }
                    ],
                ),
            ]),
            InputGroup('fuel_production', 'Fuel Production', children=[
                ContinuousInput(
                    'biofuel_perc_vol_2050',
                    '% Biofuel in Gas Pump Fuel, by Vol., 2050',
                    defaults=[Default(10)],
                    validators=[
                        validators.lte(15, message='Only ~20% of US cars in 2019 are "flex fuel", i.e. rated to use blends >15% ethanol and up to 85%.', warning=True)
                    ]
                ),
                ContinuousInput(
                    'bio_fuel_prod_e',
                    'Biofuel Lifecycle Emissions, (gCO2e/MJ)',
                    defaults=[Default(51)],
                ),

                OptionsInput(
                    'h2_prod',
                    'Hydrogen production method',
                    options=['SMR', 'SMR with carbon capture', 'Electrolysis with green electricity'],
                    defaults=[Default('SMR')],
                ),
                OptionsInput(
                    'fgi',
                    'Ignore Fleet Grid Interaction?',
                    options=[
                        Option('Yes'),
                        Option('No', conditionals=[conditionals.input_not_equal_to('region', 'US'), conditionals.input_not_equal_to('region', 'Norway')]),
                    ],
                    defaults=[Default('Yes')],
                ),
                OptionsInput(
                    'cips',
                    'Projection for: Grid Carbon Intensity',
                    options=[
                        Option('AEO20', conditionals=[conditionals.input_not_equal_to('region', 'Norway')]),
                        Option('VIS20', conditionals=[conditionals.input_not_equal_to('region', 'Norway')]),
                        Option('Static'),
                        Option('User'),
                    ],
                    defaults=[
                        Default('AEO20', conditionals=[conditionals.input_not_equal_to('region', 'Norway')]),
                        Default('VIS20', conditionals=[conditionals.input_not_equal_to('region', 'Norway')]),
                        Default('Static'),
                    ],
                    conditionals=[conditionals.input_equal_to('fgi', 'Yes')],
                ),
                ContinuousInput(
                    'delta_I',
                    '% Decline in Grid Carbon Intensity, 2019-50',
                    conditionals=[conditionals.input_equal_to('cips', 'User')],
                ),
            ] + Grid.user_inputs(fleet = True)),
            InputGroup('survival_distance', 'Survival & Distance', children=[
                OptionsInput(
                    'car_longevity',
                    'Projection for: Lifetime of Average Car',
                    options=['VIS20', 'Static', 'User'],
                    defaults=[Default('Static')],
                    tooltip=Tooltip('Average car lifetime is ~17 years for cars sold in 2019 in the US. Average car lifetime ≠ average car age, which was ~12 years in 2019 in the US. Average car lifetime = car life expectancy = average time from sale to retirement or scrappage. The model assumes empirically based variation around this average, such that ~half of cars last longer, and ~half shorter.',
                        source='2021 Transportation Energy Data Book, by the US DOE: Tables 3.6, 3.13, 3.14, & 4.3 ; Internal',
                        source_link= 'https://tedb.ornl.gov/wp-content/uploads/2021/02/TEDB_Ed_39.pdf
                ),
                ContinuousInput(
                    'delta_hl',
                    '% Change in Lifetime of Average Car, 2019-50',
                    conditionals=[conditionals.input_equal_to('car_longevity', 'User')],
                    tooltip=Tooltip('Average car lifetime is ~17 years for cars sold in 2019 in the US. Average car lifetime ≠ average car age, which was ~12 years in 2019 in the US. Average car lifetime = car life expectancy = average time from sale to retirement or scrappage. The model assumes empirically based variation around this average, such that ~half of cars last longer, and ~half shorter.',
                        source='2021 Transportation Energy Data Book, by the US DOE: Tables 3.6, 3.13, 3.14, & 4.3 ; Internal',
                        source_link='https://tedb.ornl.gov/wp-content/uploads/2021/02/TEDB_Ed_39.pdf
                ),
                ContinuousInput(
                    'D_life',
                    'Life Distance per Car, 2020-50, Default',
                    unit='thousand mi',
                    tooltip=Tooltip('Life distance traveled by a car with default average lifetime of ~17 years. If user increases the lifetime of cars (by X %), average life distance will also increase (by < X %). For any individual car of any lifetime, distance declines ~2 %/yr.',
                                    source= '2021 Transportation Energy Data Book, by the US DOE: Table 3.14 ; Internal',
                                    source_link='https://tedb.ornl.gov/wp-content/uploads/2021/02/TEDB_Ed_39.pdf
                    defaults=[Default(206)],
                ),
                ContinuousInput(
                    'mode', 'PHEV Electric Mode Share',
                    validators=[validators.integer(), validators.gte(0), validators.lte(100)],
                    defaults=[Default(50)],
                    tooltip=Tooltip(
                        'Share of PHEV distance driven in electric mode, also called battery-depleting or charge-depleting mode. The remaining distance is driven in fuel mode, also called called charge-sustaining or combustion mode. In reality, there are also hybrid modes.'),
                ),
            ]),
            InputGroup('demographics', 'Demographics', children=[
                OptionsInput(
                    'pps',
                    'Projection for: Population',
                    options=[
                        Option('AEO20', conditionals=[conditionals.input_not_equal_to('region', 'Norway')]),
                        Option('SSB', conditionals=[conditionals.input_equal_to('region', 'Norway')]),
                        Option('Static'),
                        Option('User')
                    ],
                    defaults=[
                        Default('AEO20', conditionals=[conditionals.input_not_equal_to('region', 'Norway')]),
                        Default('SSB', conditionals=[conditionals.input_equal_to('region', 'Norway')]),
                    ],
                ),
                ContinuousInput(
                    'delta_p',
                    '% Change in Population, 2019-50',
                    conditionals=[conditionals.input_equal_to('pps', 'User')],
                ),
            ]),
            InputGroup('costs', 'Costs', children=[
                OptionsInput(
                    'fuel_price_source',
                    'Projection for: fuel prices',
                    options=[
                        Option('User'),
                        Option('Static'),
                        Option('EPPA_Reference',conditionals=[conditionals.input_equal_to('region', 'Norway')]),
                        Option('EPPA_Paris_Forever', conditionals=[conditionals.input_equal_to('region', 'Norway')]),
                        Option('EPPA_Paris_2C', conditionals=[conditionals.input_equal_to('region', 'Norway')]),
                        Option('AEO20', conditionals=[conditionals.input_not_equal_to('region', 'Norway')]),
                    ],
                defaults =[Default('User')],
                ),
                ContinuousInput(
                    'gasoline_price_change',
                    '% change in gasoline price, 2019-50',
                    defaults=[Default(0)],
                    conditionals=[conditionals.input_equal_to('fuel_price_source', 'User')],
                ),
                ContinuousInput(
                    'diesel_price_change',
                    '% change in diesel price, 2019-50',
                    defaults=[Default(0)],
                    conditionals=[conditionals.input_equal_to('fuel_price_source', 'User')],
                ),
                ContinuousInput(
                    'electricity_price_change',
                    '% change in electricity price, 2019-50',
                    defaults=[Default(0)],
                    conditionals=[conditionals.input_equal_to('fuel_price_source', 'User')],
                ),
                ContinuousInput(
                    'h2_price_change',
                    '% change in hydrogen price, 2019-50',
                    defaults=[Default(0)],
                    conditionals=[conditionals.input_equal_to('fuel_price_source', 'User')],
                ),
                ContinuousInput(
                    'biofuel_price_change',
                    '% change in biofuel price, 2019-50',
                    defaults=[Default(0)],
                    conditionals=[conditionals.input_equal_to('fuel_price_source', 'User')],
                ),
                OptionsInput(
                    'yp_BEV',
                    'BEV & ICEG Prices Equal in:',
                    options=[
                        Option(2025),
                        Option(2030),
                        Option(2035),
                        Option(2040),
                        Option(2045),
                    ],
                    defaults=[Default(2030)],
                ),
                OptionsInput(
                    'yp_FCEV',
                    'FCEV & ICEG Prices Equal in:',
                    options=[
                        Option(2035),
                        Option(2040),
                        Option(2045),
                    ],
                    defaults=[Default(2040)],
                ),
            ]),
        ]
    @classmethod
    def inputs(cls):
        return cls.user_inputs()

    def __init__(self):
        self.fleet_data = FLEET_DATA
        self.defaults = pd.read_csv(PATH + 'fleet_defaults.csv')
        self.lowest_year = 1970
        self.highest_year = 2050
        self.initial_year = 2000
        self.cutoff_life = 50
        self.msps1 = None
        self.mode = None
        self.delta_I = None
        self.fgi = 'Yes'
        self.emissions_view = 'Tailpipe & Smokestack & Fuel Production'
        self.grid = Grid()
        self.if_s_curve = True #
        self.d_future = 'Static'
        self.d_a_future = 'Static'

    def set_defaults(self):
        self.powertrain_size_share = {
            'sedan': self.sedan_sales_shares[str(projected_year)],
            'LT': self.LT_sales_shares[str(projected_year)],
        }
        self.fuel_int_values = self.fuel_int_values

        self.baseline_year = 2019
        self.powertrains = POWERTRAINS
        self.sizes = [size['name'] for size in SIZES]

        if self.mode is not None and 'PHEV' not in self.powertrains:
            self.powertrains.append('PHEV')

        self.initial_year = 2000
        if self.region == 'Norway':
            self.initial_year = 2010
        self.final_year = 2050
        if self.mode is not None:
            self.mode = float(self.mode)

        if self.msps1 == "User":
            self.size_share = [(100 - self.size_share), self.size_share ]

        if self.delta_I is not None and self.delta_I > 0:
            self.delta_I *= -1
        self.delta_I_fix = self.delta_I


        REGIONS2 = ['US', 'US_CA', 'US_TX', 'US_NY', 'Norway']
        self.region = REGIONS2[REGIONS.index(self.region)]

        if self.fgi == 'No':
            self.grid.prepare(self.input_set, fleet=True)
            self.cips = 'AEO20'

        categories = [self.pps, self.spp, self.car_longevity, self.d_future, self.d_a_future, self.fuel_int, self.cips]
        deltas = ['delta_p','delta_spp','delta_hl','delta_d_future','delta_d_a_future','delta_I']
        defaults =[20, 0, 0, 20, 1.92, 0]
        for category, delta_name, default_value in zip(categories, deltas, defaults):
            if category != "User":
                setattr(self, delta_name, default_value)

        self.fleet_defaults = self.defaults.loc[self.defaults.region == self.region,:]
        if self.msps1 != "User":
            self.size_share = [0] * len(self.sizes)

        if self.msps2 != "User":
            self.powertrain_size_share = {}
            for size in self.sizes:
                pt_list = []
                for powertrain in self.powertrains:
                    pt_list.append(0)
                self.powertrain_size_share.update({size:pt_list})
            self.growth_curve = 's curve'

        if self.fuel_int != "User":
            self.delta_fuel_by_pt = {
                'ICEG': 0,
                'ICED': 0,
                'BEV': 0,
                'PHEV': 0,
                'HEV': 0,
                'FCEV':0,
            }
        else:
            self.delta_fuel_by_pt = {
                'FCEV': -self.fuel_int_values[0],
                'BEV': -self.fuel_int_values[1],
                'PHEV': -self.fuel_int_values[2],
                'HEV': -self.fuel_int_values[3],
                'ICED': -self.fuel_int_values[4],
                'ICEG': -self.fuel_int_values[5],
            }

        if self.region == "US" and self.region == "Norway":
            self.fgi = "Yes"

    def prepare(self, input_set):
        super().prepare(input_set)
        self.set_defaults()

    def pick_sources(self,variable):
        historical = self.fleet_defaults.loc[self.fleet_defaults.variables == variable,'Historical']
        return historical

    def projection(self, base, projection_var, projection_col, delta, y0 = 0, yf = 0, flag = False):
        """
        :param projection_var:
        :param projection_col:
        :param delta:
        :return:
        """

        if y0 == 0:
            y0 = self.baseline_year
            yf = self.final_year

        years = self.fleet_data.loc[y0 + 1:yf].index
        projected_data = pd.DataFrame(index=years, columns=[projection_col])
        if projection_var =='Static':
            projected_data.loc[years, projection_col] = base
        elif projection_var != "User":
            projected_data.loc[years, projection_col] = base * self.fleet_data.loc[years, projection_col]
        else:
            if flag:
                projected_data.loc[years, projection_col] = base + delta / 100 * (years.values - y0) / (yf - y0)
            else:
                projected_data.loc[years, projection_col] = base * (
                    1 + delta/100 * (years.values - y0) / (yf - y0))

        return projected_data

    def sales_total(self,base_pop,base_spp):
        """

        :return:
        """
        if "US" in self.region:
            reg = "US"
        else:
            reg = self.region

        pop_projection = self.projection(base_pop.values,self.pps, 'pop_future_'+ reg + '_' + self.pps, self.delta_p)

        sales_per_pop_projection = self.projection(base_spp.values,self.spp, 'Spp_future_US_'  + self.spp, self.delta_spp)
        total_sales = sales_per_pop_projection.mul(pop_projection.values, axis = 1)

        return total_sales,pop_projection,sales_per_pop_projection

    def powertrain_size_sales_defaults(self, years, size, powertrain, total_sales):
        """
        :param years:
        :param size:
        :param powertrain:
        :return:
        """
        f_pt_size = 'f_' + powertrain + '_' + size + self.pick_sources('fts')
        F_size = 'F_' + size + self.pick_sources('Fs')

        f_default = self.fleet_data.loc[years, f_pt_size]
        F_default = self.fleet_data.loc[years, F_size]
        market_share = f_default.mul(F_default.values,axis =1)
        sales = market_share.mul(total_sales.values,axis =1)

        return sales,f_default,F_default

    def powertrain_size_sales_model(self, bases, years, size, size_share, powertrain, powertrain_size_share, total_sales):
        """

        :param powertrain_size_share:
        :param size_share:
        :param years:
        :param size:
        :param powertrain:
        :return:
        """
        if self.msps1 == "VIS20":
            reg = "US"
        else:
            reg = self.region

        f_pt_size = 'f_' + powertrain + '_' + size + '_' + self.region + '_' + self.msps2  
        F_size = 'F_' + size + '_' + reg + '_' + self.msps1

        if self.msps1 != "User" and self.msps1 != "Static":
            bases['base_Fs'] = [1]
        if self.msps2 != "User" and self.msps2 != "Static":
            bases['base_fts'] = [1]
        if bases['base_fts'][0] == 0:
            delta_f = powertrain_size_share
            flag1 = True
        else:
            delta_f = (powertrain_size_share - float(bases['base_fts'][0])*100)/float(bases['base_fts'][0])
            flag1 = False
        if bases['base_Fs'][0] == 0:
            delta_f = size_share
            flag2 = True
        else:
            delta_F = (size_share - float(bases['base_Fs'][0])*100)/float(bases['base_Fs'][0])
            flag2 = False


        f_model = self.projection(bases['base_fts'],self.msps2, f_pt_size, delta_f, flag = flag1)
        F_model = self.projection(bases['base_Fs'],self.msps1, F_size, delta_F, flag = flag2)

        F_model = self.projection(bases['base_Fs'], self.msps1, F_size, delta_F, flag=flag2)

        if self.if_s_curve and self.msps2 == 'User' :
            f_model = self.f_s_curve_table['f_' + powertrain + '_' + size]
            f_model = pd.DataFrame({f_pt_size:f_model})
        else:
            f_model = self.projection(bases['base_fts'],self.msps2, f_pt_size, delta_f, flag = flag1)

        market_share = f_model.mul(F_model.values, axis = 1)
        f_region = 1
        final_sales = market_share.mul(total_sales.values,axis =1).rename(columns = {f_pt_size:0})*f_region

        return F_model, final_sales

    def f_s_curve(self):

        y0 = self.baseline_year
        yf = self.final_year

        F_size = 'F_' + 'LT' + self.pick_sources('Fs')
        F_LT_yi = self.fleet_data.loc[y0, F_size].values

        if self.msps1 == 'Static':
            F_LT_f = F_LT_yi 
        else:
            F_LT_f = self.size_share[1] / 100 

        f_yi = {}
        f_yf = {}
        pt_keys = self.powertrains
        f_sedan_yf = self.powertrain_size_share['sedan']
        f_LT_yf = self.powertrain_size_share['LT']
        f_sedan_yf_dic = {pt_keys[i]: f_sedan_yf[i] for i in range(len(pt_keys))}
        f_LT_yf_dic = {pt_keys[i]: f_LT_yf[i] for i in range(len(pt_keys))}

        for pt in self.powertrains:

            f_pt_sedan = 'f_' + pt + '_' + 'sedan' + self.pick_sources('fts')

            f_sedan_yi = self.fleet_data.loc[y0, f_pt_sedan].values
            f_sedan_yf = f_sedan_yf_dic[pt]

            f_pt_LT = 'f_' + pt + '_' + 'LT' + self.pick_sources('fts')
            f_LT_yi = self.fleet_data.loc[y0, f_pt_LT].values
            f_LT_yf = f_LT_yf_dic[pt]

            f_yi[pt] = ( f_LT_yi*F_LT_yi + f_sedan_yi*(1-F_LT_yi) ) 
            f_yf[pt] = ( f_LT_yf * F_LT_f + f_sedan_yf * (1 - F_LT_f) ) / 100 

        if self.growth_curve == 's curve':
            f_PHEV_eq = np.maximum(0.95, 1.01 * f_yf['PHEV'])
            f_BEV_eq = np.maximum(0.95, 1.01 * f_yf['BEV'])
            f_FCEV_eq = np.minimum(1.01, 1.50 * f_yf['FCEV'])
            N = yf - y0 + 1
            dt = 1 / (N - 1)
            t = dt * np.arange(0, N - 1)
            if f_yi['BEV'] < f_yf['BEV']:

                if f_yi['BEV'] == 0:
                    f_yi['BEV'] = 0.0001

                if f_yf['BEV'] == f_BEV_eq:
                    f_BEV_eq = 1.01 * (f_yf['BEV']) 

                a = math.log( (f_BEV_eq / f_yi['BEV']) - 1)
                b = math.log( ( (f_BEV_eq / f_yi['BEV']) - 1 ) / ( (f_BEV_eq / f_yf['BEV']) - 1 ) )


                f_BEV = f_BEV_eq / (1 + np.exp(-(b*t - a)) )
                f_BEV = f_BEV.reshape(-1,1)
            else:
                f_BEV = f_yi['BEV'] + t*(f_yf['BEV'] - f_yi['BEV'])
                f_BEV = f_BEV.reshape(-1, 1)
            if f_yi['PHEV'] < f_yf['PHEV']:

                if f_yi['PHEV'] == 0:
                    f_yi['PHEV'] = 0.0001

                if f_yf['PHEV'] == f_PHEV_eq:
                    f_PHEV_eq = 1.01 * f_yf['PHEV'] 

                a = math.log( (f_PHEV_eq / f_yi['PHEV']) - 1)
                b = math.log( ( (f_PHEV_eq / f_yi['PHEV']) - 1 ) / ( (f_PHEV_eq / f_yf['PHEV']) - 1 ) )

                f_PHEV = f_PHEV_eq / (1 + np.exp(-(b*t - a)) )
                f_PHEV = f_PHEV.reshape(-1,1)
            else:
                f_PHEV = f_yi['PHEV'] + t*(f_yf['PHEV'] - f_yi['PHEV'])
                f_PHEV = f_PHEV.reshape(-1, 1)
            if f_yi['FCEV'] < f_yf['FCEV']:

                if f_yi['FCEV'] == 0:
                    f_yi['FCEV'] = 0.0001

                if f_yf['FCEV'] == f_FCEV_eq:
                    f_FCEV_eq = 1.01 * f_yf['FCEV'] 

                a = math.log( (f_FCEV_eq / f_yi['FCEV']) - 1)
                b = math.log( ( (f_FCEV_eq / f_yi['FCEV']) - 1 ) / ( (f_FCEV_eq / f_yf['FCEV']) - 1 ) )

                f_FCEV = f_FCEV_eq / (1 + np.exp(-(b*t - a)) )
                f_FCEV = f_FCEV.reshape(-1,1)
            else:
                f_FCEV = f_yi['FCEV'] + t*(f_yf['FCEV'] - f_yi['FCEV'])
                f_FCEV = f_FCEV.reshape(-1, 1)
        else:

            N = yf - y0 + 1
            dt = 1 / (N - 1)
            t = dt * np.arange(0, N - 1)

            f_PHEV = f_yi['PHEV'] + t * (f_yf['PHEV'] - f_yi['PHEV'])
            f_PHEV = f_PHEV.reshape(-1, 1)

            f_FCEV = f_yi['FCEV'] + t * (f_yf['FCEV'] - f_yi['FCEV'])
            f_FCEV = f_FCEV.reshape(-1, 1)

            f_BEV = f_yi['BEV'] + t * (f_yf['BEV'] - f_yi['BEV'])
            f_BEV = f_BEV.reshape(-1, 1)


        f_HEV = f_yi['HEV'] + t * ( f_yf['HEV'] - f_yi['HEV'] )
        f_HEV = f_HEV.reshape(-1, 1)

        f_ICED = f_yi['ICED'] + t * (f_yf['ICED'] - f_yi['ICED'])
        f_ICED = f_ICED.reshape(-1, 1)

        f_ICEG = 1 - (f_BEV + f_PHEV + f_FCEV + f_ICED + f_HEV)
        f_BEV_sedan_yi = self.fleet_data.loc[y0, 'f_' + 'BEV' + '_' + 'sedan' + self.pick_sources('fts')].values
        if f_BEV[-1] == f_BEV[0]:
            f_BEV_sedan = f_BEV_sedan_yi * np.ones(N-1).reshape(-1,1)
        else:
            f_BEV_sedan =  f_BEV_sedan_yi + ( f_BEV - f_BEV[0] ) * (f_sedan_yf_dic['BEV']/ 100 - f_BEV_sedan_yi) / ( f_BEV[-1] - f_BEV[0] )

        f_PHEV_sedan_yi = self.fleet_data.loc[y0, 'f_' + 'PHEV' + '_' + 'sedan' + self.pick_sources('fts')].values
        if f_PHEV[-1] == f_PHEV[0]:
            f_PHEV_sedan = f_PHEV_sedan_yi * np.ones(N-1).reshape(-1,1)
        else:
            f_PHEV_sedan = f_PHEV_sedan_yi + (f_PHEV - f_PHEV[0]) * (f_sedan_yf_dic['PHEV'] / 100 - f_PHEV_sedan_yi) / (f_PHEV[-1] - f_PHEV[0])

        f_FCEV_sedan_yi = self.fleet_data.loc[y0, 'f_' + 'FCEV' + '_' + 'sedan' + self.pick_sources('fts')].values
        if f_FCEV[-1] == f_FCEV[0]:
            f_FCEV_sedan = f_FCEV_sedan_yi * np.ones(N-1).reshape(-1,1)
        else:
            f_FCEV_sedan = f_FCEV_sedan_yi + (f_FCEV - f_FCEV[0]) * (f_sedan_yf_dic['FCEV'] / 100 - f_FCEV_sedan_yi) / (f_FCEV[-1] - f_FCEV[0])

        f_HEV_sedan_yi = self.fleet_data.loc[y0, 'f_' + 'HEV' + '_' + 'sedan' + self.pick_sources('fts')].values
        if f_HEV[-1] == f_HEV[0]:
            f_HEV_sedan = f_HEV_sedan_yi * np.ones(N-1).reshape(-1,1)
        else:
            f_HEV_sedan = f_HEV_sedan_yi + (f_HEV - f_HEV[0]) * (f_sedan_yf_dic['HEV'] / 100 - f_HEV_sedan_yi) / (f_HEV[-1] - f_HEV[0])

        f_ICED_sedan_yi = self.fleet_data.loc[y0, 'f_' + 'ICED' + '_' + 'sedan' + self.pick_sources('fts')].values
        if f_ICED[-1] == f_ICED[0]:
            f_ICED_sedan = f_ICED_sedan_yi * np.ones(N-1).reshape(-1,1)
        else:
            f_ICED_sedan = f_ICED_sedan_yi + (f_ICED - f_ICED[0]) * (f_sedan_yf_dic['ICED'] / 100 - f_ICED_sedan_yi) / (f_ICED[-1] - f_ICED[0])

        f_ICEG_sedan = 1 - (f_BEV_sedan + f_PHEV_sedan + f_FCEV_sedan + f_HEV_sedan + f_ICED_sedan)
        f_BEV_LT_yi = self.fleet_data.loc[y0, 'f_' + 'BEV' + '_' + 'LT' + self.pick_sources('fts')].values
        if f_BEV[-1] == f_BEV[0]:
            f_BEV_LT = f_BEV_LT_yi * np.ones(N-1).reshape(-1,1)
        else:
            f_BEV_LT = f_BEV_LT_yi + (f_BEV - f_BEV[0]) * (f_LT_yf_dic['BEV'] / 100 - f_BEV_LT_yi) / (f_BEV[-1] - f_BEV[0])

        f_PHEV_LT_yi = self.fleet_data.loc[y0, 'f_' + 'PHEV' + '_' + 'LT' + self.pick_sources('fts')].values
        if f_PHEV[-1] == f_PHEV[0]:
            f_PHEV_LT = f_PHEV_LT_yi * np.ones(N-1).reshape(-1,1)
        else:
            f_PHEV_LT = f_PHEV_LT_yi + (f_PHEV - f_PHEV[0]) * (f_LT_yf_dic['PHEV'] / 100 - f_PHEV_LT_yi) / (f_PHEV[-1] - f_PHEV[0])

        f_FCEV_LT_yi = self.fleet_data.loc[y0, 'f_' + 'FCEV' + '_' + 'LT' + self.pick_sources('fts')].values
        if f_FCEV[-1] == f_FCEV[0]:
            f_FCEV_LT = f_FCEV_LT_yi * np.ones(N-1).reshape(-1,1)
        else:
            f_FCEV_LT = f_FCEV_LT_yi + (f_FCEV - f_FCEV[0]) * (f_LT_yf_dic['FCEV'] / 100 - f_FCEV_LT_yi) / (f_FCEV[-1] - f_FCEV[0])

        f_HEV_LT_yi = self.fleet_data.loc[y0, 'f_' + 'HEV' + '_' + 'LT' + self.pick_sources('fts')].values
        if f_HEV[-1] == f_HEV[0]:
            f_HEV_LT = f_HEV_LT_yi * np.ones(N-1).reshape(-1,1)
        else:
            f_HEV_LT = f_HEV_LT_yi + (f_HEV - f_HEV[0]) * (f_LT_yf_dic['HEV'] / 100 - f_HEV_LT_yi) / (f_HEV[-1] - f_HEV[0])

        f_ICED_LT_yi = self.fleet_data.loc[y0, 'f_' + 'ICED' + '_' + 'LT' + self.pick_sources('fts')].values
        if f_ICED[-1] == f_ICED[0]:
            f_ICED_LT = f_ICED_LT_yi * np.ones(N-1).reshape(-1,1)
        else:
            f_ICED_LT = f_ICED_LT_yi + (f_ICED - f_ICED[0]) * (f_LT_yf_dic['ICED'] / 100 - f_ICED_LT_yi) / (f_ICED[-1] - f_ICED[0])

        f_ICEG_LT = 1 - (f_BEV_LT + f_PHEV_LT + f_FCEV_LT + f_HEV_LT + f_ICED_LT)

        f_table = pd.DataFrame(
            {'f_BEV_sedan':f_BEV_sedan[:,0],
             'f_PHEV_sedan': f_PHEV_sedan[:,0],
             'f_FCEV_sedan': f_FCEV_sedan[:, 0],
             'f_HEV_sedan': f_HEV_sedan[:, 0],
             'f_ICED_sedan':f_ICED_sedan[:,0],
             'f_ICEG_sedan': f_ICEG_sedan[:, 0],
             'f_BEV_LT':f_BEV_LT[:,0],
             'f_PHEV_LT': f_PHEV_LT[:,0],
             'f_FCEV_LT': f_FCEV_LT[:, 0],
             'f_HEV_LT': f_HEV_LT[:, 0],
             'f_ICED_LT':f_ICED_LT[:,0],
             'f_ICEG_LT': f_ICEG_LT[:, 0]
            },
            index=np.arange(y0+1,yf+1)
        )

        f_table.fillna(0, inplace=True) 

        return f_table


    def computes_sales(self):


        sales = pd.DataFrame(index=np.arange(self.lowest_year, self.final_year + 1))
        population = pd.DataFrame(index=np.arange(self.lowest_year, self.final_year + 1))
        sales_per_pop = pd.DataFrame(index=np.arange(self.lowest_year, self.final_year + 1))
        F_LT = pd.DataFrame(index=np.arange(self.lowest_year, self.final_year + 1))
        pre_model_years = np.arange(self.lowest_year, self.baseline_year + 1)
        pre_population = self.fleet_data.loc[pre_model_years, 'pop' + self.pick_sources('population')]
        pre_sales_per_pop = self.fleet_data.loc[pre_model_years, 'Sp' + self.pick_sources('sales_per_driver')]
        total_sales_old = pre_sales_per_pop.mul(pre_population.values, axis = 1)

        bases = {'base_pop': pre_population.loc[self.baseline_year, :],
                 'base_spp': pre_sales_per_pop.loc[self.baseline_year, :]}

        model_years = np.arange(self.baseline_year + 1, self.final_year + 1)

        total_sales, pop_projection, sales_per_pop_projection = self.sales_total(bases['base_pop'], bases['base_spp'])
        population.loc[:, 'pop'] = np.concatenate((pre_population.values, pop_projection.values), axis=0)
        sales_per_pop.loc[:, 'spp'] = np.concatenate((pre_sales_per_pop.values, sales_per_pop_projection.values),
                                                     axis=0)
        if self.if_s_curve:
            self.f_s_curve_table = self.f_s_curve()

        for size_share, size in zip(self.size_share, self.sizes):

            for powertrain_size_share, powertrain in zip(self.powertrain_size_share[size],self.powertrains):

                pre_model_sales,f_default,F_default = self.powertrain_size_sales_defaults(
                    pre_model_years, size, powertrain, total_sales_old)
                bases = {'base_fts':f_default.loc[self.baseline_year, :].values,'base_Fs':F_default.loc[self.baseline_year, :].values}


                F_model,model_sales= self.powertrain_size_sales_model(bases,model_years,size,size_share,powertrain,
                                                                      powertrain_size_share, total_sales)

                column = 'S_' + powertrain + '_' + size
                sales.loc[:, column] = np.concatenate( (pre_model_sales.values, model_sales.values), axis=0 )

                if size == 'LT':
                    F_LT.loc[:, 'F_LT'] = np.concatenate((F_default.values, F_model.values), axis=0)

        return F_LT, sales, population, sales_per_pop

    def computes_stock(self, sales_ts, size):
        """

        :param sales_ts:
        :param size:
        :return:
        """
        years = np.arange(self.initial_year, self.final_year + 1)
        historical_years = np.arange(self.lowest_year, self.baseline_year + 1)
        model_years = np.arange(self.lowest_year, self.final_year + 1)
        stock_ts = pd.DataFrame(index=years, columns=['m_' + str(year) for year in model_years])
        half_life = pd.DataFrame(index=np.arange(self.lowest_year, self.final_year + 1))
        half_life_historical = self.fleet_data.loc[historical_years,'avg_a' + self.pick_sources('survival')]
        if self.car_longevity == "Static" or self.car_longevity == "User":
            base = half_life_historical.loc[self.baseline_year,:].values
        else:
            base = [1]
        half_life_future = self.projection(base, self.car_longevity,'avg_a_future_US_' + self.car_longevity,self.delta_hl)

        half_life.loc[:,'A'] = np.concatenate((half_life_historical.values,half_life_future.values),axis =0)

        self.cutoff_life = 50
        survival_defaults = pd.read_csv(PATH + 'age_defaults.csv',index_col=['age'])

        for model in model_years:
            model_half_life = half_life.loc[model, :].values
            model_sales = sales_ts[model]
            model_stock = stock_ts[f'm_{model}']

            data = {}

            for curr in years:
                a = curr - model

                if curr > self.baseline_year:
                    self.cutoff_life = 24

                if model > curr or a > self.cutoff_life:
                    data[curr] = 0
                else:
                    p = 1
                    if self.car_longevity == 'VIS20' and model > self.baseline_year:
                        p = survival_defaults.loc[a, f'Pa_{size}_{self.car_longevity}']
                    elif a >= 4:
                        p = math.exp(-math.log(2) * (a / model_half_life) ** 2)

                    data[curr] = model_sales * p

            stock_ts[f'm_{model}'].update(pd.Series(data=data, index=model_stock.index))

        return stock_ts

    def compute_fuel_prices(self, price_source):

        y_i = self.initial_year
        y_f = self.highest_year
        y_c = self.baseline_year 
        years = np.arange(y_i, y_f + 1)

        fuel_prices = pd.DataFrame(0, index=years,columns=['gasoline', 'biofuel', 'gas_bio', 'diesel', 'electricity', 'hydrogen'], dtype='float')
        vol_frac_biofuel = self.bio_frac_vol_y 

        if price_source == 'User':
            p_gas_c = self.fleet_data['hist_gasoline_price_' + self.region][y_c]
            p_dies_c = self.fleet_data['hist_diesel_price_' + self.region][y_c]
            p_elec_c = self.fleet_data['hist_electricity_price_' + self.region][y_c]
            p_h2_c = self.fleet_data['hist_hydrogen_price_' + self.region][y_c]
            p_bio_c = self.fleet_data['hist_biofuel_price_' + self.region][y_c] 
            p_gas_c = (p_gas_c - ( 0.1 * p_bio_c) ) / 0.9
            p_gas_f = p_gas_c * (1 + self.gasoline_price_change/100)
            p_dies_f = p_dies_c * (1 + self.diesel_price_change/100)
            p_elec_f = p_elec_c * (1 + self.electricity_price_change/100)
            p_h2_f = p_h2_c * (1 + self.h2_price_change/100)
            p_bio_f = p_bio_c * (1 + self.biofuel_price_change / 100)

            for y in years:

                if y <= y_c: 

                    fuel_prices['gasoline'][y] = ( self.fleet_data['hist_gasoline_price_' + self.region][y] ) / self.fleet_data['hist_CPI_' + self.region][y]
                    fuel_prices['biofuel'][y] = np.nan
                    fuel_prices['gas_bio'][y] = fuel_prices['gasoline'][y]
                    fuel_prices['diesel'][y] = ( self.fleet_data['hist_diesel_price_' + self.region][y] ) / self.fleet_data['hist_CPI_' + self.region][y]
                    fuel_prices['electricity'][y] = ( self.fleet_data['hist_electricity_price_' + self.region][y] ) / self.fleet_data['hist_CPI_' + self.region][y]
                    fuel_prices['hydrogen'][y] = ( self.fleet_data['hist_hydrogen_price_' + self.region][y] ) / self.fleet_data['hist_CPI_' + self.region][y]

                else: 

                    f_bio = vol_frac_biofuel.loc[y,'frac'] 
                    fuel_prices['gasoline'][y] = p_gas_c + (y-y_c)* (p_gas_f-p_gas_c)/(y_f-y_c)
                    fuel_prices['biofuel'][y] = p_bio_c + (y-y_c)* (p_bio_f-p_bio_c)/(y_f-y_c)
                    fuel_prices['gas_bio'][y] = ( p_gas_c + (y-y_c)* (p_gas_f-p_gas_c)/(y_f-y_c) )*(1-f_bio) + ( p_bio_c + (y-y_c)* (p_bio_f-p_bio_c)/(y_f-y_c) )*(f_bio)
                    fuel_prices['diesel'][y] = p_dies_c + (y-y_c)* (p_dies_f-p_dies_c)/(y_f-y_c)
                    fuel_prices['electricity'][y] = p_elec_c + (y-y_c)* (p_elec_f-p_elec_c)/(y_f-y_c)
                    fuel_prices['hydrogen'][y] = p_h2_c + (y-y_c)* (p_h2_f-p_h2_c)/(y_f-y_c)

            fuel_prices['biofuel'][y_c] = self.fleet_data['hist_biofuel_price_' + self.region][y_c]

        elif price_source == 'Static':

            for y in years:

                if y <= y_c: 

                    fuel_prices['gasoline'][y] = ( self.fleet_data['hist_gasoline_price_' + self.region][y] ) / self.fleet_data['hist_CPI_' + self.region][y]
                    fuel_prices['biofuel'][y] = np.nan
                    fuel_prices['gas_bio'][y] = fuel_prices['gasoline'][y]
                    fuel_prices['diesel'][y] = ( self.fleet_data['hist_diesel_price_' + self.region][y] ) / self.fleet_data['hist_CPI_' + self.region][y]
                    fuel_prices['electricity'][y] = ( self.fleet_data['hist_electricity_price_' + self.region][y] ) / self.fleet_data['hist_CPI_' + self.region][y]
                    fuel_prices['hydrogen'][y] = ( self.fleet_data['hist_hydrogen_price_' + self.region][y] ) / self.fleet_data['hist_CPI_' + self.region][y]

                else: 

                    f_bio = vol_frac_biofuel.loc[y, 'frac']  
                    fuel_prices['gasoline'][y] = self.fleet_data['hist_gasoline_price_' + self.region][y_c]
                    fuel_prices['biofuel'][y] = self.fleet_data['hist_biofuel_price_' + self.region][y_c]
                    fuel_prices['gas_bio'][y] = fuel_prices['gasoline'][y]*(1-f_bio) + fuel_prices['biofuel'][y]*(f_bio)
                    fuel_prices['diesel'][y] = self.fleet_data['hist_diesel_price_' + self.region][y_c]
                    fuel_prices['electricity'][y] = self.fleet_data['hist_electricity_price_' + self.region][y_c]
                    fuel_prices['hydrogen'][y] = self.fleet_data['hist_hydrogen_price_' + self.region][y_c]

            fuel_prices['biofuel'][y_c] = self.fleet_data['hist_biofuel_price_' + self.region][y_c]

        else:

            for y in years:

                if y <= y_c: 

                    fuel_prices['gasoline'][y] = ( self.fleet_data['hist_gasoline_price_' + self.region][y] ) / self.fleet_data['hist_CPI_' + self.region][y]
                    fuel_prices['biofuel'][y] = np.nan
                    fuel_prices['gas_bio'][y] = fuel_prices['gasoline'][y]
                    fuel_prices['diesel'][y] = ( self.fleet_data['hist_diesel_price_' + self.region][y] ) / self.fleet_data['hist_CPI_' + self.region][y]
                    fuel_prices['electricity'][y] = ( self.fleet_data['hist_electricity_price_' + self.region][y] ) / self.fleet_data['hist_CPI_' + self.region][y]
                    fuel_prices['hydrogen'][y] = ( self.fleet_data['hist_hydrogen_price_' + self.region][y] ) / self.fleet_data['hist_CPI_' + self.region][y]

                else: 

                    f_bio = vol_frac_biofuel.loc[y, 'frac']  
                    fuel_prices['gasoline'][y] = self.fleet_data[price_source + '_gasoline_price_' + self.region][y]
                    fuel_prices['biofuel'][y] = np.nan
                    fuel_prices['gas_bio'][y] = fuel_prices['gasoline'][y]
                    fuel_prices['diesel'][y] = self.fleet_data[price_source + '_diesel_price_' + self.region][y]
                    fuel_prices['electricity'][y] = self.fleet_data[price_source + '_electricity_price_' + self.region][y]
                    fuel_prices['hydrogen'][y] = self.fleet_data[price_source + '_hydrogen_price_' + self.region][y]

        return fuel_prices

    def compute_fuel_spend_dist(self,fuel_prices, fuel_dist, F_PHEV_corrected, calc_type):

        y_i = self.initial_year
        y_f = self.highest_year
        years = np.arange(y_i, y_f + 1)
        GG_kWh = self.GG_kWh_y 
        GD_kWh = (1/33.7) / 1.13
        kgH2_kWh = 1/33.3 

        if calc_type == 'sales':
            F_PHEV_e_sedan = F_PHEV_corrected['e_sales_sedan'].values
            F_PHEV_g_sedan = F_PHEV_corrected['g_sales_sedan'].values
            F_PHEV_e_LT = F_PHEV_corrected['e_sales_LT'].values
            F_PHEV_g_LT = F_PHEV_corrected['g_sales_LT'].values
        else:
            F_PHEV_e_sedan = F_PHEV_corrected['e_stock_sedan'].values
            F_PHEV_g_sedan = F_PHEV_corrected['g_stock_sedan'].values
            F_PHEV_e_LT = F_PHEV_corrected['e_stock_LT'].values
            F_PHEV_g_LT = F_PHEV_corrected['g_stock_LT'].values


        fuel_spend_dist = pd.DataFrame(0, index=years, columns=['ICEG_sedan','ICED_sedan','HEV_sedan','PHEV_sedan','BEV_sedan','FCEV_sedan','ICEG_LT','ICED_LT','HEV_LT','PHEV_LT','BEV_LT','FCEV_LT','ICEG_all','ICED_all','HEV_all','PHEV_all','BEV_all','FCEV_all'], dtype='float')

        fuel_spend_dist['ICEG_sedan'] = ( fuel_prices['gas_bio'].multiply(fuel_dist['ICEG']['sedan']) ).multiply(GG_kWh['GG_kWh'])
        fuel_spend_dist['ICED_sedan'] = fuel_prices['diesel'].multiply(fuel_dist['ICED']['sedan']) * GD_kWh
        fuel_spend_dist['HEV_sedan'] = ( fuel_prices['gas_bio'].multiply(fuel_dist['HEV']['sedan']) ).multiply(GG_kWh['GG_kWh'])
        fuel_spend_dist['BEV_sedan'] = fuel_prices['electricity'].multiply(fuel_dist['BEV']['sedan'])
        fuel_spend_dist['FCEV_sedan'] = fuel_prices['hydrogen'].multiply(fuel_dist['FCEV']['sedan']) * kgH2_kWh

        fuel_spend_dist['PHEV_sedan'] = ( fuel_prices['electricity'].multiply(F_PHEV_e_sedan) + fuel_prices['gas_bio'].multiply(F_PHEV_g_sedan) ).multiply(GG_kWh['GG_kWh'])


        fuel_spend_dist['ICEG_LT'] = ( fuel_prices['gas_bio'].multiply(fuel_dist['ICEG']['LT']) ).multiply(GG_kWh['GG_kWh'])
        fuel_spend_dist['ICED_LT'] = fuel_prices['diesel'].multiply(fuel_dist['ICED']['LT']) * GD_kWh
        fuel_spend_dist['HEV_LT'] = ( fuel_prices['gas_bio'].multiply(fuel_dist['HEV']['LT']) ).multiply(GG_kWh['GG_kWh'])
        fuel_spend_dist['BEV_LT'] = fuel_prices['electricity'].multiply(fuel_dist['BEV']['LT'])
        fuel_spend_dist['FCEV_LT'] = fuel_prices['hydrogen'].multiply(fuel_dist['FCEV']['LT']) * kgH2_kWh

        fuel_spend_dist['PHEV_LT'] = fuel_prices['electricity'].multiply(F_PHEV_e_LT) + ( fuel_prices['gas_bio'].multiply(F_PHEV_g_LT) ).multiply(GG_kWh['GG_kWh'])


        if calc_type == 'stock':
            fuel_spend_dist['ICEG_all'] = ( fuel_prices['gas_bio'].multiply(fuel_dist['ICEG']['all']) ).multiply(GG_kWh['GG_kWh'])
            fuel_spend_dist['ICED_all'] = fuel_prices['diesel'].multiply(fuel_dist['ICED']['all']) * GD_kWh
            fuel_spend_dist['HEV_all'] = ( fuel_prices['gas_bio'].multiply(fuel_dist['HEV']['all']) ).multiply(GG_kWh['GG_kWh'])
            fuel_spend_dist['BEV_all'] = fuel_prices['electricity'].multiply(fuel_dist['BEV']['all'])
            fuel_spend_dist['FCEV_all'] = fuel_prices['hydrogen'].multiply(fuel_dist['FCEV']['all']) * kgH2_kWh
        else:
            fuel_spend_dist['ICEG_all'] = ( fuel_prices['gas_bio'].multiply(fuel_dist['ICEG/all']) ).multiply(GG_kWh['GG_kWh'])
            fuel_spend_dist['ICED_all'] = fuel_prices['diesel'].multiply(fuel_dist['ICED/all']) * GD_kWh
            fuel_spend_dist['HEV_all'] = ( fuel_prices['gas_bio'].multiply(fuel_dist['HEV/all']) ).multiply(GG_kWh['GG_kWh'])
            fuel_spend_dist['BEV_all'] = fuel_prices['electricity'].multiply(fuel_dist['BEV/all'])
            fuel_spend_dist['FCEV_all'] = fuel_prices['hydrogen'].multiply(fuel_dist['FCEV/all']) * kgH2_kWh


        fuel_spend_dist = fuel_spend_dist.replace(0, np.nan)

        return fuel_spend_dist

    ''' OLD SALES SPEND CALCULATION -- don't delete
    def compute_sales_spend(self, sales):

        y_i = self.initial_year
        y_f = self.highest_year
        y_c = self.baseline_year  
        years = np.arange(y_i, y_f + 1)

        sales_spend_pt = pd.DataFrame(1,index=years, columns = self.powertrains)
        single_sedan_prices = pd.DataFrame(1, index=years, columns=self.powertrains)
        single_LT_prices = pd.DataFrame(1,index=years, columns = self.powertrains)

        for pt in self.powertrains:

            p_m0_sedan = self.fleet_data['p_m0_' + pt + '_sedan'][y_c]
            p_n0_sedan = self.fleet_data['p_n0_' + pt + '_sedan'][y_c]
            p_m0_LT = self.fleet_data['p_m0_' + pt + '_LT'][y_c]
            p_n0_LT = self.fleet_data['p_n0_' + pt + '_LT'][y_c]

            for y in years:

                if y <= y_c:

                    hist_p_pt_sedan = self.fleet_data['hist_price_' + pt + '_sedan'][y]  /  self.fleet_data['hist_CPI_' + self.region][y]
                    hist_p_pt_LT = self.fleet_data['hist_price_' + pt + '_LT'][y]  /  self.fleet_data['hist_CPI_' + self.region][y]
                    sales_spend_pt.loc[y, pt] = sales['S_' + pt + '_sedan'][y] * (hist_p_pt_sedan) + sales['S_' + pt + '_LT'][y] * (hist_p_pt_LT)

                    single_sedan_prices.loc[y,pt] = hist_p_pt_sedan
                    single_LT_prices.loc[y, pt] = hist_p_pt_LT

                else:

                    p_m_sedan = p_m0_sedan
                    p_m_LT = p_m0_LT

                    pt_y_sedan_sales = sales['S_' + pt + '_sedan'][y]
                    pt_yc_sedan_sales =sales['S_' + pt + '_sedan'][y_c]
                    if pt_yc_sedan_sales == 0:
                        pn_pn0_sedan = np.nan
                    elif pt_y_sedan_sales == 0:
                        pn_pn0_sedan = 0
                    else:
                        pn_pn0_sedan = ( pt_y_sedan_sales / pt_yc_sedan_sales )**(-0.32)


                    pt_y_LT_sales = sales['S_' + pt + '_LT'][y]
                    pt_yc_LT_sales = sales['S_' + pt + '_LT'][y_c]
                    if pt_yc_LT_sales == 0:
                        pn_pn0_LT = np.nan
                    elif pt_y_LT_sales == 0:
                        pn_pn0_LT = 0
                    else:
                        pn_pn0_LT = (pt_y_LT_sales / pt_yc_LT_sales ) ** (-0.32)

                    sales_spend_pt.loc[y,pt] = sales['S_' + pt + '_sedan'][y] * (p_m_sedan + p_n0_sedan * pn_pn0_sedan) + sales['S_' + pt + '_LT'][y] * (p_m_LT + p_n0_LT * pn_pn0_LT)

                    single_sedan_prices.loc[y, pt] = p_m_sedan + p_n0_sedan * pn_pn0_sedan
                    single_LT_prices.loc[y, pt] = p_m_LT + p_n0_LT * pn_pn0_LT

        sales_spend_pt = sales_spend_pt / 1000000000

        sales_spend_pt = sales_spend_pt.replace(np.nan, 0)

        return sales_spend_pt, single_sedan_prices, single_LT_prices
    '''

    def compute_sales_spend(self, sales):

        y_i = self.initial_year
        y_f = self.highest_year
        y_c = self.baseline_year  
        years = np.arange(y_i, y_f + 1)

        sales_spend_pt = pd.DataFrame(1, index=years, columns=self.powertrains)
        single_sedan_prices = pd.DataFrame(1, index=years, columns=self.powertrains)
        single_LT_prices = pd.DataFrame(1, index=years, columns=self.powertrains)
        for pt in self.powertrains:

            p_m0_sedan = self.fleet_data['p_m0_' + pt + '_sedan'][y_c]
            p_n0_sedan = self.fleet_data['p_n0_' + pt + '_sedan'][y_c]
            p_m0_LT = self.fleet_data['p_m0_' + pt + '_LT'][y_c]
            p_n0_LT = self.fleet_data['p_n0_' + pt + '_LT'][y_c]

            for y in np.arange(y_i, y_c + 1):
                hist_p_pt_sedan = self.fleet_data['hist_price_' + pt + '_sedan'][y] / self.fleet_data['hist_CPI_' + self.region][y]
                hist_p_pt_LT = self.fleet_data['hist_price_' + pt + '_LT'][y] / self.fleet_data['hist_CPI_' + self.region][y]
                sales_spend_pt.loc[y, pt] = sales['S_' + pt + '_sedan'][y] * (hist_p_pt_sedan) + sales['S_' + pt + '_LT'][y] * (hist_p_pt_LT)

                single_sedan_prices.loc[y, pt] = hist_p_pt_sedan
                single_LT_prices.loc[y, pt] = hist_p_pt_LT


        for pt in self.powertrains:

            if pt == 'BEV':

                y_p = float(self.yp_BEV)
                year = np.arange(y_c,y_p+1)

                yc_sedan_price = single_sedan_prices.loc[y_c, 'BEV']
                yp_sedan_price = single_sedan_prices.loc[y_c, 'ICEG']
                single_sedan_prices.loc[y_c:y_p, pt] = yc_sedan_price + (year-y_c)*(yp_sedan_price - yc_sedan_price)/(y_p-y_c)
                single_sedan_prices.loc[y_p+1:y_f, pt] = yp_sedan_price

                yc_LT_price = single_LT_prices.loc[y_c, 'BEV']
                yp_LT_price = single_LT_prices.loc[y_c, 'ICEG']
                single_LT_prices.loc[y_c:y_p, pt] = yc_LT_price + (year - y_c) * (yp_LT_price - yc_LT_price) / (y_p - y_c)
                single_LT_prices.loc[y_p + 1:y_f, pt] = yp_LT_price

                sales_spend_pt.loc[y_c + 1:y_f, pt] = sales['S_' + pt + '_sedan'].loc[y_c + 1:y_f].multiply(single_sedan_prices[pt].loc[y_c + 1:y_f]) + sales['S_' + pt + '_LT'].loc[y_c + 1:y_f].multiply(single_LT_prices[pt].loc[y_c + 1:y_f])


            elif pt == 'FCEV':

                y_p = float(self.yp_FCEV)
                year = np.arange(y_c,y_p+1)

                yc_sedan_price = single_sedan_prices.loc[y_c, 'FCEV']
                yp_sedan_price = single_sedan_prices.loc[y_c, 'ICEG']
                single_sedan_prices.loc[y_c:y_p, pt] = yc_sedan_price + (year-y_c)*(yp_sedan_price - yc_sedan_price)/(y_p-y_c)
                single_sedan_prices.loc[y_p+1:y_f, pt] = yp_sedan_price

                yc_LT_price = single_LT_prices.loc[y_c, 'FCEV']
                yp_LT_price = single_LT_prices.loc[y_c, 'ICEG']
                single_LT_prices.loc[y_c:y_p, pt] = yc_LT_price + (year - y_c) * (yp_LT_price - yc_LT_price) / (y_p - y_c)
                single_LT_prices.loc[y_p + 1:y_f, pt] = yp_LT_price

                sales_spend_pt.loc[y_c + 1:y_f, pt] = sales['S_' + pt + '_sedan'].loc[y_c + 1:y_f].multiply(single_sedan_prices[pt].loc[y_c + 1:y_f]) + sales['S_' + pt + '_LT'].loc[y_c + 1:y_f].multiply(single_LT_prices[pt].loc[y_c + 1:y_f])

            else:
                single_sedan_prices.loc[y_c:y_f, pt] = single_sedan_prices.loc[y_c, pt]
                single_LT_prices.loc[y_c:y_f, pt] = single_LT_prices.loc[y_c, pt]
                sales_spend_pt.loc[y_c+1:y_f, pt] = sales['S_' + pt + '_sedan'].loc[y_c+1:y_f].multiply(single_sedan_prices[pt].loc[y_c+1:y_f]) + sales['S_' + pt + '_LT'].loc[y_c+1:y_f].multiply(single_LT_prices[pt].loc[y_c+1:y_f])

            '''
                else:

                    p_m_sedan = p_m0_sedan
                    p_m_LT = p_m0_LT

                    pt_y_sedan_sales = sales['S_' + pt + '_sedan'][y]
                    pt_yc_sedan_sales = sales['S_' + pt + '_sedan'][y_c]
                    if pt_yc_sedan_sales == 0:
                        pn_pn0_sedan = np.nan
                    elif pt_y_sedan_sales == 0:
                        pn_pn0_sedan = 0
                    else:
                        pn_pn0_sedan = (pt_y_sedan_sales / pt_yc_sedan_sales) ** (-0.32)

                    pt_y_LT_sales = sales['S_' + pt + '_LT'][y]
                    pt_yc_LT_sales = sales['S_' + pt + '_LT'][y_c]
                    if pt_yc_LT_sales == 0:
                        pn_pn0_LT = np.nan
                    elif pt_y_LT_sales == 0:
                        pn_pn0_LT = 0
                    else:
                        pn_pn0_LT = (pt_y_LT_sales / pt_yc_LT_sales) ** (-0.32)

                    sales_spend_pt.loc[y, pt] = sales['S_' + pt + '_sedan'][y] * (p_m_sedan + p_n0_sedan * pn_pn0_sedan) + sales['S_' + pt + '_LT'][y] * (p_m_LT + p_n0_LT * pn_pn0_LT)

                    single_sedan_prices.loc[y, pt] = p_m_sedan + p_n0_sedan * pn_pn0_sedan
                    single_LT_prices.loc[y, pt] = p_m_LT + p_n0_LT * pn_pn0_LT
            '''

        sales_spend_pt = sales_spend_pt / 1000000000

        sales_spend_pt = sales_spend_pt.replace(np.nan, 0)

        return sales_spend_pt, single_sedan_prices, single_LT_prices

    def compute_maint_costs(self, d_car_pt_s):

        y_i = self.initial_year
        y_f = self.highest_year
        years = np.arange(y_i, y_f + 1)
        cost_dist_sedan = {'ICEG': 0.0636,'ICED': 0.0636,'HEV': 0.0647,'PHEV': 0.0639,'BEV': 0.0276,'FCEV': 0.0647}
        cost_dist_LT = {'ICEG': 0.0636,'ICED': 0.0636,'HEV': 0.0647,'PHEV': 0.0639,'BEV': 0.0276,'FCEV': 0.0647}

        cost_pt_s = pd.DataFrame(0, index=years, columns=['ICEG_sedan', 'ICED_sedan', 'HEV_sedan', 'PHEV_sedan', 'BEV_sedan', 'FCEV_sedan', 'ICEG_LT', 'ICED_LT', 'HEV_LT', 'PHEV_LT', 'BEV_LT','FCEV_LT'])
        cost_pt = pd.DataFrame(0, index=years, columns=['ICEG', 'ICED', 'HEV', 'PHEV', 'BEV', 'FCEV'])

        for pt in self.powertrains:

            cost_pt_s[pt + '_sedan'] = cost_dist_sedan[pt] * d_car_pt_s.loc[y_i:y_f, pt + '_sedan']
            cost_pt_s[pt + '_LT'] = cost_dist_LT[pt] * d_car_pt_s.loc[y_i:y_f, pt + '_LT']
            cost_pt[pt] =  cost_pt_s[pt + '_sedan'] + cost_pt_s[pt + '_LT']

        cost_total = cost_pt_s.sum(axis=1)

        return cost_pt_s, cost_pt, cost_total

    def single_car_spend_dist(self, lifetime, d_car, d_cum, fuel_dist_sales, fuel_prices, single_sedan_prices, single_LT_prices, F_PHEV_corrected):

        yf_2020 = 2020 + lifetime - 1
        yf_2030 = 2030 + lifetime - 1

        emissions_indices = ['car', 'fuel', 'maintenance']
        costs_sedan_2020 = pd.DataFrame(0, index=emissions_indices, columns=self.powertrains, dtype='float' )
        costs_LT_2020 = pd.DataFrame(0, index=emissions_indices, columns=self.powertrains, dtype='float')
        costs_sedan_2030 = pd.DataFrame(0, index=emissions_indices, columns=self.powertrains, dtype='float')
        costs_LT_2030 = pd.DataFrame(0, index=emissions_indices, columns=self.powertrains, dtype='float')
        d_y_2020 = d_car.loc[2020:yf_2020, 'm_2020']
        d_y_2030 = d_car.loc[2030:yf_2030, 'm_2030']
        d_cum_2020 = d_cum['m_2020'].loc[yf_2020]
        d_cum_2030 = d_cum['m_2030'].loc[yf_2030]
        fuel_prices_2020 = fuel_prices.loc[2020:yf_2020,:]
        fuel_prices_2030 = fuel_prices.loc[2030:yf_2030, :]
        maint_cost_dist_sedan = {'ICEG': 0.0636, 'ICED': 0.0636, 'HEV': 0.0647, 'PHEV': 0.0639, 'BEV': 0.0276, 'FCEV': 0.0647}
        maint_cost_dist_LT = {'ICEG': 0.0636, 'ICED': 0.0636, 'HEV': 0.0647, 'PHEV': 0.0639, 'BEV': 0.0276, 'FCEV': 0.0647}
        GG_kWh = self.GG_kWh_y 
        GD_kWh = (1 / 33.7) / 1.13
        kgH2_kWh = (1 / 33.3)
        F_PHEV_e_sedan_20 = F_PHEV_corrected['e_sales_sedan'][2020]
        F_PHEV_g_sedan_20 = F_PHEV_corrected['g_sales_sedan'][2020]
        F_PHEV_e_LT_20 = F_PHEV_corrected['e_sales_LT'][2020]
        F_PHEV_g_LT_20 = F_PHEV_corrected['g_sales_LT'][2020]

        F_PHEV_e_sedan_30 = F_PHEV_corrected['e_sales_sedan'][2030]
        F_PHEV_g_sedan_30 = F_PHEV_corrected['g_sales_sedan'][2030]
        F_PHEV_e_LT_30 = F_PHEV_corrected['e_sales_LT'][2030]
        F_PHEV_g_LT_30 = F_PHEV_corrected['g_sales_LT'][2030]
        costs_sedan_2020['ICEG']['fuel'] = (( d_y_2020.multiply(GG_kWh.loc[2020:yf_2020, 'GG_kWh']) * fuel_dist_sales['ICEG']['sedan'][2020]).dot(fuel_prices_2020['gasoline'])) / d_cum_2020
        costs_sedan_2020['ICED']['fuel'] = ( (d_y_2020 * fuel_dist_sales['ICED']['sedan'][2020]).dot(fuel_prices_2020['diesel']) ) * GD_kWh/ d_cum_2020
        costs_sedan_2020['HEV']['fuel'] = ( (d_y_2020.multiply(GG_kWh.loc[2020:yf_2020, 'GG_kWh']) * fuel_dist_sales['HEV']['sedan'][2020]).dot(fuel_prices_2020['gasoline']) ) / d_cum_2020
        costs_sedan_2020['BEV']['fuel'] = ( (d_y_2020 * fuel_dist_sales['BEV']['sedan'][2020]).dot(fuel_prices_2020['electricity']) ) / d_cum_2020
        costs_sedan_2020['FCEV']['fuel'] = ( (d_y_2020 * fuel_dist_sales['HEV']['sedan'][2020]).dot(fuel_prices_2020['hydrogen']) ) * kgH2_kWh/ d_cum_2020
        costs_sedan_2020['PHEV']['fuel'] = ( (d_y_2020 * F_PHEV_e_sedan_20).dot(fuel_prices_2020['electricity']) + (d_y_2020.multiply(GG_kWh.loc[2020:yf_2020, 'GG_kWh']) * F_PHEV_g_sedan_20).dot(fuel_prices_2020['gasoline']) ) / d_cum_2020

        costs_LT_2020['ICEG']['fuel'] = ((d_y_2020.multiply(GG_kWh.loc[2020:yf_2020, 'GG_kWh']) * fuel_dist_sales['ICEG']['LT'][2020]).dot(fuel_prices_2020['gasoline'])) / d_cum_2020
        costs_LT_2020['ICED']['fuel'] = ((d_y_2020 * fuel_dist_sales['ICED']['LT'][2020]).dot(fuel_prices_2020['diesel'])) * GD_kWh / d_cum_2020
        costs_LT_2020['HEV']['fuel'] = ((d_y_2020.multiply(GG_kWh.loc[2020:yf_2020, 'GG_kWh']) * fuel_dist_sales['HEV']['LT'][2020]).dot(fuel_prices_2020['gasoline'])) / d_cum_2020
        costs_LT_2020['BEV']['fuel'] = ((d_y_2020 * fuel_dist_sales['BEV']['LT'][2020]).dot(fuel_prices_2020['electricity'])) / d_cum_2020
        costs_LT_2020['FCEV']['fuel'] = ((d_y_2020 * fuel_dist_sales['HEV']['LT'][2020]).dot(fuel_prices_2020['hydrogen'])) * kgH2_kWh / d_cum_2020
        costs_LT_2020['PHEV']['fuel'] = ((d_y_2020 * F_PHEV_e_LT_20).dot(fuel_prices_2020['electricity']) + (d_y_2020.multiply(GG_kWh.loc[2020:yf_2020, 'GG_kWh']) * F_PHEV_g_LT_20).dot(fuel_prices_2020['gasoline']) ) / d_cum_2020
        costs_sedan_2030['ICEG']['fuel'] = ((d_y_2030.multiply(GG_kWh.loc[2030:yf_2030, 'GG_kWh']) * fuel_dist_sales['ICEG']['sedan'][2030]).dot(fuel_prices_2030['gasoline'])) / d_cum_2030
        costs_sedan_2030['ICED']['fuel'] = ((d_y_2030 * fuel_dist_sales['ICED']['sedan'][2030]).dot(fuel_prices_2030['diesel'])) * GD_kWh / d_cum_2030
        costs_sedan_2030['HEV']['fuel'] = ((d_y_2030.multiply(GG_kWh.loc[2030:yf_2030, 'GG_kWh']) * fuel_dist_sales['HEV']['sedan'][2030]).dot(fuel_prices_2030['gasoline'])) / d_cum_2030
        costs_sedan_2030['BEV']['fuel'] = ((d_y_2030 * fuel_dist_sales['BEV']['sedan'][2030]).dot(fuel_prices_2030['electricity'])) / d_cum_2030
        costs_sedan_2030['FCEV']['fuel'] = ((d_y_2030 * fuel_dist_sales['HEV']['sedan'][2030]).dot(fuel_prices_2030['hydrogen'])) * kgH2_kWh / d_cum_2030
        costs_sedan_2030['PHEV']['fuel'] = ((d_y_2030 * F_PHEV_e_sedan_30).dot(fuel_prices_2030['electricity']) + (d_y_2030.multiply(GG_kWh.loc[2030:yf_2030, 'GG_kWh']) * F_PHEV_g_sedan_30).dot(fuel_prices_2030['gasoline']) ) / d_cum_2030

        costs_LT_2030['ICEG']['fuel'] = ((d_y_2030.multiply(GG_kWh.loc[2030:yf_2030, 'GG_kWh']) * fuel_dist_sales['ICEG']['LT'][2030]).dot(fuel_prices_2030['gasoline'])) / d_cum_2030
        costs_LT_2030['ICED']['fuel'] = ((d_y_2030 * fuel_dist_sales['ICED']['LT'][2030]).dot(fuel_prices_2030['diesel'])) * GD_kWh / d_cum_2030
        costs_LT_2030['HEV']['fuel'] = ((d_y_2030.multiply(GG_kWh.loc[2030:yf_2030, 'GG_kWh']) * fuel_dist_sales['HEV']['LT'][2030]).dot(fuel_prices_2030['gasoline'])) / d_cum_2030
        costs_LT_2030['BEV']['fuel'] = ((d_y_2030 * fuel_dist_sales['BEV']['LT'][2030]).dot(fuel_prices_2030['electricity'])) / d_cum_2030
        costs_LT_2030['FCEV']['fuel'] = ((d_y_2030 * fuel_dist_sales['HEV']['LT'][2030]).dot(fuel_prices_2030['hydrogen'])) * kgH2_kWh / d_cum_2030
        costs_LT_2030['PHEV']['fuel'] = ((d_y_2030 * F_PHEV_e_LT_30).dot(fuel_prices_2030['electricity']) + (d_y_2030.multiply(GG_kWh.loc[2030:yf_2030, 'GG_kWh']) * F_PHEV_g_LT_30).dot(fuel_prices_2030['gasoline'])) / d_cum_2030
        for pt in self.powertrains:

            costs_sedan_2020[pt]['car'] = single_sedan_prices.loc[2020,pt] / d_cum_2020
            costs_sedan_2030[pt]['car'] = single_sedan_prices.loc[2030,pt] / d_cum_2030
            costs_LT_2020[pt]['car'] = single_LT_prices.loc[2020, pt] / d_cum_2020
            costs_LT_2030[pt]['car'] = single_LT_prices.loc[2030, pt] / d_cum_2030

            costs_sedan_2020[pt]['maintenance'] = maint_cost_dist_sedan[pt]
            costs_sedan_2030[pt]['maintenance'] =  maint_cost_dist_sedan[pt]
            costs_LT_2020[pt]['maintenance'] =  maint_cost_dist_LT[pt]
            costs_LT_2030[pt]['maintenance'] =  maint_cost_dist_LT[pt]

        return costs_sedan_2020, costs_LT_2020, costs_sedan_2030, costs_LT_2030

    def lifecycle_e_per_d(self, lifetime, d_car, d_cum, fleet_data, fuel_dist_new, I_grid):

        emissions_defaults = pd.read_csv(PATH + 'emission_intensity_defaults.csv', index_col=['fuel'])

        yf_2020 = 2020 + lifetime - 1
        yf_2030 = 2030 + lifetime - 1
        emissions_indices = ['tailpipe', 'fuel production', 'car production']
        e_sedan_2020 = pd.DataFrame(0, index=emissions_indices, columns=self.powertrains)
        e_LT_2020 = pd.DataFrame(0, index=emissions_indices, columns=self.powertrains)
        e_avg_2020 = pd.DataFrame(0, index=emissions_indices, columns=self.powertrains)
        e_sedan_2030 = pd.DataFrame(0, index=emissions_indices, columns=self.powertrains)
        e_LT_2030 = pd.DataFrame(0, index=emissions_indices, columns=self.powertrains)
        e_avg_2030 = pd.DataFrame(0, index=emissions_indices, columns=self.powertrains)
        d_y_2020 = d_car.loc[2020:yf_2020,'m_2020']
        d_y_2030 = d_car.loc[2030:yf_2030, 'm_2030']
        d_cum_2020 = d_cum['m_2020'].loc[yf_2020]
        d_cum_2030 = d_cum['m_2030'].loc[yf_2030]

        for pt in self.powertrains:
            I_2020_2014 = I_grid.loc[2020, 'I'] / I_grid.loc[2014, 'I']
            e_sedan_2020[pt]['car production'] = I_2020_2014 * fleet_data.loc[2020,'CPE_'+ pt +'_sedan'] * (10**6) / d_cum_2020
            e_LT_2020[pt]['car production'] = I_2020_2014 * fleet_data.loc[2020,'CPE_'+ pt +'_LT'] * (10**6) / d_cum_2020
            if (pt == 'BEV') | (pt == 'FCEV'):
                e_sedan_2020[pt]['tailpipe'] = 0
                e_LT_2020[pt]['tailpipe'] = 0
            elif pt == 'PHEV':
                I_1 = 0 
                I_2 =  self.I_TP_pt_y['PHEVf'] 
                I = (I_1 * self.mode / 100) + (I_2 * (1 - self.mode / 100))
                e_sedan_2020[pt]['tailpipe'] = I.loc[2020:yf_2020].dot( fuel_dist_new[pt]['sedan'].loc[2020] * d_y_2020.loc[2020:yf_2020] ) / d_cum_2020
                e_LT_2020[pt]['tailpipe'] = I.loc[2020:yf_2020].dot( fuel_dist_new[pt]['LT'].loc[2020] * d_y_2020.loc[2020:yf_2020] ) / d_cum_2020
            else:
                I = self.I_TP_pt_y[pt]
                e_sedan_2020[pt]['tailpipe'] = I.loc[2020:yf_2020].dot( fuel_dist_new[pt]['sedan'].loc[2020] * d_y_2020.loc[2020:yf_2020] ) / d_cum_2020
                e_LT_2020[pt]['tailpipe'] = I.loc[2020:yf_2020].dot( fuel_dist_new[pt]['LT'].loc[2020] * d_y_2020.loc[2020:yf_2020] ) / d_cum_2020
            if (pt == 'BEV'):
                I = I_grid.loc[2020:yf_2020, 'I']
                e_dist_sedan = I * fuel_dist_new[pt]['sedan'].loc[2020]
                e_dist_LT = I * fuel_dist_new[pt]['LT'].loc[2020]
                e_sedan_2020[pt]['fuel production'] = e_dist_sedan.multiply(d_y_2020, axis=0).sum(axis=0) / d_cum_2020
                e_LT_2020[pt]['fuel production'] = e_dist_LT.multiply(d_y_2020, axis=0).sum(axis=0) / d_cum_2020
            elif (pt == 'FCEV'):
                if self.h2_prod == 'SMR':
                    lookup = 'FCEV_SMR'
                elif self.h2_prod == 'SMR with carbon capture':
                    lookup = 'FCEV_SMR_CC'
                else:
                    lookup = 'FCEV_elect'
                I = self.I_CFP_pt_y[lookup] 
                e_sedan_2020[pt]['fuel production'] = I.loc[2020:yf_2020].dot(fuel_dist_new[pt]['sedan'].loc[2020] * d_y_2020.loc[2020:yf_2020]) / d_cum_2020
                e_LT_2020[pt]['fuel production'] = I.loc[2020:yf_2020].dot(fuel_dist_new[pt]['LT'].loc[2020] * d_y_2020.loc[2020:yf_2020]) / d_cum_2020
            elif pt == 'PHEV':
                I_1 = I_grid.loc[2020:yf_2020, 'I']
                I_2 = self.I_CFP_pt_y['PHEVf'] 
                I = (I_1 * self.mode / 100) + (I_2 * (1 - self.mode / 100))
                e_sedan_2020[pt]['fuel production'] = I.loc[2020:yf_2020].dot(fuel_dist_new[pt]['sedan'].loc[2020] * d_y_2020.loc[2020:yf_2020]) / d_cum_2020
                e_LT_2020[pt]['fuel production'] = I.loc[2020:yf_2020].dot(fuel_dist_new[pt]['LT'].loc[2020] * d_y_2020.loc[2020:yf_2020]) / d_cum_2020
            else:
                I = self.I_CFP_pt_y[pt]
                e_sedan_2020[pt]['fuel production'] = I.loc[2020:yf_2020].dot(fuel_dist_new[pt]['sedan'].loc[2020] * d_y_2020.loc[2020:yf_2020]) / d_cum_2020
                e_LT_2020[pt]['fuel production'] = I.loc[2020:yf_2020].dot(fuel_dist_new[pt]['LT'].loc[2020] * d_y_2020.loc[2020:yf_2020]) / d_cum_2020
            I_2030_2014 = I_grid.loc[2030, 'I'] / I_grid.loc[2014, 'I']
            e_sedan_2030[pt]['car production'] = I_2030_2014 * fleet_data.loc[2030,'CPE_'+ pt +'_sedan'] * (10**6) / d_cum_2030
            e_LT_2030[pt]['car production'] = I_2030_2014 * fleet_data.loc[2030,'CPE_'+ pt +'_LT'] * (10**6) / d_cum_2030
            if (pt == 'BEV') | (pt == 'FCEV'):
                e_sedan_2030[pt]['tailpipe'] = 0
                e_LT_2030[pt]['tailpipe'] = 0
            elif pt == 'PHEV':
                I_1 = 0 
                I_2 =  self.I_TP_pt_y['PHEVf'] 
                I = (I_1 * self.mode / 100) + (I_2 * (1 - self.mode / 100))
                e_sedan_2030[pt]['tailpipe'] = I.loc[2030:yf_2030].dot( fuel_dist_new[pt]['sedan'].loc[2030] * d_y_2030.loc[2030:yf_2030] ) / d_cum_2030
                e_LT_2030[pt]['tailpipe'] = I.loc[2030:yf_2030].dot( fuel_dist_new[pt]['LT'].loc[2030] * d_y_2030.loc[2030:yf_2030] ) / d_cum_2030
            else:
                I = self.I_TP_pt_y[pt]
                e_sedan_2030[pt]['tailpipe'] = I.loc[2030:yf_2030].dot( fuel_dist_new[pt]['sedan'].loc[2030] * d_y_2030.loc[2030:yf_2030] ) / d_cum_2030
                e_LT_2030[pt]['tailpipe'] = I.loc[2030:yf_2030].dot( fuel_dist_new[pt]['LT'].loc[2030] * d_y_2030.loc[2030:yf_2030] ) / d_cum_2030
            if (pt == 'BEV'):
                I = I_grid.loc[2030:yf_2030, 'I']
                e_dist_sedan = I * fuel_dist_new[pt]['sedan'].loc[2030]
                e_dist_LT = I * fuel_dist_new[pt]['LT'].loc[2030]
                e_sedan_2030[pt]['fuel production'] = e_dist_sedan.multiply(d_y_2030, axis=0).sum(axis=0) / d_cum_2030
                e_LT_2030[pt]['fuel production'] = e_dist_LT.multiply(d_y_2030, axis=0).sum(axis=0) / d_cum_2030
            elif (pt == 'FCEV'):
                if self.h2_prod == 'SMR':
                    lookup = 'FCEV_SMR'
                elif self.h2_prod == 'SMR with carbon capture':
                    lookup = 'FCEV_SMR_CC'
                else:
                    lookup = 'FCEV_elect'
                I = self.I_CFP_pt_y[lookup] 
                e_sedan_2030[pt]['fuel production'] = I.loc[2030:yf_2030].dot(fuel_dist_new[pt]['sedan'].loc[2030] * d_y_2030.loc[2030:yf_2030]) / d_cum_2030
                e_LT_2030[pt]['fuel production'] = I.loc[2030:yf_2030].dot(fuel_dist_new[pt]['LT'].loc[2030] * d_y_2030.loc[2030:yf_2030]) / d_cum_2030
            elif pt == 'PHEV':
                I_1 = I_grid.loc[2030:yf_2030, 'I']
                I_2 = self.I_CFP_pt_y['PHEVf'] 
                I = (I_1 * self.mode / 100) + (I_2 * (1 - self.mode / 100))
                e_sedan_2030[pt]['fuel production'] = I.loc[2030:yf_2030].dot(fuel_dist_new[pt]['sedan'].loc[2030] * d_y_2030.loc[2030:yf_2030]) / d_cum_2030
                e_LT_2030[pt]['fuel production'] = I.loc[2030:yf_2030].dot(fuel_dist_new[pt]['LT'].loc[2030] * d_y_2030.loc[2030:yf_2030]) / d_cum_2030
            else:
                I = self.I_CFP_pt_y[pt]
                e_sedan_2030[pt]['fuel production'] = I.loc[2030:yf_2030].dot(fuel_dist_new[pt]['sedan'].loc[2030] * d_y_2030.loc[2030:yf_2030]) / d_cum_2030
                e_LT_2030[pt]['fuel production'] = I.loc[2030:yf_2030].dot(fuel_dist_new[pt]['LT'].loc[2030] * d_y_2030.loc[2030:yf_2030]) / d_cum_2030

        return e_sedan_2020, e_LT_2020, e_avg_2020, e_sedan_2030, e_LT_2030, e_avg_2030

    def compute_biofuel_emissions(self, biofuel_perc_vol_2050, bio_fuel_prod_e):
        E_pure_gasoline = 34.02262053629327 
        E_pure_ethanol = 22.370115 
        I_TP_gas = 264.168 
        I_TP_ethanol = 0 
        emissions_defaults = pd.read_csv(PATH + 'emission_intensity_defaults.csv', index_col=['fuel'])
        gas_prod_e = emissions_defaults['I_CFP'].loc['ICEG']


        y0 = self.baseline_year
        yi = self.initial_year
        yf = self.final_year
        years = np.arange(yi, yf + 1)
        I_biofuel = pd.DataFrame(0, index=years, columns=['I_TP_biofuel', 'I_CFP_biofuel'])
        bio_frac_vol_y = pd.DataFrame(0, index=years, columns=['frac'])
        GG_kWh_y = pd.DataFrame(0, index=years, columns=['GG_kWh'])


        for y in years:

            if y <= y0:
                biofuel_perc_vol = 10
                bio_fuel_lifecycle_e = 51
            else:
                biofuel_perc_vol = 10 + (biofuel_perc_vol_2050 - 10) * (y - y0)/(yf - y0)
                bio_fuel_lifecycle_e = bio_fuel_prod_e
            E_gas = E_pure_gasoline * (1 - biofuel_perc_vol / 100)
            E_ethanol = E_pure_ethanol * (biofuel_perc_vol / 100)
            B = E_ethanol / (E_gas + E_ethanol)  
            bio_frac_vol_y.loc[y,'frac'] =  biofuel_perc_vol/100
            GG_kWh_y.loc[y, 'GG_kWh'] = 1 / (E_gas + E_ethanol)

            I_biofuel.loc[y,'I_TP_biofuel'] = I_TP_gas*(1-B) + B*I_TP_ethanol
            I_biofuel.loc[y,'I_CFP_biofuel'] = gas_prod_e*(1-B) + (bio_fuel_lifecycle_e * 3.6)*B  

        return I_biofuel, bio_frac_vol_y, GG_kWh_y

    def compute_outputs(self):
        stocks_dict = {}
        d_dict ={}
        F_dict ={}
        years = np.arange(self.baseline_year + 1, self.final_year + 1)
        model_years = np.arange(self.lowest_year, self.final_year + 1)
        fuel_dist_new = pd.DataFrame(index=np.arange(self.initial_year, self.final_year + 1))
        emissions_dist_new = pd.DataFrame(index=np.arange(self.initial_year, self.final_year + 1))
        stocks_plot = pd.DataFrame(index=np.arange(self.initial_year, self.final_year+1))
        d_plot = pd.DataFrame(index=np.arange(self.initial_year, self.final_year + 1))
        lib = pd.DataFrame(0, index=np.arange(self.initial_year, self.final_year+1), columns = ['In_Use','Retired','Sold','Retired_2019'])
        lib_sedan = pd.DataFrame(index=np.arange(self.initial_year, self.final_year+1))
        lib_lt = pd.DataFrame(index=np.arange(self.initial_year, self.final_year + 1))
        fuel_plot = pd.DataFrame(index=np.arange(self.initial_year, self.final_year + 1))
        fuel_PHEVe = pd.DataFrame(index=np.arange(self.initial_year, self.final_year + 1))
        fuel_PHEVg = pd.DataFrame(index=np.arange(self.initial_year, self.final_year + 1))
        emissions = pd.DataFrame(index=np.arange(self.initial_year, self.final_year + 1))
        car_prod = pd.DataFrame(index=np.arange(self.initial_year, self.final_year + 1))
        F_PHEV_corrected = pd.DataFrame(0,index=np.arange(self.initial_year, self.final_year + 1),columns=['e_stock_sedan','g_stock_sedan','e_stock_LT','g_stock_LT','e_sales_sedan','g_sales_sedan','e_sales_LT','g_sales_LT'])
        F_LT, sales, population, sales_per_pop = self.computes_sales()
        pt_size_sales = sales.copy(deep=True)
        d_new, d_car, d_cumulative = self.compute_d_car()
        delta_c = self.capacity_change_calc(d_cumulative)
        batt_cap_table = pd.read_csv(PATH + 'batt_cap.csv',index_col = ['size'])
        I_biofuel, self.bio_frac_vol_y, self.GG_kWh_y = self.compute_biofuel_emissions(self.biofuel_perc_vol_2050, self.bio_fuel_prod_e)
        emissions_defaults = pd.read_csv(PATH + 'emission_intensity_defaults.csv', index_col=['fuel'])
        self.I_TP_pt_y = pd.DataFrame(0,index=np.arange(self.initial_year, self.final_year+1),columns=emissions_defaults.index)
        self.I_CFP_pt_y = pd.DataFrame(0, index=np.arange(self.initial_year, self.final_year + 1),columns=emissions_defaults.index)

        for fuel in emissions_defaults.index:

            if fuel in ['ICEG','HEV','PHEVf']:
                self.I_TP_pt_y.loc[:,fuel] = I_biofuel['I_TP_biofuel'] 
                self.I_CFP_pt_y.loc[:,fuel] = I_biofuel['I_CFP_biofuel'] 
            else:
                self.I_TP_pt_y.loc[:,fuel] = emissions_defaults.loc[fuel, 'I_TP']
                self.I_CFP_pt_y.loc[:,fuel] = emissions_defaults.loc[fuel, 'I_CFP']

        for size in self.sizes:
            for powertrain in self.powertrains:
                column = 'S_' + powertrain + '_' + size
                label = powertrain + '_' + size

                stocks_calc = self.computes_stock(sales.loc[:, column], size)
                d_total = d_car * stocks_calc
                delta_fuel = self.delta_fuel_by_pt[powertrain]

                if powertrain != 'PHEV':
                    F_int, F_new= self.fuel_intensity(delta_c, powertrain, size, stocks_calc,delta_fuel)
                    fuel_total = (F_int * d_total).sum(axis=1)
                    fuel_dist_new[label] = F_new.loc[self.initial_year:self.final_year,:].values.flatten()

                else:
                    F_int1, F_new1 = self.fuel_intensity(delta_c, 'PHEVe', size, stocks_calc,delta_fuel)
                    F_int2, F_new2 = self.fuel_intensity(delta_c, 'PHEVf', size, stocks_calc,delta_fuel)

                    fuel_total1 = (F_int1 * d_total).sum(axis=1) * self.mode/100
                    fuel_total2 = (F_int2 * d_total).sum(axis=1) * (1-self.mode/100)
                    fuel_PHEVe.loc[:, 'PHEVe_' +size] = fuel_total1
                    fuel_PHEVg.loc[:, 'PHEVg_' +size] = fuel_total2
                    fuel_total = fuel_total1 + fuel_total2
                    F_int = F_int1 + F_int2
                    fuel_dist_new[label] = self.mode/100 * F_new1.loc[self.initial_year:self.final_year, :].values.flatten() + F_new2.loc[self.initial_year:self.final_year,:].values.flatten() * (1-self.mode/100)


                    F_PHEV_corrected['e_sales_' + size]  = self.mode/100 * F_new1.loc[self.initial_year:self.final_year, :]
                    F_PHEV_corrected['g_sales_' + size] = (1-self.mode/100) * F_new2.loc[self.initial_year:self.final_year,:]
                    F_PHEV_corrected['e_stock_' + size] = fuel_total1.divide(d_total.sum(axis=1) * 1)
                    F_PHEV_corrected['g_stock_' + size] = fuel_total2.divide(d_total.sum(axis=1) * 1 )


                stocks_dict.update({powertrain + '_' + size: stocks_calc})
                d_dict.update({powertrain + '_' + size: d_total})
                F_dict.update({powertrain + '_' + size: F_int})
                stocks_plot.loc[:, label] = stocks_calc.sum(axis=1)
                d_plot.loc[:,label]= d_total.sum(axis =1)
                fuel_plot.loc[:, label] = fuel_total

                if powertrain == 'BEV' or powertrain == 'HEV' or powertrain == 'PHEV' or powertrain == 'FCEV':
                    batt_cap = batt_cap_table[powertrain][size]
                    lib['In_Use'] = lib['In_Use'] + batt_cap * stocks_plot.loc[:,label]
                    lib['Sold'] =  lib['Sold'] + batt_cap * sales.loc[self.initial_year:self.final_year,column]
                    lib['Retired'] =  lib['Retired'] + -1 *batt_cap * (stocks_plot.loc[:,label].diff() - sales.loc[self.initial_year:self.final_year,column].values)
                    lib['Retired_2019'] = lib['Retired'].cumsum()
                    lib['Retired_2019'] = lib['Retired_2019'] - lib['Retired_2019'][2018]
                    lib.loc[self.initial_year:2019, 'Retired_2019'] = 0

        if self.fgi == "Yes":
            I_grid = self.compute_grid_intensity()
        else:
            D_EV = pd.DataFrame(index = years, columns = ['D_EV'])
            D_EV['D_EV'] = fuel_plot.loc[years,'BEV_sedan'].values.flatten() + fuel_plot.loc[years,'BEV_LT'].values.flatten() + fuel_PHEVe.loc[years,
                'PHEVe_sedan'].values.flatten() + fuel_PHEVe.loc[years,'PHEVe_LT'].values.flatten()

            I_grid, D_2020, D_2035, D_2050, S_h_2020, S_h_2035, S_h_2050 = self.compute_grid_intensity(D_EV)
        for size in self.sizes:
            for powertrain in self.powertrains:
                label = powertrain + '_' + size
                if powertrain != 'PHEV':
                    I, temp = self.compute_emissions(powertrain, fuel_plot.loc[:, label].copy(), I_grid=I_grid)
                    emissions.loc[:, label] = temp.values
                else:
                    I_1, emissions1 = self.compute_emissions('PHEVe', fuel_PHEVe.loc[:, 'PHEVe_' +size].copy(), I_grid=I_grid)
                    I_2, emissions2 = self.compute_emissions('PHEVf', fuel_plot.loc[:, label].copy().subtract(fuel_PHEVe.loc[:, 'PHEVe_' +size].values), I_grid=I_grid)
                    emissions.loc[:, label] = emissions1.values.flatten() + emissions2.values.flatten()
                    I = (I_1*self.mode/100).add(I_2 * (1 - self.mode/100))
                emissions_dist_new[label] = I.multiply(fuel_dist_new[label].values, axis=0)
                car_prod.loc[:, label] = self.compute_car_prod(I_grid, sales.loc[self.initial_year:, 'S_' + label],'CPE_' + label).values
        fuel_dist_sales = self.weighted_average(fuel_dist_new, sales.loc[self.initial_year:,:].copy())
        emission_dist_sales = self.weighted_average(emissions_dist_new, sales.loc[self.initial_year:,:].copy())

        pattern = '(?<!S)_' 
        fuel_dist_stock = fuel_plot.divide(d_plot)*1000
        emission_dist_stock = emissions.divide(d_plot)
        car_prod_pt_size = car_prod
        car_prod = self.sum_sizes(car_prod.fillna(0))/10**6 #
        sales = self.sum_sizes(sales) /1000000
        emissions = self.sum_sizes(emissions) / 1000000000000
        CPE = car_prod.fillna(0).sum(axis = 1)
        CPE_OE = CPE.divide(emissions.sum(axis = 1)) *100
        CPEandOE = CPE.add(emissions.sum (axis = 1))
        stocks_plot = self.sum_sizes(stocks_plot)/1000000
        fuel_plot = self.sum_sizes(fuel_plot)/1000000000
        d_plot_pt_s = d_plot.copy(deep=True)
        d_plot = self.sum_sizes(d_plot)/1000000000000
        F_LT = F_LT *100
        d_new = d_new/1000000000000
        lib = lib/1000000
        population = population/1000000

        fuel_dist_intermediate = fuel_plot.divide(d_plot)
        emission_dist_intermediate = emissions.divide(d_plot)
        fuel_dist_intermediate.columns = fuel_dist_intermediate.columns + '_all'
        emission_dist_intermediate.columns = emission_dist_intermediate.columns + '_all'
        fuel_dist_stock = fuel_dist_stock.join(fuel_dist_intermediate)/1000 
        emission_dist_stock = emission_dist_stock.join(emission_dist_intermediate)

        fuel_dist_stock = fuel_dist_stock.replace(0, np.nan)
        fuel_dist_sales = fuel_dist_sales.replace(0, np.nan)

        emission_dist_stock = emission_dist_stock.replace(0, np.nan)
        emission_dist_sales = emission_dist_sales.replace(0, np.nan)
        fuel_dist_stock.columns = fuel_dist_stock.columns.str.split(pattern, expand=True)
        emission_dist_stock.columns = emission_dist_stock.columns.str.split(pattern, expand=True)
        fuel_prices = self.compute_fuel_prices(self.fuel_price_source)
        fuel_spend_dist_sales = self.compute_fuel_spend_dist(fuel_prices, fuel_dist_sales, F_PHEV_corrected, 'sales')
        fuel_spend_dist_stock = self.compute_fuel_spend_dist(fuel_prices, fuel_dist_stock, F_PHEV_corrected, 'stock')
        fuel_use_by_fuel = pd.DataFrame(index=np.arange(self.initial_year, self.final_year + 1))
        f_PHEV_e = fuel_PHEVe.sum(axis=1)/1000000000
        f_PHEV_g = fuel_PHEVg.sum(axis=1)/1000000000

        fuel_use_by_fuel['Gasoline_Bio'] = f_PHEV_g + fuel_plot['ICEG'] + fuel_plot['HEV']
        fuel_use_by_fuel['Diesel'] = fuel_plot['ICED']
        fuel_use_by_fuel['Electricity'] =  f_PHEV_e + fuel_plot['BEV']
        fuel_use_by_fuel['Hydrogen'] = fuel_plot['FCEV']
        GG_kWh = self.GG_kWh_y # (1 / 33.7) 
        GD_kWh = (1 / 33.7) / 1.13
        kgH2_kWh = 1/33.3 

        fuel_spend_by_fuel = pd.DataFrame(index=np.arange(self.initial_year, self.final_year + 1))
        fuel_spend_by_fuel['Gasoline_Bio'] = ( fuel_use_by_fuel['Gasoline_Bio'].multiply(fuel_prices['gas_bio']) ).multiply(GG_kWh['GG_kWh'])
        fuel_spend_by_fuel['Diesel'] = fuel_use_by_fuel['Diesel'].multiply(fuel_prices['diesel']) *  GD_kWh
        fuel_spend_by_fuel['Electricity'] = fuel_use_by_fuel['Electricity'].multiply(fuel_prices['electricity'])
        fuel_spend_by_fuel['Hydrogen'] = fuel_use_by_fuel['Hydrogen'].multiply(fuel_prices['hydrogen']) * kgH2_kWh
        fuel_spend_by_pt = pd.DataFrame(index=np.arange(self.initial_year, self.final_year + 1))
        fuel_spend_by_pt['ICED'] = fuel_spend_by_fuel['Diesel']
        fuel_spend_by_pt['FCEV'] = fuel_spend_by_fuel['Hydrogen']
        fuel_spend_by_pt['ICEG'] = ( fuel_plot['ICEG'].multiply(fuel_prices['gas_bio']) ).multiply(GG_kWh['GG_kWh'])
        fuel_spend_by_pt['HEV'] = ( fuel_plot['HEV'].multiply(fuel_prices['gas_bio']) ).multiply(GG_kWh['GG_kWh'])
        fuel_spend_by_pt['BEV'] = fuel_plot['BEV'].multiply(fuel_prices['electricity'])
        fuel_spend_by_pt['PHEV'] = f_PHEV_e.multiply(fuel_prices['electricity']) + ( (f_PHEV_g.multiply(fuel_prices['gas_bio']) ) ).multiply(GG_kWh['GG_kWh'])
        sales_spend_by_pt, single_sedan_prices, single_LT_prices = self.compute_sales_spend(pt_size_sales)  
        maint_cost_pt_s, maint_cost_pt, maint_cost_fleet = self.compute_maint_costs(d_plot_pt_s)
        total_spend_by_pt = pd.DataFrame(0,index=np.arange(self.initial_year, self.final_year + 1), columns=self.powertrains)
        for pt in self.powertrains:
            total_spend_by_pt[pt] = maint_cost_pt[pt]/1000000000 + fuel_spend_by_pt[pt] + sales_spend_by_pt[pt]

        costs_sedan_2020, costs_LT_2020, costs_sedan_2030, costs_LT_2030 = self.single_car_spend_dist(18, d_car, d_cumulative, fuel_dist_sales, fuel_prices, single_sedan_prices, single_LT_prices, F_PHEV_corrected)
        total_spend_by_spend_type = pd.DataFrame(0, index=np.arange(self.initial_year, self.final_year + 1), columns=['Maintenance', 'Fuel', 'Car Sale'])
        total_spend_by_spend_type['Maintenance'] = maint_cost_fleet/1000000000
        total_spend_by_spend_type['Fuel'] = fuel_spend_by_pt.sum(axis=1)
        total_spend_by_spend_type['Car Sale'] = sales_spend_by_pt.sum(axis=1)
        frac_LT_2020 = F_LT['F_LT'].loc[2020] / 100
        frac_LT_2030 = F_LT['F_LT'].loc[2030] / 100

        e_sedan_2020, e_LT_2020, e_avg_2020, e_sedan_2030, e_LT_2030, e_avg_2030 = self.lifecycle_e_per_d(18, d_car, d_cumulative, FLEET_DATA, fuel_dist_new, I_grid)
        tot_cars = stocks_plot.sum(axis = 1)
        tot_dist = d_plot.sum(axis = 1)
        tot_fuel = fuel_plot.sum(axis = 1)
        tot_emissions = emissions.sum(axis = 1)
        fuel_per_car = tot_fuel/ tot_cars
        fuel_per_dist = (tot_fuel/tot_dist)/1000
        dist_per_car = (tot_dist/ tot_cars)
        emissions_per_car = tot_emissions/ tot_cars
        emissions_per_dist = tot_emissions/ tot_dist

        cost = total_spend_by_pt.sum(axis = 1)
        cost_since2019 = cost.cumsum()/10**3
        cost_since2019 = cost_since2019 - cost_since2019.loc[2019]
        cost_since2019.loc[self.initial_year:2019] = 0

        e_cum_op = emissions.cumsum()
        e_cum_op = e_cum_op - e_cum_op.loc[2019,:]
        e_cum_op.loc[self.initial_year:2019, :] = 0
        e_cum_op = e_cum_op.sum(axis = 1)

        CPEandOE_cumulative = CPEandOE.cumsum()
        CPEandOE_cumulative = CPEandOE_cumulative - CPEandOE_cumulative.loc[2019]
        CPEandOE_cumulative.loc[self.initial_year:2019] = 0

        res = {
            'fuel_dist_sales': fuel_dist_sales,
            'emission_dist_sales': emission_dist_sales,
            'fuel_dist_stock': fuel_dist_stock,
            'emission_dist_stock': emission_dist_stock,
            'cpe_and_oe': CPEandOE,
            'cpe': CPE,
            'cpe_oe': CPE_OE,
            'i_grid': I_grid,
            'f_lt': F_LT,
            'sales': sales,
            'stock': stocks_plot,
            'd_new': d_new,
            'fuel': fuel_plot,
            'population': population,
            'sales_per_pop': sales_per_pop,
            'lib': lib,
            'emissions': emissions,
            'd_plot': d_plot,
            'fuel_per_car': fuel_per_car,
            'fuel_per_dist': fuel_per_dist,
            'dist_per_car': dist_per_car,
            'emissions_per_car': emissions_per_car,
            'emissions_per_dist': emissions_per_dist,
            'e_cum_op': e_cum_op,
            'cpe_and_oe_cumu':CPEandOE_cumulative,
            'fuel_prices': fuel_prices,
            'fuel_spend_dist_sales': fuel_spend_dist_sales,
            'fuel_spend_dist_stock': fuel_spend_dist_stock,
            'fuel_use_by_fuel': fuel_use_by_fuel,
            'fuel_spend_by_fuel': fuel_spend_by_fuel,
            'fuel_spend_by_pt':fuel_spend_by_pt,
            'sales_spend_by_pt': sales_spend_by_pt,
            'total_spend_by_pt': total_spend_by_pt,
            'total_spend_by_spend_type': total_spend_by_spend_type,
            'cost':cost,
            'cost_since2019': cost_since2019,
            'costs_sedan_2020': costs_sedan_2020,
            'costs_LT_2020': costs_LT_2020,
            'costs_sedan_2030': costs_sedan_2030,
            'costs_LT_2030': costs_LT_2030,
            'e_sedan_2020': e_sedan_2020,
            'e_LT_2020': e_LT_2020,
            'e_avg_2020': e_avg_2020,
            'e_sedan_2030': e_sedan_2030,
            'e_LT_2030': e_LT_2030,
            'e_avg_2030': e_avg_2030,
        }

        if self.fgi == 'No':
            res['D_2020'] = D_2020
            res['D_2035'] = D_2035
            res['D_2050'] = D_2050
            res['S_h_2020'] = S_h_2020
            res['S_h_2035'] = S_h_2035
            res['S_h_2050'] = S_h_2050

        return res

    def run(self):
        return self.compute_outputs()

    def sum_sizes(self,df):
        pattern = '(?<!S)_' 
        if 'S_BEV_sedan' in df.columns:
            df = df.fillna(0)
        df.columns = df.columns.str.split(pattern, expand=True)
        return df.groupby(axis=1, level=0).sum()

    def weighted_average(self,df, wf):
        pattern = '(?<!S)_' 
        df.columns = df.columns.str.split(pattern, expand=True)
        wf.columns = wf.columns.str.split(pattern, expand=True)
        df_final = df.copy()
        for p in self.powertrains:
            df1 = df.groupby(axis = 1, level = 0).get_group(p)
            wf1 = wf.groupby(axis=1, level=0).get_group('S_' + p)
            sum = wf1['S_' + p].sum(axis = 1).copy().replace(0, np.nan)
            vals = (df1[p].sedan.multiply(wf1['S_' + p].sedan, axis =0).values.flatten() + df1[p].LT.multiply(wf1['S_' + p].LT, axis = 0).values.flatten())/sum.values.flatten()
            df_final[p +'/all'] = vals
        return df_final

    def compute_d_car(self):

        years = np.arange(self.initial_year, self.final_year + 1)
        model_years = np.arange(self.lowest_year, self.final_year + 1)
        d_car = pd.DataFrame(index=years, columns=['m_' + str(year) for year in model_years])
        d_new = pd.DataFrame(index=model_years)

        d_new['d_n'] = self.fleet_data.loc[self.lowest_year:self.baseline_year,'dn' + self.pick_sources('dn')]
        d_new['delta_d_a'] = self.fleet_data.loc[self.lowest_year:self.baseline_year,'delta_d_a' + self.pick_sources('delta_d_a')]

        base_d = d_new.loc[self.baseline_year,'d_n']
        base_d_a = d_new.loc[self.baseline_year,'delta_d_a']
        D_life_base = 206  # thousand miles. expected life distance of avg car sold in 2019, with expected life of ~17.5 years. Table 3.14 in DOE TEDB 2021. https://tedb.ornl.gov/wp-content/uploads/2021/02/TEDB_Ed_39.pdf
        delta_d_a_future = (self.delta_d_a_future - base_d_a * 100) / base_d_a
        d_new.loc[self.baseline_year+1:self.final_year,'d_n'] = (self.projection(base_d,self.d_future,'d_'+self.region +'_Default',self.delta_d_future).loc[:,'d_'+self.region +'_Default'] ) * self.D_life/D_life_base
        d_new.loc[self.baseline_year+1:self.final_year,'delta_d_a'] = self.projection(base_d_a,self.d_a_future,'d_a_'+self.region +'_Default',delta_d_a_future).loc[:,'d_a_'+self.region +'_Default']

        for curr in years:
            for model in model_years:
                if model > curr:
                    d_car['m_' + str(model)][curr] = 0
                elif model == curr:
                    d_car['m_' + str(model)][curr] = d_new['d_n'][curr]
                else:
                    a = curr - model
                    d_car['m_' + str(model)][curr] = max(d_new['d_n'][curr] *(1-d_new['delta_d_a'][curr]*a), 0)
        d_cumulative = d_car.cumsum()

        return d_new,d_car,d_cumulative

    def PHEV_mode(self,size):
        m = self.pick_sources('Fn')
        self.fleet_data['Fn_PHEV_' + size + '_US_VIS20'] = 0.01*(self.mode * self.fleet_data['Fn_PHEVe_' + size + '_US_VIS20'] + (1-self.mode) * self.fleet_data['Fn_PHEVf_' + size + '_US_VIS20'])
        self.fleet_data['Fn_future_PHEV_' + size + '_world_'+ self.fuel_int] = 0.01*(self.mode * self.fleet_data['Fn_future_PHEVe_' + size + '_world_'+ self.fuel_int] + (1-self.mode) * self.fleet_data['Fn_future_PHEVf_' + size + '_world_'+ self.fuel_int])
        self.F_VIS_derates['PHEV'][size] = 0.01*(self.mode * self.F_VIS_derates['PHEVe'][size] + (1-self.mode) * self.F_VIS_derates['PHEVf'][size])
        self.subregion_data['PHEV'][self.region] = 0.01 * (self.mode * self.subregion_data['PHEVe'][self.region] + (1 - self.mode) * self.subregion_data['PHEVf'][self.region])

    def fuel_intensity(self, delta_c, powertrain, size, stock, delta_fuel = None):
        years = np.arange(self.initial_year, self.final_year + 1)
        model_years = np.arange(self.lowest_year, self.final_year + 1)
        F = pd.DataFrame(index=years, columns=['m_' + str(year) for year in model_years])
        F_new = pd.DataFrame(index=model_years,columns =['F'])
        self.F_VIS_derates = pd.read_csv(PATH + "F_VIS_derates.csv", index_col='size')
        delta_efficiency = 0.65
        self.subregion_data = pd.read_csv(PATH + "subregion_data.csv", index_col='Region')

        column = powertrain + '_' + size

        F_new['F'] = self.fleet_data.loc[self.lowest_year:self.baseline_year,'Fn_'+ column + self.pick_sources('Fn')]
        if self.fuel_int == 'MIT15':
            projection_col = 'Fn_future_' + column + '_world_'+ self.fuel_int
        else:
            projection_col = 'Fn_future_' + column + '_US_' + self.fuel_int
        base = F_new.loc[self.baseline_year, 'F']

        F_new.loc[self.baseline_year+1:self.final_year,'F'] = self.projection(base, self.fuel_int,projection_col,delta_fuel).loc[:,projection_col]
        x_d = 1 

        x_T = self.subregion_data.loc[self.region,powertrain]
        x_VIS = 1/self.F_VIS_derates.loc[size,powertrain]
        F_new = F_new * x_T * x_VIS

        for model in model_years:
            model_stock = stock[f'm_{model}']
            model_delta_c = delta_c[f'm_{model}']
            model_F = F_new['F'][model]

            data = {}

            for curr in years:
                stock_value = model_stock[curr]
                if stock_value == 0 or math.isnan(stock_value):
                    data[curr] = 0
                else:
                    if powertrain == 'BEV' or powertrain == 'PHEVe':
                        x_d = 1 / (1 - abs(model_delta_c[curr] * delta_efficiency))
                    data[curr] = model_F * x_d

            F[f'm_{model}'].update(pd.Series(data=data, index=F[f'm_{model}'].index))

        return F, F_new

    def compute_grid_intensity(self, D_EV = None):

        model_years = np.arange(self.initial_year, self.final_year + 1)
        I = pd.DataFrame(index=model_years)
        historical_em = pd.read_csv(PATH + 'historical_emissions.csv',index_col = ['year'])
        I.loc[self.initial_year:self.baseline_year, 'I'] = historical_em.loc[self.initial_year:self.baseline_year,self.region].values
        if 'Fuel' in self.emissions_view:
            I['I'] = 1.17 * I['I']
        base_I = I.loc[self.baseline_year, 'I']
        if self.fgi == "Yes":

            I.loc[self.baseline_year + 1:self.final_year, 'I'] = self.projection((base_I), self.cips,
                                                                             'CI_future_' + self.region + '_' + self.cips,
                                                                             self.delta_I_fix).loc[:,
                                                             'CI_future_' + self.region + '_' + self.cips]
            I = I.astype(float)
            return I
        else:
            I_grid, D_2020, D_2035, D_2050, S_h_2020, S_h_2035, S_h_2050 = self.grid.fleet_grid_integrator(D_EV / 1000000000, self.region, self.emissions_view)
            I.loc[self.baseline_year + 1:self.final_year, 'I'] = I_grid.values.flatten()
            return I, D_2020, D_2035, D_2050, S_h_2020, S_h_2035, S_h_2050

    def compute_emissions(self, powertrain, fuel_total, I_grid):

        emissions_defaults = pd.read_csv(PATH + 'emission_intensity_defaults.csv',index_col=['fuel'])

        I_rel = I_grid.copy()
        if powertrain == 'BEV' or powertrain == 'PHEVe':
            if self.emissions_view != 'Tailpipe only':
                emissions = I_rel.multiply(fuel_total.values, axis = 0)
            else:
                emissions = 0 * fuel_total
        else:
            if powertrain == 'FCEV':
                if self.h2_prod == 'SMR':
                    powertrain = 'FCEV_SMR'
                elif self.h2_prod == 'SMR with carbon capture':
                    powertrain = 'FCEV_SMR_CC'
                else:
                    powertrain = 'FCEV_elect'
            I = self.I_TP_pt_y[powertrain] 
            I_rel['I'] = I
            if self.emissions_view != 'Tailpipe only':
                I = I + self.I_CFP_pt_y[powertrain] 
            if 'Fuel' in self.emissions_view:
                I = I + 0 
            I_rel['I'] = I
            emissions = I * fuel_total

        return I_rel, emissions

    def capacity_change_calc(self, d_cumulative):
        years = np.arange(self.initial_year, self.final_year + 1)
        model_years = np.arange(self.lowest_year, self.final_year + 1)
        delta_c = pd.DataFrame(index=years, columns=['m_' + str(year) for year in model_years])
        nonlinear_cutoff = 50000

        for curr in years:
            for model in model_years:
                d_cum = d_cumulative['m_' + str(model)][curr]
                if d_cum < nonlinear_cutoff:
                    delta_c['m_' + str(model)][curr] = 0.4553*(d_cum/100000)**3 - 0.5614*(d_cum/100000)**2 + 0.2722*(d_cum/100000)
                else:
                    delta_c['m_' + str(model)][curr] = 0.029*(d_cum/100000) + 0.0392

        return delta_c

    def compute_car_prod(self, I_grid, sales, column):
        c_tsy_onecar = FLEET_DATA.loc[self.initial_year:self.final_year,column]
        years = np.arange(self.initial_year, self.final_year + 1)
        c_tsy = pd.DataFrame(index= years, columns = [column])
        I_2014 = I_grid.loc[2014,:].values[0]
        intermediate = sales.mul(c_tsy_onecar, axis = 0)
        c_tsy = I_grid.mul(intermediate, axis = 0)/I_2014
        return c_tsy

if __name__ == '__main__':
    fleet = FleetModel()

    fleet.set_user_inputs(
        {'region': 'US', 'msps2': 'User', 'growth_curve':'s curve', 'msps1': 'Static', 'size_share': '', 'spp': 'AEO20',
         'delta_spp': '', 'fuel_int': 'MIT15', 'delta_fuel': '', 'h2_prod': 'SMR', 'fgi': 'Yes', 'cips': 'AEO20',
         'delta_I': '', 'evmethod': '', 'O': '', 'D': '', 'fhw': '', 'fh': '', 'fw': '', 'Hd': '', 'ap_gas': '',
         'car_longevity': 'Static', 'delta_hl': '', 'mode': '50', 'd_future': 'Static', 'delta_d_future': '',
         'd_a_future': 'Static', 'delta_d_a_future': '', 'pps': 'AEO20', 'delta_p': '', 'fuel_price_source': 'User',
         'gasoline_price_change': '0', 'diesel_price_change': '0', 'electricity_price_change': '0', 'biofuel_price_change': '0', 'biofuel_perc_vol_2050': 10,
         'bio_fuel_prod_e': 51,'h2_price_change': '0', 'powertrain_size_share': {'sedan': [100, 0, 0, 0, 0, 0], 'LT': [100, 0, 0, 0, 0, 0]}, 'yp_BEV':2030, 'yp_FCEV':2040}
    )

    fleet.set_defaults()
    fleet.compute_outputs()
    z = 0
