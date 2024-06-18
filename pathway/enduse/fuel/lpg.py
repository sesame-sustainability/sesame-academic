from core import utils, validators
from core.pathway import ActivitySource
from core.inputs import ContinuousInput, Default
from pathway.enduse.substance import Substance
from analysis.lca import compute_input_flows, compute_emission_flows


class LPG(ActivitySource):

    def prepare(self, input_set):
        super().prepare(input_set)
        low_heat_value = Substance('Liquid', 'Liquefied petroleum gas (LPG)').get_lower_heat_value()
        self.output = utils.create_flow_object('lpg', 1.0, 'MJ')

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
