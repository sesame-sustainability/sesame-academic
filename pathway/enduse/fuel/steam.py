from core import utils, validators
from core.pathway import ActivitySource
from core.inputs import ContinuousInput, Default
from pathway.enduse.substance import Substance


class Steam(ActivitySource):

    def get_inputs(self):
        self.output = utils.create_flow_object('steam', 1.0, 'MJ')
        return {
            'primary': self.output,
            'secondary': []
        }
