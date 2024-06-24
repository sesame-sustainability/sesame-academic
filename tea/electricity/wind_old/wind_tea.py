import os
import statistics

import pandas as pd
import us

from tea.electricity.LCOE import LCOE
from core import conditionals, validators
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput
from core.tea import TeaBase


PATH = os.getcwd() + "/tea/electricity/wind/"
TRGs = ['TRG1', 'TRG2', 'TRG3', 'TRG4', 'TRG5', 'TRG6', 'TRG7', 'TRG8', 'TRG9', 'TRG10']


class WindTEA(TeaBase):
    unit = '$/MWh'

    @classmethod
    def user_inputs(cls):
        return [
            CategoricalInput('group_by', 'Group By'),
            CategoricalInput('region', 'Region'),
            CategoricalInput('install_type', 'Installation Type'),
            OptionsInput('cost_source', 'Select Data Source for Technology Costs', defaults=[Default('NREL')], options=['NREL', 'EIA']),
            OptionsInput('finance_source', 'Select Data Source for Finance Costs', defaults=[Default('ATB')], options=['ATB', 'EIA', 'ReEDS']),
            ContinuousInput('tax_credit', 'Tax Credits', validators=[validators.numeric(), validators.gte(0)]),
        ]

    def __init__(self, lca_pathway=None):
        self.lca_pathway = lca_pathway
        self.cost_by_parts = pd.read_csv(PATH + "cost_by_parts.csv")
        self.cost_multipliers = pd.read_csv(PATH + "capital_cost_multipliers.csv")
        self.finance = pd.read_csv(PATH + "finance.csv")
        self.region_speed = pd.read_csv(PATH + "region_speed_new.csv")
        self.other_costs = pd.read_csv(PATH + "wind_other_costs.csv")
        super().__init__()

    def get_capacity_factor(self):
        region_speeds = self.region_speed[self.region_speed['Region'] == self.region]
        return float(statistics.mean(region_speeds['cap_fac']))

    def get_cap_reg_mult(self):
        if self.group_by == 'Techno-Resource Group':
            return 1
        else:
            state = us.states.lookup(self.region)
            state_cost_multipliers = self.cost_multipliers[self.cost_multipliers['State'] == state.abbr]
            return float(statistics.mean(state_cost_multipliers['cap_reg_mult']))

    def get_finance_values(self):
        finance_costs = {}
        filtered = self.finance[self.finance['Source'] == self.finance_source]
        for row in filtered.to_dict(orient='records'):
            finance_costs[row['Abbr']] = float(row['value'])
        return finance_costs

    def get_other_costs(self):
        wind_costs = {}
        filtered = self.other_costs[(self.other_costs['Source'] == self.cost_source) &
                                    (self.other_costs['Type'] == self.install_type)]
        for row in filtered.to_dict(orient='records'):
            wind_costs[row['Cost Type']] = float(row['value'])
        return wind_costs

    def get_wind_lcoe(self):
        cap_fac = self.get_capacity_factor()
        cap_reg_mult = self.get_cap_reg_mult()
        cost_values = self.get_other_costs()
        finance_values = self.get_finance_values()

        lifetime = 30
        grid_cost = 0
        fuel_cost = 0

        wind_lcoe = LCOE(cap_fac, cap_reg_mult, cost_values['OCC'], cost_values['FOM'], cost_values['VOM'], finance_values, lifetime, grid_cost, fuel_cost)
        return wind_lcoe, cap_fac

    def get_cost_breakdown(self):

        wind_lcoe, CF = self.get_wind_lcoe()
        wind_cost_breakdown = wind_lcoe.get_cost_breakdown()
        self.storage = "No"
        if self.storage == "Yes":
            self.storage_connection()
            alpha = self.r * (self.cycles / self.eta_rt) / (24 * CF)
            kWh_re = 1 / (alpha * self.eta_rt + 1 - alpha)
            kWh_sto = kWh_re * self.eta_rt
            storage_lcoe = self.storage_object.get_cost_breakdown()
            wind_cost_breakdown["Capital and Fixed"] = {'Generation':kWh_re * wind_cost_breakdown["Capital and Fixed"], 'storage':kWh_sto *storage_lcoe["Capital and Fixed"]}
            wind_cost_breakdown["Operational"] = {'Generation': kWh_re * wind_cost_breakdown["Operational"],
                                                        'storage': kWh_sto *storage_lcoe["Operational"]}
            wind_cost_breakdown["Maintenance"] = {'Generation': kWh_re * wind_cost_breakdown["Maintenance"],
                                                        'storage': kWh_sto *storage_lcoe["Maintenance"]}
        else:
            cap_cost_total = wind_cost_breakdown["Capital and Fixed"]
            cap_cost_by_part = {}
            filtered = self.cost_by_parts[self.cost_by_parts['Type'] == self.install_type]
            for row in filtered.to_dict(orient='records'):
                cap_cost_by_part[row["Item"]] = (float(row["% cost"]) * cap_cost_total) / 100.0
            wind_cost_breakdown["Capital and Fixed"] = cap_cost_by_part

        return wind_cost_breakdown
