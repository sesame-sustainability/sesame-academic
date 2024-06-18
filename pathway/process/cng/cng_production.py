from core.pathway import ActivitySource
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from analysis.lca import compute_input_flows, compute_emission_flows


class CNGProduction(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
        ]

    def get_inputs(self):
        flow_dict = compute_input_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )

        return {
            'primary': flow_dict['natural gas'],
            'secondary': [flow_dict[key] for key in flow_dict if key != 'natural gas']
        }

    def get_emissions(self):
        return compute_emission_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )
