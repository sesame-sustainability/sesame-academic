from core.pathway import ActivitySource
from core.inputs import CategoricalInput
from analysis.lca import compute_input_flows, compute_emission_flows


class ConcreteProduction(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return []

    def get_inputs(self):
        flow_dict = compute_input_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )

        return {
            'primary': flow_dict['concrete feeds (49% gravel/35% sand/9% cement/7% water)'],
            'secondary': [flow_dict[key] for key in flow_dict if key != 'concrete feeds (49% gravel/35% sand/9% cement/7% water)']
        }

    def get_emissions(self):
        return compute_emission_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )
