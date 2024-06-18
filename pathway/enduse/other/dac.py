from core import utils, validators
from core.pathway import ActivitySource
from core.inputs import ContinuousInput, Default
from pathway.enduse.substance import Substance


class DAC_EU(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
            ContinuousInput('amount', 'Amount of Carbon dioxide captured in ton/year',  defaults=[Default(1)], validators=[validators.numeric(), validators.gte(0)])
        ]

    def prepare(self, input_set):
        super().prepare(input_set)
        # low_heat_value = Substance('Liquid', 'Dimethyl ether (DME)').get_lower_heat_value()
        # output flow is the heat content in MJ of the fuel per kg of the fuel
        self.output = utils.create_flow_object('dac', self.amount, 'kg')

    def get_output(self):
        return utils.create_flow_object('dac', self.amount, 'ton/year')

    def get_inputs(self):
        return {
            'primary': self.output,
            'secondary': []
        }