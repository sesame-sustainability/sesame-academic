import os

import pandas as pd

from core.pathway import ActivitySource
from core.inputs import ContinuousInput, Default, Tooltip
import core.validators as validators
from analysis.sensitivity import SensitivityInput

default_loss = 4.7 

class Transmission(ActivitySource):

    @classmethod
    def user_inputs(cls):

        return [
            ContinuousInput(
                'loss', 'Power Lost in Transmission',
                unit='%',
                defaults=[Default(default_loss)],
                tooltip=Tooltip(' ', source='Average of 2018 EPA & EIA values',
                                source_link='https://greet.es.anl.gov/files/Update_td_losses_2018'),
                validators=[validators.numeric(), validators.lt(100), validators.gte(0)],
            ),
        ]

    @classmethod
    def sensitivity(cls):
        return [
            SensitivityInput(
                'loss',
                minimizing=default_loss *0.7,
                maximizing=default_loss *1.3,
            ),
        ]

    def get_inputs(self):
        primary = self.output.copy()
        primary['value'] = self.output['value'] / (1 - 0.01 * self.loss)

        return {
            'primary': primary,
            'secondary': []
        }
