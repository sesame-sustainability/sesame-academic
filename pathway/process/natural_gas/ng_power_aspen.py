from core.pathway import ActivitySource
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from analysis.lca import compute_input_flows, compute_emission_flows
import core.validators as validators
import core.conditionals as conditionals
import numpy as np
import pandas as pd
import os

import pathway.process.natural_gas.ccs as ccs
from tea.electricity.ng.ng_tea import NaturalGasTEA

PATH = os.getcwd() + "/pathway/process/natural_gas/"

class NGPowerASPEN(ActivitySource):

    @classmethod
    def user_inputs(cls):
        tea_inputs = NaturalGasTEA.user_inputs(tea_lca=True)
        for input in tea_inputs:
            input.conditionals.append(conditionals.context_equal_to('compute_cost', True))

        greet_data = pd.read_csv(os.path.join(PATH, 'ng_power_greet_lcidata.csv'))
        greet_regions = list(greet_data['Region'].unique())

        lca_inputs = [
            OptionsInput(
                'generation_region', 'Region',
                defaults=[Default('US')],
                options=greet_regions,
            ),
            CategoricalInput(
                'turbine', 'Generator Type',
                defaults=[Default('Combined Cycle')],
            ),
            CategoricalInput(
                'model', 'Turbine Model',
            ),
            ContinuousInput(
                'loading', 'Loading',
                unit='%',
                defaults=[Default(50)],
                #     Default(57, conditionals=[conditionals.input_equal_to('turbine', 'Combined Cycle')]),
                #     Default(14, conditionals=[conditionals.input_equal_to('turbine', 'Gas Turbine')]),
                # ],
                validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                tooltip=Tooltip('Powerplant capacity factors averaged ~57% for combined cycle, ~12% for gas turbine, & ~40% for coal, in the US in 2020.', source='EIA 2020', source_link='https://www.eia.gov/electricity/annual/html/epa_04_08_a.html')
            ),
        ]

        return lca_inputs + ccs.user_inputs(tea=False) + tea_inputs

    def get_interpolated_df(self):
        df = self.filtered_data_frame()
        interpolated_df = pd.DataFrame(columns=df.columns)
        for flow in df.flows.unique():
            rows = df[df['flows'] == flow]
            rows = rows.sort_values(by=['Loading'])
            rows['value'] = np.interp(self.loading/100, rows['Loading'], rows['value'])
            rows['Loading'] = self.loading/100
            interpolated_df = interpolated_df.append(rows.iloc[0].to_dict(), ignore_index=True)
        return interpolated_df

    def get_inputs(self):
        flow_dict = compute_input_flows(
            self.get_interpolated_df(),
            flow_output=self.output
        )

        if self.use_CCS == 'Yes':
            self.get_emissions()

            CCS_inputs = pd.read_csv(PATH + "ng_power_ccs_lcidata.csv")
            filtered = CCS_inputs[CCS_inputs['technology'] == self.ccs.technology]
            nat_gas_ccs = float(filtered[filtered['flows'] == "natural gas"].iloc[0].value)
            electricity_ccs = float(filtered[filtered['flows'] == "electricity"].iloc[0].value)
            mj_in_kwh = 3.6

            if self.use_user_ci == 'No':
                incremental_electricity = {
                    'name': 'electricity',
                    'value': self.ccs.CO2_captured * electricity_ccs / mj_in_kwh,
                    'unit': 'kWh'
                }

                elec_emissions = compute_input_flows(
                    self.filtered_data_frame(),
                    flow_output=incremental_electricity
                )
                flow_dict['natural gas']['value'] += elec_emissions['natural gas']['value']

            flow_dict['natural gas']['value'] += self.ccs.CO2_captured * nat_gas_ccs

        return {
            'primary': flow_dict['natural gas'],
            'secondary': [flow_dict[key] for key in flow_dict if key != 'natural gas']
        }

    def get_output(self):
        return self.output

    def get_emissions(self):
        emissions = compute_emission_flows(
            self.get_interpolated_df(),
            flow_output=self.output)

        if self.use_CCS == 'Yes':
            self.ccs = ccs.CCS(self.input_set, self.get_interpolated_df(), emissions)
            self.ccs.run()

        return emissions
