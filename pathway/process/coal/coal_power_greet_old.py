from core.pathway import ActivitySource
from core.inputs import CategoricalInput, Default
from analysis.lca import compute_input_flows, compute_emission_flows


class CoalPowerGREET(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
            CategoricalInput('coal_rank', 'Coal Rank',
                             defaults=[Default('Mix (50% bituminous_40% Sub-bituminous_4.4% lignite_5.1% other)')]),
            CategoricalInput('generation_region',
                             'Generation Region', defaults=[Default('US')]),
            CategoricalInput('generator_type', 'Generator Type',
                             defaults=[Default('Mix')]),
            CategoricalInput('infrastructure_emission_inclusion', 'Include Infrastructure Emissions?',
                             defaults=[Default('Yes')])
        ]

    def get_inputs(self):
        flow_dict = compute_input_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )
        return {
            'primary': flow_dict['coal'],
            'secondary': []
        }

    def get_emissions(self):
        return compute_emission_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )
