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

PATH = os.getcwd() + "/tea/electricity/storage/thermal_storage/"

class ThermalStorageTEA(Storage):
    
    # Redefining method in Storage()
    def literature_inputs(cls, storage_type = None):

        user_inputs= [
            OptionsInput('cost_source_ss', 'Select Data Source for Technology Costs', conditionals=[conditionals.input_equal_to('user_defined', 'Literature')], defaults=[Default('MIT - 2050 estimate')], options=['MIT - 2050 estimate']),
            OptionsInput('cost_scenario', 'Select Cost Scenario', conditionals=[conditionals.input_equal_to('user_defined', 'Literature')], defaults=[Default('Moderate')], options=['High','Moderate','Low']),
        ]
        if storage_type is not None:
            for user_input in user_inputs:
                user_input.conditionals.append(conditionals.input_equal_to('storage_type', 'Thermal energy storage'))

        return user_inputs

    @classmethod
    def user_inputs(cls,storage_type = None):
        inputs = [
            # Using same default values as Li-ion batteries for duration and cycling
            # 30 yr lifetime based on thermal power generators, no standalone TES system to reference from

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
        inputs.extend(cls.literature_inputs(cls,storage_type))
        inputs.extend(cls.custom_user_inputs(cls))
        return inputs

    def __init__(self, lca_pathway=None):
        self.lca_pathway = lca_pathway   
        self.finance = pd.read_csv(PATH + "finance.csv")   
        self.cost_data = pd.read_csv(PATH + "TES_data_kW.csv")