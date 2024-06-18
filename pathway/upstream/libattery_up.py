from core.pathway import ActivitySource
from core.inputs import CategoricalInput
from analysis.lca import compute_input_flows, compute_emission_flows
from core import conditionals, validators


class LiBatteryUpstream(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return []

    def get_inputs(self):
        return {
            'primary': None,
            'secondary': []
        }






