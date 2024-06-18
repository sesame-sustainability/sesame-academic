import os
import statistics
from pathlib import Path

import pandas as pd
# import us

from tea.electricity.LCOE import LCOE
from core import conditionals, validators
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput
from core.tea import TeaBase

PATH = os.getcwd() + "/tea/electricity/storage/thermal_storage/"

class ThermalStorageTEA(TeaBase):

    @classmethod
    def user_inputs(cls, generation = "No"):
        if generation == "Yes":
            return [ContinuousInput('r', 'Storage capacity to renewable power ratio [Wh/W]',
                                       validators=[validators.numeric(), validators.gt(0)],
                    conditionals=[conditionals.input_equal_to('storage', 'Yes')]),
                    OptionsInput('cost_source_ss', 'Select Data Source for Technology Costs',
                                  defaults=[Default('MIT - 2050 estimate')], options=['MIT - 2050 estimate'],
                                 conditionals=[conditionals.input_equal_to('storage', 'Yes')]),
                     OptionsInput('cost_scenario', 'Select Cost Scenario', defaults=[Default('Moderate')],
                                  options=['High', 'Moderate', 'Low'],conditionals=[conditionals.input_equal_to('storage', 'Yes')]),
                     OptionsInput('finance_source_ss', 'Select Data Source for Finance Costs', defaults=[Default('ATB')],
                                  options=['ATB', 'EIA', 'ReEDS'],conditionals=[conditionals.input_equal_to('storage', 'Yes')]),
                     ContinuousInput('lifetime_ss', 'Lifetime of storage system', defaults=[Default(30)],
                                     validators=[validators.numeric(), validators.integer(), validators.gt(0)],conditionals=[conditionals.input_equal_to('storage', 'Yes')]),
                     ContinuousInput('cycles', 'Cycles per day', validators=[validators.numeric(), validators.gt(0)],conditionals=[conditionals.input_equal_to('storage', 'Yes')]),
                     ContinuousInput('duration_charge', 'Charge Duration (hr)',
                                     validators=[validators.numeric(), validators.gt(0)],conditionals=[conditionals.input_equal_to('storage', 'Yes')]),
                     ContinuousInput('duration_discharge', 'Discharge Duration (hr)',
                                     validators=[validators.numeric(), validators.gt(0)],conditionals=[conditionals.input_equal_to('storage', 'Yes')])
                     ]
        else:
            return [OptionsInput('cost_source_ss', 'Select Data Source for Technology Costs', defaults=[Default('MIT - 2050 estimate')], options=['MIT - 2050 estimate']),
                OptionsInput('cost_scenario', 'Select Cost Scenario', defaults=[Default('Moderate')], options=['High','Moderate','Low']),
                OptionsInput('finance_source_ss', 'Select Data Source for Finance Costs', defaults=[Default('ATB')], options=['ATB', 'EIA', 'ReEDS']),
                ContinuousInput('lifetime_ss', 'Lifetime of storage system', defaults=[Default(30)],
                                  validators=[validators.numeric(), validators.integer(), validators.gt(0)]),
                ContinuousInput('cycles', 'Cycles per day', validators=[validators.numeric(), validators.gt(0)]),
                ContinuousInput('duration_charge', 'Charge Duration (hr)',
                                  validators=[validators.numeric(), validators.gt(0)]),
                ContinuousInput('duration_discharge', 'Discharge Duration (hr)',
                                  validators=[validators.numeric(), validators.gt(0)])
                ]
    
    def __init__(self, lca_pathway=None):
        self.lca_pathway = lca_pathway   
        self.finance = pd.read_csv(PATH + "finance.csv")   
        self.cost_data = pd.read_csv(PATH + "TES_data_kW.csv")

    # Set to 1 in get_storage_lcoe()

    # def get_cap_reg_mult(self):
    #     if self.group_by == 'Techno-Resource Group':
    #         return 1
    #     else:
    #         state_cost_multipliers = self.cost_multipliers[self.cost_multipliers['State'] == self.state.abbr]
    #         return float(statistics.mean(state_cost_multipliers['cap_reg_mult']))
    def get_storage_rte(self):
        return 1
    def get_cap_fac(self):
        cf = self.cycles * self.duration_discharge * 365 / 8760
        return cf

    def get_finance_values(self):
        finance_costs = {}
        filtered = self.finance[self.finance['Source'] == self.finance_source_ss]
        for row in filtered.to_dict(orient='records'):
            finance_costs[row['Abbr']] = float(row['value'])
        return finance_costs

    def get_cost_values(self):
        storage_costs = {}
        df = self.cost_data[(self.cost_data['Source'] == self.cost_source_ss) & (self.cost_data['Cost Scenario'] == self.cost_scenario)]
                
        capex_power_charge = df.loc[df['Variable'] == 'Charging Capital Cost']["Value"].item() 
        capex_power_discharge = df.loc[df['Variable'] == 'Discharging Capital Cost']["Value"].item() 
        capex_energy = df.loc[df['Variable'] == 'Energy Capital Cost']["Value"].item()      
        
        FOM_discharge = df.loc[df['Variable'] == 'FOM discharge']["Value"].item() 
        FOM_charge = df.loc[df['Variable'] == 'FOM charge']["Value"].item() 
        FOM_storage = df.loc[df['Variable'] == 'FOM storage']["Value"].item() 

        VOM = df.loc[df['Variable'] == 'VOM']["Value"].item() 
        
        eta_charge = df.loc[df['Variable'] == 'Efficiency up']["Value"].item() 
        eta_discharge = df.loc[df['Variable'] == 'Efficiency down']["Value"].item() 

        # Overnight Capital Cost (OCC) expressed in $/kW_e produced
        # Convert charging cost from $/kW_in to $/kW_out with roundtrip efficiency and ratio of duration
        # Convert energy cost from "native" units, e.g. thermal, to electricity
        ratio = self.duration_discharge/self.duration_charge * 1/(eta_charge*eta_discharge)
        storage_costs["OCC"] = capex_power_discharge + (capex_power_charge * ratio) + (capex_energy/eta_discharge * self.duration_discharge)
        storage_costs["FOM"] = FOM_discharge + (FOM_charge * ratio) + (FOM_storage/eta_discharge * self.duration_discharge)
        storage_costs["VOM"] = VOM

        return storage_costs               

    def get_storage_lcoe(self):
        cap_fac = self.get_cap_fac()
        # cap_reg_mult = self.get_cap_reg_mult()
        cap_reg_mult = 1
        cost_values = self.get_cost_values()
        finance_values = self.get_finance_values()

        lifetime = self.lifetime_ss
        grid_cost = 0
        fuel_cost = 0

        storage_lcoe = LCOE(cap_fac, cap_reg_mult, cost_values, finance_values, lifetime, grid_cost, fuel_cost)
        return storage_lcoe

    def get_cost_breakdown(self):
        lcoe = self.get_storage_lcoe()
        cost_breakdown = lcoe.get_cost_breakdown()
        return cost_breakdown

        # storage_lcoe = self.get_storage_lcoe()
        # storage_cost_breakdown = storage_lcoe.get_cost_breakdown()
        # cap_cost_total = storage_cost_breakdown["Capital and Fixed"]
        # cap_cost_by_part = {}
        # for row in self.cost_by_parts.to_dict(orient='records'):
        #     cap_cost_by_part[row["Item"]] = (float(row["% cost"]) * cap_cost_total) / 100.0

        # storage_cost_breakdown["Capital and Fixed"] = cap_cost_by_part
        # return storage_cost_breakdown