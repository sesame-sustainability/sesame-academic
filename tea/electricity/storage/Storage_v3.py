"""
Date: June 6, 2021
Python class for TEA of storage technologies
@author: MITei-SESAME Seiji Engelkemier
------

Storage_v2.py replaces Storage.py and technology specific storage TEA .py files
because each storage technology has mostly the same inputs and exactly same methods.

There is also an option to use this class with the Power with Storage feature.

"""

import pandas as pd
import os

from tea.electricity.LCOE import LCOE
from core.tea import TeaBase
from core import conditionals, validators
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Option

PATH = os.getcwd() + "/tea/electricity/storage/"
PATH_cost = os.getcwd() + "/tea/electricity/storage/data/"
cost_files = {
    'Thermal': 'TES_data_kW.csv',
    'Li-ion battery': 'Li-ion_data_kW.csv',
    'Compressed Air': 'compressed_air_costs.csv'
}

# Copied from default_value_dict_creator.xlsx
# defaults_dict = {
#   var: (
#       deafult_value, 
#       [
#           ('conditional_fn','input_variable_name','input_variable_value'), 
#           more_conditionals, ...
#       ] 
#   )
# }
LiB_defaults = {
    'duration_charge': (4,[('input_equal_to','storage_tech','Li-ion battery')]),
    'duration_discharge': (4,[('input_equal_to','storage_tech','Li-ion battery')]),
    'cycles': (1,[('input_equal_to','storage_tech','Li-ion battery')]),
    'lifetime_ss': (15,[('input_equal_to','storage_tech','Li-ion battery')]),
    'finance_source_ss': ('ATB',[]),
    'user_defined': ('Literature',[]),
    # 'cost_source_ss': ('MIT - 2020 estimate',[('input_equal_to','storage_tech','Li-ion battery')]),
    # 'cost_scenario': ('Today',[('input_equal_to','storage_tech','Li-ion battery')]),
    'capex_power_charge': (0,[('input_equal_to','storage_tech','Li-ion battery')]),
    'capex_power_discharge': (298,[('input_equal_to','storage_tech','Li-ion battery')]),
    'capex_energy': (237,[('input_equal_to','storage_tech','Li-ion battery')]),
    'FOM_discharge': (7.45,[('input_equal_to','storage_tech','Li-ion battery')]),
    'FOM_charge': (0,[('input_equal_to','storage_tech','Li-ion battery')]),
    'FOM_storage': (5.92,[('input_equal_to','storage_tech','Li-ion battery')]),
    'VOM': (0.03,[('input_equal_to','storage_tech','Li-ion battery')]),
    'eta_charge': (0.92,[('input_equal_to','storage_tech','Li-ion battery')]),
    'eta_discharge': (0.92,[('input_equal_to','storage_tech','Li-ion battery')])
}

TES_defaults = {
    'duration_charge': (6,[('input_equal_to','storage_tech','Thermal')]),
    'duration_discharge': (10,[('input_equal_to','storage_tech','Thermal')]),
    'cycles': (1,[('input_equal_to','storage_tech','Thermal')]),
    'lifetime_ss': (30,[('input_equal_to','storage_tech','Thermal')]),
    'finance_source_ss': ('ATB',[]),
    'user_defined': ('Literature',[]),
    # 'cost_source_ss': ('MIT - 2050 estimate',[('input_equal_to','storage_tech','Thermal')]),
    # 'cost_scenario': ('Moderate',[('input_equal_to','storage_tech','Thermal')]),
    'capex_power_charge': (3.34,[('input_equal_to','storage_tech','Thermal')]),
    'capex_power_discharge': (706,[('input_equal_to','storage_tech','Thermal')]),
    'capex_energy': (5.4,[('input_equal_to','storage_tech','Thermal')]),
    'FOM_discharge': (3.93,[('input_equal_to','storage_tech','Thermal')]),
    'FOM_charge': (0.08,[('input_equal_to','storage_tech','Thermal')]),
    'FOM_storage': (0.03,[('input_equal_to','storage_tech','Thermal')]),
    'VOM': (0,[('input_equal_to','storage_tech','Thermal')]),
    'eta_charge': (0.995,[('input_equal_to','storage_tech','Thermal')]),
    'eta_discharge': (0.5,[('input_equal_to','storage_tech','Thermal')])
}

