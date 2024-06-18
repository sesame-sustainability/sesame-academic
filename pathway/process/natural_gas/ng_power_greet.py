from core.pathway import ActivitySource
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from analysis.lca import compute_input_flows, compute_emission_flows
import core.validators as validators
import core.conditionals as conditionals
import os
import pandas as pd

import pathway.process.natural_gas.ccs as ccs
from tea.electricity.ng.ng_tea import NaturalGasTEA
from analysis.sensitivity import SensitivityInput

PATH = os.getcwd() + "/pathway/process/natural_gas/"

class NGPowerGREET(ActivitySource):

    @classmethod
    def user_inputs(cls):
        tea_inputs = NaturalGasTEA.user_inputs(tea_lca=True)
        for input in tea_inputs:
            input.conditionals.append(conditionals.context_equal_to('compute_cost', True))

        lca_inputs = [
            # OptionsInput('user_efficiency','Use user-specified efficiency?', options=['Yes','No']),
            # ContinuousInput('efficiency', 'Power Generation Efficiency (%), between 28 and 55 recommended',
            #                 validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
            #                 conditionals=[conditionals.input_equal_to('user_effeciency','Yes')]),
            CategoricalInput(
                'generation_region', 'Region',
                defaults=[Default('US')],
                tooltip=Tooltip(
                    'For LCA & TEA, Region impacts power plant efficiency. For TEA, Region also impacts capacity factor and thus levelized capital cost. US average efficiency = 50% (LHV basis), capacity factor =45%, for a mix of generator types.',
                    source='GREET2019, EPA',
                    source_link='https://greet.es.anl.gov/; https://www.epa.gov/energy/emissions-generation-resource-integrated-database-egrid',
                )
            ),
            CategoricalInput(
                'generator_type', 'Generator Type',
                defaults=[Default('Mix')],
                tooltip=Tooltip(
                    'For LCA & TEA, generator type impacts power plant efficiency. For TEA, generator type also impacts capacity factor and cost parameters. The generator mix varies by regions. For US average, 84% combined cycle, 6% gas turbine, 9% boiler. US mix average efficiency ~50% (LHV basis), capacity factor ~ 45%.',
                    source='GREET2019',
                    source_link='https://greet.es.anl.gov/',
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

        return  lca_inputs + ccs.user_inputs() + tea_inputs

    @classmethod
    def sensitivity(cls):
        return [
            SensitivityInput(
                'generation_region',
                minimizing='WECC',
                maximizing='ASCC',
            ),
            SensitivityInput(
                'generator_type',
                minimizing='Combined Cycle',
                maximizing='Gas Turbine',
            ),
            # SensitivityInput(
            #     'infrastructure_emission_inclusion',
            #     minimizing='No',
            #     maximizing='Yes',
            # ),
            SensitivityInput(
                'use_CCS',
                minimizing='Yes',
                maximizing='No',
            ),
        ]

    def get_inputs(self):
        flow_dict = compute_input_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )

        if self.use_CCS == 'Yes':
            # TODO: this is called here to run CCS, would be better to remove this implicit state
            self.get_emissions()

            # TODO: would be nice to move below into CCS module as well
            CCS_inputs = pd.read_csv(PATH + "ng_power_ccs_lcidata.csv")
            filtered = CCS_inputs[CCS_inputs['technology'] == 'amine']
            nat_gas_ccs = float(filtered[filtered['flows'] == 'natural gas'].iloc[0].value)
            electricity_ccs = float(filtered[filtered['flows'] == 'electricity'].iloc[0].value)
            mj_in_kwh = 3.6

            if self.use_user_ci == 'Powerplant':
                incremental_electricity = {
                    'name': 'electricity',
                    'value': self.ccs.CO2_captured * electricity_ccs / mj_in_kwh,
                    'unit': 'kWh'
                }

                elec_nat_gas = compute_input_flows(
                    self.filtered_data_frame(),
                    flow_output = incremental_electricity
                )
                flow_dict['natural gas']['value'] += elec_nat_gas['natural gas']['value']

            flow_dict['natural gas']['value'] += self.ccs.CO2_captured * nat_gas_ccs

        return {
            'primary': flow_dict['natural gas'],
            'secondary': [flow_dict[key] for key in flow_dict if key != 'natural gas']
        }

    def get_emissions(self):
        emissions = compute_emission_flows(
            self.filtered_data_frame(),
            flow_output=self.output)

        if self.use_CCS == 'Yes':
            if self.input_set.context.get('compute_cost'):
                self.use_user_ci = 'Powerplant'

            self.ccs = ccs.CCS(self.input_set, self.filtered_data_frame(), emissions)
            self.ccs.run()



        return emissions
