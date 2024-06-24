from core import utils, validators
from core.pathway import ActivitySource
from core.inputs import ContinuousInput, Default
from pathway.enduse.substance import Substance


class DME(ActivitySource):

    def prepare(self, input_set):
        super().prepare(input_set)
        low_heat_value = Substance('Liquid', 'Dimethyl ether (DME)').get_lower_heat_value()
        self.output = utils.create_flow_object('dimethyl ether', low_heat_value, 'MJ')

    def get_output(self):
        return utils.create_flow_object('dme', 1.0, 'kg')

    def get_inputs(self):
        return {
            'primary': self.output,
            'secondary': []
        }
