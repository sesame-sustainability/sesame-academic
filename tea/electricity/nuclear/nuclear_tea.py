"""
Created on Tue Jan 26 10:44:43 2021

@author: brendanwagner
"""

import os
import statistics

import pandas as pd
import us

from tea.electricity.LCOE import LCOE
from core import conditionals, validators
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from core.tea import TeaBase


PATH = os.getcwd() + "/tea/electricity/nuclear/"



class NuclearTEA(TeaBase):

    @classmethod
    def user_inputs(cls):
        return [
            OptionsInput(
                'reactor_type', 'Reactor Type',
                defaults = [Default('PWR')],
                options = ['PWR', 'HTGR', 'SMR'],
                tooltip = Tooltip(
                    "LWR=Light Water Reactor; HTGR= High-Temperature Gas-Cooled Reactor; most US nuclear reactors are LWR. PWR=Pressurized Water Reactor; BRW=Boiling Water Reactor; according to GREET assumption, all US LWR are PWR. Caveat: GREET 2019 model is used here for LCA, but it only includes emissions related to uranium extraction/processing/transportation and power plant infrastructure. Other contributors such as plant decomissioning are not included.",
                    source='GREET2019',
                    source_link='https://greet.es.anl.gov/',
                ),
            ),

            ContinuousInput(
                'occ', 'Capital Cost',
                unit='$/kW',
                defaults=[
                    Default('6041', conditionals=[conditionals.input_equal_to('reactor_type', 'PWR')]),
                    Default('5200', conditionals=[conditionals.input_not_equal_to('reactor_type', 'HTGR')]),
                    Default('6191', conditionals=[conditionals.input_not_equal_to('reactor_type', 'SMR')]),
                    ],
                validators=[validators.numeric(), validators.integer(), validators.gt(0)],
                tooltip=Tooltip(
                    "Capital cost is the major cost contributor to nuclear power, and the capital cost has large variability, especially for relatively new technologies (HTGR, SMR), so we make the input flexible here. Large variation can be noticed, e.g., in Figure 12 of https://www.sciencedirect.com/science/article/pii/S0301421516300106. PWR dominates LWR in the US.",
                    source='MIT Future of Nuclear',
                    source_link='https://energy.mit.edu/wp-content/uploads/2018/09/The-Future-of-Nuclear-Energy-in-a-Carbon-Constrained-World.pdf; https://doi.org/10.1016/j.joule.2020.10.001',
                ),
            ),


            ContinuousInput(
                'lifetime','Lifetime',
                unit='year',
                defaults=[Default(30)],
                validators=[validators.numeric(), validators.integer(), validators.gt(0)],
                tooltip = Tooltip(
                    "Plant lifetime impacts capital cost levelization (see crf equation in 'interest rate' tooltip). Other finance cost parameters (interest rate, inflaction rate, rate of return on equity, debt fraction, tax rate, etc. for capital cost amortization and levelization) are from NREL ATB2019. Technology cost parameters (overnight capital cost, fixed operating cost, and variable operating cost) are from MIT Future of Nuclear, instead of ATB because it does not have data per nuclear reactor type.",
                    source='ATB2019; MIT Future of Nuclear',
                    source_link='https://atb.nrel.gov/; https://energy.mit.edu/wp-content/uploads/2018/09/The-Future-of-Nuclear-Energy-in-a-Carbon-Constrained-World.pdf; https://doi.org/10.1016/j.joule.2020.10.001',
                ),
            ),

            ContinuousInput(
                'interest_rate', 'Interest Rate',
                 unit='%/year',
                defaults=[Default(5)],
                validators=[validators.numeric(), validators.gt(0), validators.lte(20)],
                tooltip=Tooltip(
                    "Levelized capital cost = CRF (capital recovery factor) * PFF (project financial factor) *capital cost; crf = WACC/(1-(1/(1+WACC)^t)), where t=lifetime; WACC = ((1+((1-DF)*((1+RROE)*(1+i)-1)) + (DF*((1+IR)*(1+i)-1)*(1-TR))) / (1+i)) – 1, , where PROE (rate or return on equity) ~5%, DF (debt fraction) ~74%, TR (tax rate) ~ 26%, i (inflation rate) ~2.5%, IR (interest rate_real)=(IR_user input-i)/(1+i)",
                    source='2021 Annual Technology Baseline by NREL (National Renewable Energy Laboratory), Solar Tabs',
                    source_link='https://data.openei.org/submissions/4129',
                ),
            ),

            ContinuousInput(
                'cap_fac','Capacity Factor',
                defaults=[Default(0.93)],
                validators=[validators.numeric(), validators.gt(0), validators.lt(1)],
                tooltip = Tooltip(
                    "Percent of the facility's design capacity is used to produce product, e.g., mathematically the number of hours in a year the facility runs, divided by 24*365 hours.",
                    source='ATB2019; MIT Future of Nuclear',
                    source_link='https://atb.nrel.gov/',
                ),
            ),

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



    def __init__(self, lca_pathway=None):
        self.lca_pathway = lca_pathway
        self.finance = pd.read_csv(PATH + "nuclear_finance.csv")
        self.other_costs = pd.read_csv(PATH + "nuclear_costs.csv")
        super().__init__()


    def get_finance_values(self):
        finance_costs = {}
        filtered = self.finance[self.finance['Source'] == 'ATB']
        for row in filtered.to_dict(orient='records'):
            finance_costs[row['Abbr']] = float(row['Value'])
        finance_costs["i"]=self.interest_rate/100
        return finance_costs

    def get_cost_values(self):
        nuclear_costs = {}
        filtered = self.other_costs[
                                    (self.other_costs['Type'] == self.reactor_type)]
        for row in filtered.to_dict(orient='records'):
            nuclear_costs[row['Cost Type']] = float(row['Value'])
        return nuclear_costs
        print (nuclear_costs)

    def get_lcoe(self):
        cost_values = self.get_cost_values()
        occ = self.occ 
        cap_fac = self.cap_fac
        cap_reg_mult = 1
        finance_values = self.get_finance_values()

        lifetime = self.lifetime
        tax_rate = self.tax_rate
        interest_rate = self.interest_rate
        grid_cost = 0
        fuel_cost = 7 


        nuclear_lcoe = LCOE(
            cap_fac, cap_reg_mult,
            occ, 
            cost_values['FOM'], 
            cost_values['VOM']+self.user_trans_dist_cost, 
            finance_values,
            lifetime, 
            grid_cost, 
            fuel_cost, 
            tax_rate 
        )
        return nuclear_lcoe

    def get_cost_breakdown(self):
        lcoe = self.get_lcoe()
        cost_breakdown = lcoe.get_cost_breakdown()
        return cost_breakdown
