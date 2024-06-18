import os
# import statistics
# from pathlib import Path

import pandas as pd
# import us

from tea.electricity.storage.Storage import Storage
# from tea.electricity.LCOE import LCOE
from core import conditionals, validators
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput
# from core.tea import TeaBase

PATH = os.getcwd() + "/tea/electricity/storage/compressed_air/"

class CompressedAirTEA(Storage):

    def literature_inputs(cls,storage_type = None):
        user_inputs = [
            OptionsInput('cost_source_ss', 'Select Data Source for Technology Costs', conditionals=[conditionals.input_equal_to('user_defined', 'Literature')], defaults=[Default('MIT estimate')], options=['MIT estimate']),
            OptionsInput('cost_scenario', 'Select Cost Scenario', conditionals=[conditionals.input_equal_to('user_defined', 'Literature')], defaults=[Default(2020)], options=[2020, 2050]),
        ]
        if storage_type is not None:
            for user_input in user_inputs:
                user_input.conditionals.append(conditionals.input_equal_to('storage_type', 'Compressed air energy storage'))

        return user_inputs

    @classmethod
    def user_inputs(cls, storage_type=None):
        inputs = [
            # Using same default values as Li-ion batteries for duration and cycling
            # 30 yr lifetime typical for gas turbines. Two existing CAES plants have been in operation for ~30 years as of 2021.

            ContinuousInput('duration_charge','Charge Duration (hr)', defaults=[Default(4)], validators=[validators.numeric(), validators.gt(0)]),
            ContinuousInput('duration_discharge','Discharge Duration (hr)', defaults=[Default(4)], validators=[validators.numeric(), validators.gt(0)]),
            ContinuousInput('cycles','Cycles per day', defaults=[Default(1)], validators=[validators.numeric(), validators.gt(0)]),
            ContinuousInput('lifetime_ss','Lifetime (yr)', defaults=[Default(30)], validators=[validators.numeric(), validators.integer(), validators.gt(0)]),

            # Financial parameters
            OptionsInput('finance_source_ss', 'Select Data Source for Finance Costs', defaults=[Default('ATB')], options=['ATB', 'EIA', 'ReEDS']),

            # Cost data
            OptionsInput('user_defined', 'Use literature or custom values', defaults=[Default('Literature')], options=['Literature','Custom']),
        ]
        # Method will return inputs depending on choice for "user_defined". Other option ignored using conditionals.
        inputs.extend(cls.literature_inputs(cls, storage_type))
        inputs.extend(cls.custom_user_inputs(cls))
        return inputs
    
    def __init__(self, lca_pathway=None):
        self.lca_pathway = lca_pathway   
        self.finance = pd.read_csv(PATH + "finance.csv")   
        self.cost_data = pd.read_csv(PATH + "compressed_air_costs.csv")