from core import utils, validators
from core.pathway import ActivitySource
from core.inputs import ContinuousInput, Default


class Electricity(ActivitySource):

    def prepare(self, input_set):
        super().prepare(input_set)
        self.output = utils.create_flow_object('electricity', 1.0, 'kWh')

    def get_inputs(self):
        return {
            'primary': self.output,
            'secondary': []
        }
