from core.pathway import ActivitySource
from core.inputs import CategoricalInput
from analysis.lca import compute_input_flows, compute_emission_flows
import pandas as pd

class DieselProduction(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
            CategoricalInput('type', 'Type'),
            CategoricalInput('api', 'API'),
            CategoricalInput('location', 'Location'),
            CategoricalInput('ref_complexity','Refinery Complexity index'),
            CategoricalInput('sulphur', 'Sulphur Content'),

        ]

    def get_inputs(self):
        df = self._get_df()
        flow_dict = compute_input_flows(df, flow_output=self.output)

        return {
            'primary': flow_dict['crude oil'],
            'secondary': [flow_dict[key] for key in flow_dict if key != 'crude oil']
        }

    def get_output(self):
        return self.output

    def get_emissions(self):
        df = self._get_df()
        return compute_emission_flows(df, flow_output=self.output)

    def get_cost(self):
        pass

    def _get_df(self):
        df = self.data_frame()
        df = df[df['Type'] == self.type]
        df = df[df['API'] == self.api]
        df = df[df['Location'] == self.location]
        df = df[df['Refinery Complexity index'] == self.ref_complexity]
        df = df[df['Sulphur Content'] == self.sulphur]

        return df