CAES_defaults = {
    'duration_charge': (6,[('input_equal_to','storage_tech','Compressed Air')]),
    'duration_discharge': (10,[('input_equal_to','storage_tech','Compressed Air')]),
    'cycles': (1,[('input_equal_to','storage_tech','Compressed Air')]),
    'lifetime_ss': (30,[('input_equal_to','storage_tech','Compressed Air')]),
    'finance_source_ss': ('ATB',[]),
    'user_defined': ('Literature',[]),
    # 'cost_source_ss': ('MIT estimate',[('input_equal_to','storage_tech','Compressed Air')]),
    # 'cost_scenario': (2020,[('input_equal_to','storage_tech','Compressed Air')]),
    'capex_power_charge': (452,[('input_equal_to','storage_tech','Compressed Air')]),
    'capex_power_discharge': (617,[('input_equal_to','storage_tech','Compressed Air')]),
    'capex_energy': (53.2,[('input_equal_to','storage_tech','Compressed Air')]),
    'FOM_discharge': (8.7,[('input_equal_to','storage_tech','Compressed Air')]),
    'FOM_charge': (0,[('input_equal_to','storage_tech','Compressed Air')]),
    'FOM_storage': (0,[('input_equal_to','storage_tech','Compressed Air')]),
    'VOM': (0,[('input_equal_to','storage_tech','Compressed Air')]),
    'eta_charge': (0.737,[('input_equal_to','storage_tech','Compressed Air')]),
    'eta_discharge': (0.795,[('input_equal_to','storage_tech','Compressed Air')])
}

