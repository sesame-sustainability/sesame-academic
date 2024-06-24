from core.pathway import ActivitySource
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from analysis.lca import compute_input_flows, compute_emission_flows
import core.validators as validators
import core.conditionals as conditionals
import os
import pandas as pd

from tea.electricity.coal.coal_tea import CoalTEA
import pathway.process.coal.ccs as ccs
from analysis.sensitivity import SensitivityInput

PATH = os.getcwd() + "/pathway/process/coal/"

class CoalPowerGREET(ActivitySource):

    @classmethod
    def user_inputs(cls):
        tea_inputs = CoalTEA.user_inputs(tea_lca=True)
        for input in tea_inputs:
            input.conditionals.append(conditionals.context_equal_to('compute_cost', True))

        lca_inputs = [
            CategoricalInput(
                'region', 'Region',
                defaults=[Default('US')],
                tooltip=Tooltip(
                    'For LCA & TEA, Region impacts power plant efficiency. For TEA, Region also impacts capacity factor and thus levelized capital cost. US average efficiency = 36% (LHV basis), capacity factor =54%, for a mix of generator types.  .',
                    source='GREET2019, EPA',
                    source_link='https://greet.es.anl.gov/; https://www.epa.gov/energy/emissions-generation-resource-integrated-database-egrid',
                )
            ),
            CategoricalInput(
                'plant_type', 'Generator Type',
                defaults=[Default('Boiler (~99% of US coal turbines)')],
                tooltip=Tooltip(
                    'For LCA & TEA, generator type impacts power plant efficiency. For TEA, generator type also impacts capacity factor and cost parameters. The generator mix varies by regions. For US average, 99% boiler, 1% IGCC. US mix average efficiency ~36% (LHV basis), capacity factor ~ 54%.',
                    source='GREET2019, EPA',
                    source_link='https://greet.es.anl.gov/; https://www.epa.gov/energy/emissions-generation-resource-integrated-database-egrid',
                )

            ),
            CategoricalInput(
                'infrastructure_emission_inclusion', 'Count Emissions from Building Powerplant',
                defaults=[Default('Yes')],
                tooltip=Tooltip(
                    'Emissions associated with the cement, steel, etc. used for constructing the power plant, amortized over the plant lifetime and levelized by plant power output. This contribution to LCA is very small and thus often ignored by many LCA studies.',
                    source='GREET2019',
                    source_link='https://greet.es.anl.gov/',
                )

            ),
        ]

        return lca_inputs + ccs.user_inputs() + tea_inputs

    @classmethod
    def sensitivity(cls):
        return [
            SensitivityInput(
                'region',
                minimizing='RFC',
                maximizing='HICC',
            ),
            SensitivityInput(
                'plant_type',
                minimizing='IGCC - Integrated Gasification Combined Cycle',
                maximizing='Boiler (~99% of US coal turbines)',
            ),
            SensitivityInput(
                'infrastructure_emission_inclusion',
                minimizing='No',
                maximizing='Yes',
            ),
            SensitivityInput(
                'use_CCS',
                minimizing='Yes',
                maximizing='No',
            ),
        ]

    @property
    def coal_type(self):
        if not hasattr(self, 'pathway'):
            return None

        return self.pathway.instance('upstream').coal_type

    def filtered_data_frame(self):
        df = super().filtered_data_frame()
        if self.coal_type:
            df = df[df['Coal Type'] == self.coal_type]
        return df

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

            if not self.input_set.context.get('compute_cost', None):
                self.use_user_ci = 'Powerplant' 

            if self.use_user_ci == 'Powerplant':
                incremental_electricity = {
                    'name': 'electricity',
                    'value': self.ccs.CO2_captured * electricity_ccs / mj_in_kwh,
                    'unit': 'kWh'
                }

                elec_emissions = compute_input_flows(
                    self.filtered_data_frame(),
                    flow_output = incremental_electricity
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
            if self.input_set.context.get('compute_cost'):
                self.use_user_ci = 'Powerplant'

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
