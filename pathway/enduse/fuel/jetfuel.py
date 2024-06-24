from core import utils, validators
from core.pathway import ActivitySource
from core.inputs import CategoricalInput, ContinuousInput, OptionsInput, Default
from analysis.lca import compute_input_flows, compute_emission_flows
from pathway.enduse.substance import Substance


class  Jetfuel(ActivitySource):

    def prepare(self, input_set):
        super().prepare(input_set)
        low_heat_value = Substance('Liquid', 'Conventional Jet Fuel').get_lower_heat_value()
        self.output = utils.create_flow_object('jetfuel', 1.0 * low_heat_value, 'MJ')

    def get_output(self):
        return utils.create_flow_object('jetfuel', 1.0, 'kg')

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
