from core.pathway import ActivitySource
from core.inputs import CategoricalInput
from analysis.lca import compute_input_flows, compute_emission_flows


class SteelProduction(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
            CategoricalInput('steel_type', 'Steel Type')
        ]

    def get_inputs(self):
        flow_dict = compute_input_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )

        return {
            'primary': flow_dict['iron ore'],
            'secondary': [flow_dict[key] for key in flow_dict if key != 'iron ore']
        }

    def get_emissions(self):
        return compute_emission_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )
