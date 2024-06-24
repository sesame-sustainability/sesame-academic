from core import utils, validators
from core.pathway import ActivitySource
from core.inputs import ContinuousInput, Default
from pathway.enduse.substance import Substance


class LiBattery(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
            ContinuousInput('amount', 'Battery Capacity in kWh',  defaults=[Default(1)], validators=[validators.numeric(), validators.gte(0)])
        ]

    def prepare(self, input_set):
        super().prepare(input_set)
        self.output = utils.create_flow_object('li battery', self.amount, 'kWh')

    def get_output(self):
        return utils.create_flow_object('li battery', self.amount, 'kWh')

    def get_inputs(self):
        return {
            'primary': self.output,
            'secondary': []
        }
