from core.pathway import ActivitySource
from core.inputs import ContinuousInput, CategoricalInput, Default
from core import conditionals, validators
from analysis.lca import compute_input_flows, compute_emission_flows
import core.validators as validators
import sys
import pandas as pd
import os

class HydroPowerGREET(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
            CategoricalInput('generation_region', 'Generation Region', defaults=[Default('US')])
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
            flow_output=self.output
        )



