"""
Created on January 14, 2022
@author: sydney johnson
"""
import json
import os
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import re
from core.common import InputSource, Versioned
import core.conditionals as conditionals
from core.inputs import OptionsInput, ContinuousInput, PercentInput, Default, InputSet
from core.model import ModelComposer
from analysis.system.industrial_fleet.iron_steel_projections import SteelProjection
from analysis.system.industrial_fleet.cement_projections import CementProjection
#Main Industrial Fleet Model to access industries: Steel,Cement,Aluminium, etc.

class IndFleetModel(InputSource, Versioned):
    version = 1

    industries = [
        ('Steel', SteelProjection),
        ('Cement', CementProjection),
    ]

    @classmethod
    def user_inputs(cls):
        inputs = [
            OptionsInput(
                'industry', 'Industry',
                options=[ind for ind, model in cls.industries],
                defaults=[Default('Steel')],
            ),
        ]

        composer = ModelComposer(cls.industries, 'industry')
        return inputs + composer.merged_inputs()

    def run(self):
        if self.industry == 'Steel':
            self.model = SteelProjection()
        elif self.industry == 'Cement':
            self.model = CementProjection()
        else:
            raise Exception(f'invalid industry: {self.industry}')

        composer = ModelComposer(self.industries, 'industry')
        composer.prepare(self.input_set, self.model)

        return self.model.run()

    def figures(self, results):
        return self.model.figures(results)

    def plot(self, results):
        return self.model.plot(results)
