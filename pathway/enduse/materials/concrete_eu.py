from core import utils, validators
from core.pathway import ActivitySource
from core.inputs import ContinuousInput, Default
from pathway.enduse.substance import Substance


class Concrete(ActivitySource):

    def prepare(self, input_set):
        super().prepare(input_set)
        self.output = utils.create_flow_object('concrete', 1.0, 'kg')

    def get_output(self):
        return utils.create_flow_object('concrete', 1.0, 'kg')

    def get_inputs(self):
        return {
            'primary': self.output,
            'secondary': []
        }
