from core.pathway import ActivitySource
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from analysis.lca import compute_input_flows, compute_emission_flows
from analysis.sensitivity import SensitivityInput
from core import validators, conditionals

class NaturalGas(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
            CategoricalInput(
                'ng_type', 'Natural Gas Type',
                defaults=[Default('Mix (~50/50 Conventional/Shale)')],
                tooltip=Tooltip(
                    'The extraction process is different per natural gas type. US average mix is used as default.',
                    source='GREET2019',
                    source_link='https://greet.es.anl.gov/',
                )

            ),
            CategoricalInput(
                'well_infrastructure', 'Count Emissions from Building Well Infrastructure',
                defaults=[Default('Yes')],
                tooltip=Tooltip(
                    'Emissions associated with the cement, steel, etc. used for constructing the well, amortized over the plant lifetime and levelized by plant power output. This contribution to LCA is very small and thus often ignored by many LCA studies.',
                    source='GREET2019',
                    source_link='https://greet.es.anl.gov/',
                )

            ),
            CategoricalInput(
                'leakage_param', 'Methane Leakage Parameter',
                defaults=[Default('EPA 2019')],
                tooltip=Tooltip('Default based on EPA study finding 1.4% leakage at US natural gas production sites. EDF estimated 2.3%. Large uncertainty exists and true leakage could be significantly higher. Some leaks can be part of the system design for pressure balancing. Refer to the ~30 numbers near Cell A121 of the GREET Inputs tab for the specific values.',
                    source='EDF & EPA 2019',
                    source_link='https://www.science.org/doi/10.1126/science.aar7204',
                )),
            # ContinuousInput(
            #     'leak_rate', 'Methane Leakage Rate', unit='%',
            #     defaults=[Default(2.3)],
            #     validators = [validators.numeric(), validators.gte(0), validators.lte(20)],
            #     tooltip=Tooltip('Default based on EDF study finding 2.3% leakage at US natural gas production sites. EPA earlier estimated 1.4%. Large uncertainty exists and true leakage could be significantly higher.',
            #                source='EDF 2019',
            #                source_link='https://www.science.org/doi/10.1126/science.aar7204')
            #
            #     )
        ]

    @classmethod
    def sensitivity(cls):
        return [
            SensitivityInput(
                'ng_type',
                minimizing='Conventional',
                maximizing='Shale',
            ),
            SensitivityInput(
                'well_infrastructure',
                minimizing='No',
                maximizing='Yes',
            ),
            SensitivityInput(
                'leakage_param',
                minimizing='EPA (1.4%)',
                maximizing='~5%',
            ),

        ]

    def get_inputs(self):
        flow_dict = compute_input_flows(self.filtered_data_frame(), flow_output=self.output)

        return {
            'primary': None,
            'secondary': [val for _, val in flow_dict.items()]
        }

    def get_emissions(self):
        return compute_emission_flows(self.filtered_data_frame(), self.output)
