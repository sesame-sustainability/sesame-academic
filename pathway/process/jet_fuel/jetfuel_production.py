from core.pathway import ActivitySource
from analysis.lca import compute_input_flows, compute_emission_flows
from core.inputs import CategoricalInput, ContinuousInput, OptionsInput, Default
import pandas as pd

class JetFuelProduction(ActivitySource):

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
            'primary': flow_dict['petroleum'],
            'secondary': [flow_dict[key] for key in flow_dict if key != 'petroleum']
        }

    def get_emissions(self):
        return compute_emission_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )
