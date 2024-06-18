from core.pathway import ActivitySource
from core.inputs import CategoricalInput
from analysis.lca import compute_input_flows, compute_emission_flows
import pandas as pd


class GasolineRefining(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
            CategoricalInput('type', 'Type'),
            CategoricalInput('api', 'API'),
            CategoricalInput('location', 'Location'),
            CategoricalInput('ref_complexity', 'Refinery Complexity Index'),
            CategoricalInput('sulphur', 'Sulphur Content'),

        ]

    def get_inputs(self):
        flow_dict = compute_input_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )

        return {
            'primary': flow_dict['crude oil'],
            'secondary': [flow_dict[key] for key in flow_dict if key != 'crude oil']
        }

    def get_emissions(self):
        return compute_emission_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )
