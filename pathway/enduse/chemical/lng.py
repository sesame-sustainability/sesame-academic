from core import utils, validators
from core.pathway import ActivitySource
from core.inputs import ContinuousInput, Default
from pathway.enduse.substance import Substance


class LNG(ActivitySource):

    def prepare(self, input_set):
        super().prepare(input_set)
        low_heat_value = Substance('Liquid', 'Liquefied natural gas (LNG)').get_lower_heat_value()
        self.output = utils.create_flow_object('lng', 1.0 * low_heat_value, 'MJ')

    def get_output(self):
        return utils.create_flow_object('lng', 1.0, 'kg')

    def get_inputs(self):
        return {
            'primary': self.output,
            'secondary': []
        }
