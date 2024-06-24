from core.pathway import ActivitySource
from core.inputs import CategoricalInput, ContinuousInput, OptionsInput, Default, Tooltip
from analysis.lca import compute_input_flows, compute_emission_flows
import core.validators as validators
import core.conditionals as conditionals
import os
import pandas as pd

from tea.electricity.coal.coal_tea import CoalTEA
import pathway.process.coal.ccs as ccs

PATH = os.getcwd() + "/pathway/process/coal/"

class CoalPowerASPEN(ActivitySource):
    @classmethod
    def user_inputs(cls):
        tea_inputs = CoalTEA.user_inputs(tea_lca=True)
        for input in tea_inputs:
            input.conditionals.append(conditionals.context_equal_to('compute_cost', True))

        lca_inputs = [
            CategoricalInput(
                'generator_type', 'Generator Type',
                defaults=[Default('Boiler, Super-Critical')],
            ),
            CategoricalInput(
                'region', 'Region',
                defaults=[Default('US')],
            ),
            ContinuousInput(
                'loading_ratio', 'Loading',
                unit='%',
                defaults=[Default(40)], 
                tooltip=Tooltip(
                    'Powerplant capacity factors averaged ~57% for combined cycle, ~12% for gas turbine, & ~40% for coal, in the US in 2020.',
                    source='EIA 2020', source_link='https://www.eia.gov/electricity/annual/html/epa_04_08_a.html'),
                validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
            ),
        ]

        return lca_inputs + ccs.user_inputs() + tea_inputs

    def get_inputs(self):
        flow_dict = compute_input_flows(
            self.filtered_data_frame(),
            flow_output=self.output)

        if self.use_CCS == 'Yes':
            self.get_emissions()

            CCS_inputs = pd.read_csv(PATH + "coal_power_CCS_lcidata.csv")
            filtered = CCS_inputs[CCS_inputs['technology'] == self.ccs.technology]
            coal_ccs = float(filtered[filtered['flows'] == "coal"].iloc[0].value)
            electricity_ccs = float(filtered[filtered['flows'] == "electricity"].iloc[0].value)
            mj_in_kwh = 3.6

            if self.use_user_ci == 'Powerplant':
                incremental_electricity = {
                    'name': 'electricity',
                    'value': self.ccs.CO2_captured * electricity_ccs / mj_in_kwh,
                    'unit': 'kWh'
                }

                elec_emissions = compute_input_flows(
                    self.filtered_data_frame(),
                    flow_output=incremental_electricity
                )
                flow_dict['coal']['value'] += elec_emissions['coal']['value']

            flow_dict['coal']['value'] += self.ccs.CO2_captured * coal_ccs

        return {
            'primary': flow_dict['coal'],
            'secondary': [flow_dict[key] for key in flow_dict if key != 'coal']
        }

    def get_emissions(self):
        emissions = compute_emission_flows(
            self.filtered_data_frame(),
            flow_output=self.output)

        if self.use_CCS == 'Yes':
            self.ccs = ccs.CCS(self.input_set, self.filtered_data_frame(), emissions)

            coal_type = self.coal_type
            if 'Mix' in coal_type:
                coal_type = 'Mix'
            self.ccs.run(coal_type)

        return emissions

    @property
    def coal_type(self):
        if not hasattr(self, 'pathway'):
            return None

        return self.pathway.instance('upstream').coal_type
