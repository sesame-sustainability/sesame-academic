from core.pathway import ActivitySource
from core.inputs import CategoricalInput
from analysis.lca import compute_input_flows, compute_emission_flows

class Crude(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
            CategoricalInput('location', 'Location'),
            CategoricalInput('efficiency', 'Efficiency')
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