class StorageTEA(TeaBase):
    unit = '$/MWh'

    # Is this correct use of @staticmethod ?
    @staticmethod
    def set_user_inputs_default(inputs,defaults_dict):
        """
        Returns inputs with defaults
        Applies default value and conditionals on default value to inputs from defaults_dict
        defaults_dict = [value, [('conditional_fn','input_variable_name','input_variable_value'),...] ]
        """
        for key, val_set in defaults_dict.items():
            for input in inputs:
                if input.name == key:
                    value = val_set[0]
                    conditionals_list = val_set[1]
                    conds = []
                    for conditional_tuple in conditionals_list:
                        fn = conditional_tuple[0]
                        var_name = conditional_tuple[1]
                        var_value = conditional_tuple[2]
                        # Some unicode issue
                        # https://stackoverflow.com/questions/10993612/how-to-remove-xa0-from-string-in-python
                        var_value = var_value.replace(u'\xa0', u' ')

                        if fn == 'input_equal_to':
                            conds.append(conditionals.input_equal_to(var_name,var_value))
                        else:
                            print('Conditional function not implemented')
                    input.defaults.append(Default(value,conditionals=conds))
        return inputs

    @classmethod
    def user_inputs(cls,with_lca=False, power_storage=False):
        storage_tech_options = ['Li-ion battery', 'Thermal', 'Compressed Air']

        common_inputs_0 = [
            OptionsInput('storage_tech', 'Select storage technology', 
                defaults=[Default('Li-ion battery')], 
                options=storage_tech_options
            ),
            # Operational parameters
            # TO-DO: create or modify the validator such that the capacity factor is between 0 and 1
            # defaults=[Default(4,conditionals.input_equal_to('storage_tech', 'Li-ion battery'))]
            ContinuousInput('duration_charge','Charge Duration (hr)', 
                validators=[validators.numeric(), validators.gt(0)]
            ),
            ContinuousInput('duration_discharge','Discharge Duration (hr)',
                validators=[validators.numeric(), validators.gt(0)]
            ),
            ContinuousInput('cycles','Cycles per day',
                validators=[validators.numeric(), validators.gt(0)]
            ),
            ContinuousInput('lifetime_ss','Lifetime (yr)', 
                validators=[validators.numeric(), validators.integer(), validators.gt(0)]
            ),

            # Financial parameters
            OptionsInput('finance_source_ss', 'Select Data Source for Finance Costs', 
                defaults=[Default('ATB')], 
                options=['ATB', 'EIA', 'ReEDS']
            ),

            # Cost data
            OptionsInput('user_defined', 'Use literature or custom values', 
                defaults=[Default('Literature')], 
                options=['Literature','Custom']
            ),
        ]
        
        custom_cost_inputs = [
            ContinuousInput('capex_power_charge','Charging Capital Cost [$/kW_e]',validators=[validators.numeric(), validators.gte(0)]),
            ContinuousInput('capex_power_discharge','Discharging Capital Cost [$/kW_e]', validators=[validators.numeric(), validators.gte(0)]),
            ContinuousInput('capex_energy','Energy Capital Cost, [$/kWh_x e.g. kWh_thermal]', validators=[validators.numeric(), validators.gte(0)]),
            ContinuousInput('FOM_discharge','FOM discharge[$/kW_e-yr]', validators=[validators.numeric(), validators.gte(0)]),
            ContinuousInput('FOM_charge','FOM charge [$/kW_e-yr]', validators=[validators.numeric(), validators.gte(0)]),
            ContinuousInput('FOM_storage','FOM storage [$/kWh-yr]', validators=[validators.numeric(), validators.gte(0)]),
            ContinuousInput('VOM','VOM [$/kWh_e]', validators=[validators.numeric(), validators.gte(0)]),
            ContinuousInput('eta_charge','Efficiency up (charge) [fraction]', validators=[validators.numeric(), validators.gte(0), validators.lte(1)]),
            ContinuousInput('eta_discharge','Efficiency down (discharge) [fraction]', validators=[validators.numeric(), validators.gte(0), validators.lte(1)])
        ]
        for user_input in custom_cost_inputs:
            user_input.conditionals.append(conditionals.input_equal_to('user_defined', 'Custom'))

        literature_options = [
            OptionsInput(
                'cost_source_ss', 'Select Data Source for Technology Costs',
                defaults=[
                    Default('MIT - 2020 estimate', conditionals=[conditionals.input_equal_to('storage_tech', 'Li-ion battery')]),
                    Default('MIT - 2050 estimate', conditionals=[conditionals.input_equal_to('storage_tech', 'Thermal')]),
                    Default('MIT estimate', conditionals=[conditionals.input_equal_to('storage_tech', 'Compressed Air')]),
                ],
                options=[
                    Option('MIT - 2020 estimate', conditionals=[conditionals.input_equal_to('storage_tech', 'Li-ion battery')]),
                    Option('MIT - 2050 estimate', conditionals=[conditionals.input_equal_to('storage_tech', 'Thermal')]),
                    Option('MIT estimate', conditionals=[conditionals.input_equal_to('storage_tech', 'Compressed Air')]),
                ],
                conditionals=[
                    conditionals.input_equal_to('user_defined', 'Literature')
                ]
            ),
            OptionsInput(
                'cost_scenario', 'Select Cost Scenario',
                defaults=[
                    Default('Today', conditionals=[conditionals.input_equal_to('storage_tech', 'Li-ion battery')]),
                    Default('Moderate', conditionals=[conditionals.input_equal_to('storage_tech', 'Thermal')]),
                    Default(2020, conditionals=[conditionals.input_equal_to('storage_tech', 'Compressed Air')]),
                ],
                options=[
                    Option('Today', conditionals=[conditionals.input_equal_to('storage_tech', 'Li-ion battery')]),
                    Option('High', conditionals=[conditionals.input_equal_to('storage_tech', 'Thermal')]),
                    Option('Moderate', conditionals=[conditionals.input_equal_to('storage_tech', 'Thermal')]),
                    Option('Low', conditionals=[conditionals.input_equal_to('storage_tech', 'Thermal')]),
                    Option(2020, conditionals=[conditionals.input_equal_to('storage_tech', 'Compressed Air')]),
                    Option(2050, conditionals=[conditionals.input_equal_to('storage_tech', 'Compressed Air')]),
                ],
                conditionals=[
                    conditionals.input_equal_to('user_defined', 'Literature')
                ]
            ),
        ]


        if with_lca:
            # Not setup for LCA
            pass
        else:
            if power_storage:
                return common_inputs_0 + literature_options
            else:
                inputs = common_inputs_0 + custom_cost_inputs + literature_options
                # Append default values
                inputs = cls.set_user_inputs_default(inputs,LiB_defaults)
                inputs = cls.set_user_inputs_default(inputs,TES_defaults)
                inputs = cls.set_user_inputs_default(inputs,CAES_defaults)
                return inputs
        
    # How to deal with file names and paths?
    def __init__(self, power_storage_dict=None, *args, **kwargs):
        self.finance = pd.read_csv(PATH + "finance.csv")   
        # Can't initialize cost data here because haven't selected values for user input yet
        # self.cost_data = pd.read_csv(PATH + "storage_data.csv")
        super().__init__(*args, **kwargs)

        # Args passed in from PowerAndStorageTEA class
        if power_storage_dict != None:
            self.storage_tech = power_storage_dict['storage_tech']
            self.duration_charge = power_storage_dict['t_c']
            self.duration_discharge = power_storage_dict['t_d']
            self.cycles = power_storage_dict['cycles']
            self.lifetime_ss = power_storage_dict['lifetime']
            self.finance_source_ss = 'EIA'
            self.user_defined = 'Literature'
            self.cost_source_ss = power_storage_dict['cost_source_ss']
            self.cost_scenario = power_storage_dict['cost_scenario']


    def load_cost_data(self):
        self.cost_data = pd.read_csv(os.path.join(PATH_cost, cost_files[self.storage_tech]))
        return None

    # Does storage CF include charge duration?
    def get_capacity_factor(self):
        cf = self.cycles * self.duration_discharge * 365 / 8760
        return cf

    def get_cycles(self):
        return self.cycles

    def get_eta(self):
        if self.user_defined == 'Literature':
            df = self.cost_data[(self.cost_data['Source'] == self.cost_source_ss) & (self.cost_data['Cost Scenario'] == self.cost_scenario)]
            eta_charge = df.loc[df['Variable'] == 'Efficiency up']["Value"].item() 
            eta_discharge = df.loc[df['Variable'] == 'Efficiency down']["Value"].item() 
        elif self.user_defined == 'Custom':
            eta_charge = self.eta_charge
            eta_discharge = self.eta_discharge  
        return eta_charge, eta_discharge

    def get_finance_values(self):
        finance_costs = {}
        filtered = self.finance[self.finance['Source'] == self.finance_source_ss]
        for row in filtered.to_dict(orient='records'):
            finance_costs[row['Abbr']] = float(row['value'])
        return finance_costs

    def get_cost_values(self):
        storage_costs = {}
        if self.user_defined == 'Literature':
            df = self.cost_data[(self.cost_data['Source'] == self.cost_source_ss) & (self.cost_data['Cost Scenario'] == self.cost_scenario)]
            capex_power_charge = df.loc[df['Variable'] == 'Charging Capital Cost']["Value"].item() 
            capex_power_discharge = df.loc[df['Variable'] == 'Discharging Capital Cost']["Value"].item() 
            capex_energy = df.loc[df['Variable'] == 'Energy Capital Cost']["Value"].item()      
            
            FOM_discharge = df.loc[df['Variable'] == 'FOM discharge']["Value"].item() 
            FOM_charge = df.loc[df['Variable'] == 'FOM charge']["Value"].item() 
            FOM_storage = df.loc[df['Variable'] == 'FOM storage']["Value"].item() 

            # VOM recorded as $/MWh, which SESAME's LCOE() expects
            VOM = df.loc[df['Variable'] == 'VOM']["Value"].item()
            
            eta_charge = df.loc[df['Variable'] == 'Efficiency up']["Value"].item() 
            eta_discharge = df.loc[df['Variable'] == 'Efficiency down']["Value"].item() 
        elif self.user_defined == 'Custom':
            capex_power_charge =  self.capex_power_charge
            capex_power_discharge = self.capex_power_discharge
            capex_energy = self.capex_energy
            FOM_discharge = self.FOM_discharge
            FOM_charge = self.FOM_charge
            FOM_storage = self.FOM_storage
            VOM = self.VOM
            eta_charge = self.eta_charge
            eta_discharge = self.eta_discharge                
        
        # Overnight Capital Cost (OCC) expressed in $/kW_e produced
        # Convert charging cost from $/kW_in to $/kW_out with roundtrip efficiency and ratio of duration
        # Convert energy cost from "native" units, e.g. kWh_thermal, to kWh_elec
        ratio = self.duration_discharge/self.duration_charge * 1/(eta_charge*eta_discharge)
        storage_costs["OCC"] = capex_power_discharge + (capex_power_charge * ratio) + (capex_energy/eta_discharge * self.duration_discharge)
        storage_costs["FOM"] = FOM_discharge + (FOM_charge * ratio) + (FOM_storage/eta_discharge * self.duration_discharge)
        storage_costs["VOM"] = VOM

        return storage_costs               

    def get_storage_lcoe(self):
        self.load_cost_data()
        cap_fac = self.get_capacity_factor()
        # cap_reg_mult = self.get_cap_reg_mult()
        cap_reg_mult = 1
        cost_values = self.get_cost_values()
        finance_values = self.get_finance_values()

        lifetime = self.lifetime_ss
        grid_cost = 0
        fuel_cost = 0

        storage_lcoe = LCOE(cap_fac, cap_reg_mult, cost_values['OCC'], cost_values['FOM'],cost_values['VOM'], finance_values, lifetime, grid_cost, fuel_cost)
        return storage_lcoe

    def get_cost_breakdown(self):
        lcoe = self.get_storage_lcoe()
        cost_breakdown = lcoe.get_cost_breakdown()
        return cost_breakdown 