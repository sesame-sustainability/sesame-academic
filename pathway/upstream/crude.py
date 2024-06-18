from core.pathway import ActivitySource
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from analysis.lca import compute_input_flows, compute_emission_flows
from core import conditionals, validators


class Crude(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
            CategoricalInput('crude_type', 'Crude Type',
                             defaults=[Default('Average Mix to US Refineries')],
                             tooltip=Tooltip(
                                 'US average mix (by volume or energy): 77% conventional, 8% oil sand, 15% shale oil. Caveat: GREET does not have crude-specific refining emission models built in, and thus we are using an average refining emissions in the process stage, which does not change with the crude type. However, by varying the available crude sulfur content and API knobs in GREET, we found that such variation does not have a very large impact on the refining emissions and even smaller impact on well-to-wheel LCA because the lifecycle GHG emissions are dominated by end-use combustion. The impact is a few percent deviation (lifecycle-wise) from the base case when compared with the extreme cases of sulfur content and API (thus refining efficiency) in GREET.',
                                 source='GREET2019',
                                 source_link='https://greet.es.anl.gov/',
                             )
                             ),
            CategoricalInput('crude_sub_type', 'Crude Sub-Type',
                             conditionals=[conditionals.input_included_in('crude_type', ['Oil Sand', 'Shale Oil'])]),
            CategoricalInput('well_infrastructure', 'Count Emissions from Building Well Infrastructure',
                             defaults=[Default('yes')],
                             tooltip=Tooltip(
                                 'Emissions related to producing the iron/steel, concrete/cement, … to build the facility, amortized over the lifetime of the facility. For traditional energy product production methods, this contribution is usually very small and thus often ignored by many studies.',
                                 source='GREET2019',
                                 source_link='https://greet.es.anl.gov/',
                             )
        )
        ]

    def get_inputs(self):
        flow_dict = compute_input_flows(
            self.filtered_data_frame(),
            self.output
        )

        return {
            'primary': None,
            'secondary': [val for _, val in flow_dict.items()]
        }

    def get_emissions(self):
        return compute_emission_flows(
            self.filtered_data_frame(),
            self.output
        )
