from core import utils, conditionals, validators
from core.pathway import ActivitySource
from core.inputs import ContinuousInput, OptionsInput, CategoricalInput
from pathway.enduse.substance import Substance


class LDV(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
            ContinuousInput('amount', 'Number of miles driven', validators=[validators.numeric(), validators.gte(0)]),
            OptionsInput('mpg_source', 'MPG Source', options=["Custom", "Existing Model"]),
            ContinuousInput('mpg', 'MPG',
                            conditionals=[conditionals.input_equal_to("mpg_source", "Custom")]),
            CategoricalInput('car_size', 'Vehicle Size',
                             conditionals=[conditionals.input_equal_to("mpg_source", "Existing Model")])
        ]

    def prepare(self, input_set):
        super().prepare(input_set)
        low_heat_value = Substance('Liquid', 'Gasoline').get_lower_heat_value()
        self.output = utils.create_flow_object('gasoline', 1.0 * low_heat_value, 'MJ')

    def get_emissions(self):
        pass

    def get_inputs(self):
        return {
            'primary': self.output,
            'secondary': []
        }
