import os
import statistics

import pandas as pd
import us

from tea.electricity.LCOE import LCOE
from core import conditionals, validators
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from core.tea import TeaBase
from analysis.sensitivity import SensitivityInput


PATH = os.getcwd() + "/tea/electricity/wind/"
TRGs = ['TRG1', 'TRG2', 'TRG3', 'TRG4', 'TRG5', 'TRG6', 'TRG7', 'TRG8', 'TRG9', 'TRG10']


class WindTEA(TeaBase):
    unit = '$/MWh'

    @classmethod
    def user_inputs(cls, with_lca=False):
        common_inputs_0 = [
            CategoricalInput(
                'region', 'Region',
                defaults=[Default('California')],
            ),
        ]
        common_inputs_1 = [
            ContinuousInput(
                'windfarm_size', 'Powerplant Size',
                unit = 'MW',
                defaults=[Default(600)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(2000)],
            ),
            ContinuousInput(
                'economies_of_scale_factor', 'Economies of Scale Factor',
                unit = 'dimensionless',
                defaults=[Default(0.7)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(1)],
            ),
            OptionsInput(
                'cost_source', 'Data Source for Tech Costs',
                options=['NREL', 'EIA'],
                defaults=[Default('NREL')],
            ),
        ]
        common_inputs_2 = [
            ContinuousInput(
                'user_trans_dist_cost', 'Transmission & Distribution Cost',
                unit='$/MWh',
                defaults=[Default(47)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(200)],
                tooltip=Tooltip(
                    '47 $/MWh is the US average transmission AND distribution cost, including 14 transmission, and 33 distribution (mainly to residential and commercial consumers). If the power is intended for industrial use, then 14 is recommended.',
                    source='EIA',
                    source_link='https://www.eia.gov/outlooks/aeo/data/browser/
                ),
            ),
            OptionsInput(
                'finance_source', 'Data Source for Finance Costs',
                options=['ATB', 'EIA', 'ReEDS'],
                defaults=[Default('ATB')],
            ),
            ContinuousInput(
                'tax_credit', 'Tax Credits',
                validators=[validators.numeric(), validators.gte(0)],
                defaults=[Default(1)],
            ),
            ContinuousInput(
                'tax_rate', 'Tax',
                unit='%',
                defaults=[Default(6.35)],
                validators=[validators.numeric(), validators.gt(0), validators.lt(100)],
                tooltip=Tooltip(
                    "The default value represents sales tax, which varies by states and specific use cases. 6.35% represents US averegae sales tax. For electricity-specific tax, 7% was found for North Carolina, and 6.25% for Texas non-residential use: https://comptroller.texas.gov/taxes/publications/96-1309.pdf.",
                    source_link='https://www.ncdor.gov/taxes-forms/sales-and-use-tax/electricity
                ),
            ),

        ]

        if with_lca:
            return common_inputs_0 + common_inputs_1 + common_inputs_2
        else:
            filters = []
            return [
                CategoricalInput(
                    'group_by', 'Group By',
                    defaults=[Default('State')],
                ),
            ] + common_inputs_0 + [
                CategoricalInput(
                    'install_type', 'Installation Type',
                    defaults=[Default('onshore')],
                ),
                OptionsInput(
                    'lifetime', 'Lifetime', unit='years',
                    options=[5, 10, 20, 30, 40],
                    defaults=[Default(20)],
                ),
            ] + common_inputs_1 + [
                ContinuousInput(
                    'transm_loss', 'Transmission Loss', unit='%',
                    defaults=[Default(4.7)],
                    validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                ),
            ] + common_inputs_2

    @classmethod
    def sensitivity(cls, lca_pathway=None):
        return [
            SensitivityInput(
                'region',
                minimizing='Florida',
                maximizing='Massachusetts',
            ),
            SensitivityInput(
                'windfarm_size',
                data_lacking=True,
            ),
            SensitivityInput(
                'economies_of_scale_factor',
                data_lacking=True,
            ),
            SensitivityInput(
                'cost_source',
                minimizing='EIA',
                maximizing='NREL',
            ),
            SensitivityInput(
                'user_trans_dist_cost',
                data_lacking=True,
            ),
            SensitivityInput(
                'finance_source',
                minimizing='EIA',
                maximizing='ReEDS',
            ),
            SensitivityInput(
                'tax_rate',
                data_lacking=True,
            ),
            SensitivityInput(
                'lifetime',
                minimizing=30,
                maximizing=10,
            ),
        ]

    def __init__(self, **kwargs):
        self.cost_by_parts = pd.read_csv(PATH + "cost_by_parts.csv")
        self.cost_multipliers = pd.read_csv(PATH + "capital_cost_multipliers.csv")
        self.finance = pd.read_csv(PATH + "finance.csv")
        self.region_speed = pd.read_csv(PATH + "region_speed_new.csv")
        self.other_costs = pd.read_csv(PATH + "wind_other_costs.csv")
        super().__init__(**kwargs)

    def prepare(self, input_set):
        super().prepare(input_set)
        if self.lca_pathway is not None:
            self.group_by = 'State'

            process = self.lca_pathway.instance('process')
            install_lca = process.install_type
            if 'offshore' in install_lca:
                self.install_type = 'offshore'
            else:
                self.install_type = 'onshore'
            self.lifetime = process.lifetime
            self.transm_loss = self.lca_pathway.instance('gatetoenduse').loss

    def get_cap_fac(self):
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

    def get_references(self):
        filtered = self.other_costs[(self.other_costs['Source'] == self.cost_source) &
                                    (self.other_costs['Type'] == self.install_type)]
        ref_windfarm = filtered[filtered['Cost Type'] == "OCC"].ref_windfarm
        return ref_windfarm 

    def get_wind_lcoe(self):
        if self.lca_pathway is not None:
            cap_fac = self.lca_pathway.instance('process').get_capacity_factor()/100
        else:
            cap_fac = self.get_cap_fac()
        cap_reg_mult = self.get_cap_reg_mult()

        filtered = self.other_costs[(self.other_costs['Source'] == self.cost_source) &
                                    (self.other_costs['Type'] == self.install_type)]
        ref_windfarm = filtered[filtered['Cost Type'] == "OCC"].ref_windfarm

        windfarm_scaling_factor = float((self.windfarm_size/ref_windfarm) ** self.economies_of_scale_factor)

        OCC = self.get_other_costs()["OCC"]
        FOM = self.get_other_costs()["FOM"]
        VOM = self.get_other_costs()["VOM"]
        finance_values = self.get_finance_values()

        lifetime = self.lifetime
        grid_cost = 0
        fuel_cost = 0
        wind_lcoe = LCOE(
            cap_fac,
            cap_reg_mult,
            1/(1 - self.transm_loss / 100) * OCC * float(ref_windfarm * windfarm_scaling_factor/self.windfarm_size),
            1/(1 - self.transm_loss / 100) * FOM,
            1/(1 - self.transm_loss / 100) * (VOM + self.user_trans_dist_cost),
            finance_values,
            lifetime,
            grid_cost,
            1/(1 - self.transm_loss / 100) * fuel_cost,
            self.tax_rate)
        return wind_lcoe

    def get_cost_breakdown(self):
        wind_lcoe = self.get_wind_lcoe()
        wind_cost_breakdown = wind_lcoe.get_cost_breakdown()
        wind_cost_breakdown['Non-fuel variable'] = 0  
        wind_cost_breakdown['Delivery'] = 1 / (1 - self.transm_loss / 100) * self.user_trans_dist_cost 
        wind_cost_breakdown['Tax'] = self.tax_rate/100 * (wind_cost_breakdown['Capital'] + wind_cost_breakdown['Fuel'] + wind_cost_breakdown['Non-fuel variable'] + wind_cost_breakdown['Delivery'])  

        return {
            key: wind_cost_breakdown[key]
            for key in ['Capital', 'Fixed', 'Fuel', 'Non-fuel variable', 'Delivery', 'Tax']
        }
