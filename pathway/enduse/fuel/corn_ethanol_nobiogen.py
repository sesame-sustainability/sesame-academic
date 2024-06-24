from core import utils, validators
from core.pathway import ActivitySource
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from pathway.enduse.substance import Substance
from analysis.lca import compute_input_flows, compute_emission_flows

class Corn_ethanol_nobiogen(ActivitySource):

    def prepare(self, input_set):
        super().prepare(input_set)
        low_heat_value = Substance('Liquid', 'Ethanol').get_lower_heat_value()
        self.output = utils.create_flow_object('ethanol', 1.0, 'MJ')

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
