from core import utils, validators
from core.pathway import ActivitySource
from core.inputs import ContinuousInput, Default
from pathway.enduse.substance import Substance


class Concrete(ActivitySource):

    def prepare(self, input_set):
        super().prepare(input_set)
        # low_heat_value = Substance('Liquid', 'Dimethyl ether (DME)').get_lower_heat_value()
        # output flow is the heat content in MJ of the fuel per kg of the fuel
        self.output = utils.create_flow_object('concrete', 1.0, 'kg')

    def get_output(self):
        return utils.create_flow_object('concrete', 1.0, 'kg')

    def get_inputs(self):
        return {
            'primary': self.output,
            'secondary': []
        }
