from core import utils, validators
from core.pathway import ActivitySource
from core.inputs import ContinuousInput, Default
from pathway.enduse.substance import Substance
from analysis.lca import compute_input_flows, compute_emission_flows


class CNG(ActivitySource):

    def prepare(self, input_set):
        super().prepare(input_set)
        self.output = utils.create_flow_object('cng', 1.0 , 'MJ')
# CNG doesn't have a gate to user transportation module because compression and end use are usually co-located. CNG transportation data was not found in GREET 2019.
    def get_inputs(self):
        return {
            'primary': self.output,
            'secondary': []
        }

    def get_emissions(self):
        return compute_emission_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )
