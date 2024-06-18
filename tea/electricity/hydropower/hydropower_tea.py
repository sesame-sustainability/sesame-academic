import os
import statistics

import pandas as pd
import us

from tea.electricity.LCOE import LCOE
from core import conditionals, validators
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput
from core.tea import TeaBase


PATH = os.getcwd() + "/tea/electricity/hydropower/"
hydro_resource_types_NREL = ['NPD','NSD']
hydro_resource_classes_NREL = [1,2,3,4]
# If non-numbers are included in the Class column of the costs file, the column is read as text data
hydro_resource_classes_NREL = [str(item) for item in hydro_resource_classes_NREL]
hydro_resource_scenarios_NREL = ['Advanced','Moderate','Conservative']

hydro_resource_types_IEA = ['Reservoir','Run of River']
# hydro_resource_classes_IEA = ['> 5 MW','< 5 MW']
# # If non-numbers are included in the Class column of the costs file, the column is read as text data
# hydro_resource_classes_IEA = [str(item) for item in hydro_resource_classes_NREL]
hydro_resource_scenarios_IEA = ['Min','Median','Mean','Max']

# NOTE: CAPEX is not scaled by power law (typically with coefficient = 0.6) because literature and data generally do not support this trend
# This is not surprising given challenges of staying on bugdget for large civil engineering projects 
# Exceptions may be in countries that routinely build similarly designed hydropower stations
# For NREL ATB data, hydro didn't scale by the power rule (or at the coefficient is so low that the power law is not meaningful) https://atb.nrel.gov/electricity/2021/data
# Table 5.2 on page 94 of IRENA's 2019 report shows that CAPEX generally does not follow a power rule and is somewhat flat https://www.irena.org/publications/2020/Jun/Renewable-Power-Costs-in-2019
# Figure 27 of the 2017 Hydropower Market Report shows O&M costs but not CAPEX scaling by a power law. https://www.energy.gov/sites/default/files/2018/04/f51/Hydropower%20Market%20Report.pdf




class HydropowerTEA(TeaBase):

    @classmethod
    def user_inputs(cls):
        return [
            OptionsInput('cost_source', 'Data Source for Technology Costs', defaults=[Default('NREL ATB')], options=['NREL ATB','IEA']),
            
            # NREL ATB specific inputs
            # TO-DO: add note about NPD and NSD. Based on US analysis, mostly small scale.
                # NPD: Non-powered dam. Adding generation to NPD.
                # NSD: New stream-reach development. Adding generation to undeveloped sites.
                # See "hydropower_info.xlsx" for typical height and power capacity
            OptionsInput('resource_type', 'Resource Type', conditionals=[conditionals.input_equal_to('cost_source', 'NREL ATB')], options=hydro_resource_types_NREL),
            OptionsInput('resource_class', 'Resource Class', conditionals=[conditionals.input_equal_to('cost_source', 'NREL ATB')], options=hydro_resource_classes_NREL),
            OptionsInput('resource_scenario', 'Resource Scenario', conditionals=[conditionals.input_equal_to('cost_source', 'NREL ATB')], options=hydro_resource_scenarios_NREL),
            OptionsInput('cost_year', 'Year', conditionals=[conditionals.input_equal_to('cost_source', 'NREL ATB')], options=[2020]),
            
            # IEA specific inputs 
            OptionsInput('resource_type', 'Resource Type', conditionals=[conditionals.input_equal_to('cost_source', 'IEA')], options=hydro_resource_types_IEA),
            OptionsInput('resource_class', 'Resource Class', conditionals=[conditionals.input_equal_to('cost_source', 'IEA'),conditionals.input_equal_to('resource_type', 'Reservoir')], 
                options=['> 5 MW']),
            OptionsInput('resource_class', 'Resource Class', conditionals=[conditionals.input_equal_to('cost_source', 'IEA'),conditionals.input_equal_to('resource_type', 'Run of River')], 
                options=['< 5 MW','> 5 MW']),
            OptionsInput('resource_scenario', 'Resource Scenario', conditionals=[conditionals.input_equal_to('cost_source', 'IEA')], options=hydro_resource_scenarios_IEA),
            OptionsInput('cost_year', 'Year', conditionals=[conditionals.input_equal_to('cost_source', 'IEA')], options=[2020]),
            ContinuousInput('VOM','VOM ($/MWh)', conditionals=[conditionals.input_equal_to('cost_source', 'IEA')], defaults=[Default(0)], validators=[validators.numeric(), validators.gte(0)]),
            ContinuousInput('FOM','FOM ($/kW-yr)', conditionals=[conditionals.input_equal_to('cost_source', 'IEA')], defaults=[Default(100)], validators=[validators.numeric(), validators.gte(0)]),
            
            # TO-DO: read default CF values from "hydropower_CF.csv"
            ContinuousInput('cap_fac','Capacity Factor', defaults=[Default(0.6)], validators=[validators.numeric(), validators.gt(0), validators.lte(1)]),
            OptionsInput('finance_source', 'Select Data Source for Finance Costs', defaults=[Default('ATB')], options=['ATB']),
            ContinuousInput('tax_credit', 'Tax Credits', validators=[validators.numeric(), validators.gte(0)]),
            ContinuousInput(
                'user_trans_dist_cost', 'Transmission & Distribution Cost',
                unit='$/MWh',
                defaults=[Default(47)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(200)],
                tooltip=Tooltip(
                    '47 $/MWh is the US average transmission AND distribution cost, including 14 transmission, and 33 distribution (mainly to residential and commercial consumers). If the power is intended for industrial use, then 14 is recommended.',
                    source='EIA',
                    source_link='https://www.eia.gov/outlooks/aeo/data/browser/#/?id=8-AEO2021&region=0-0&cases=ref2021&star; https://www.eia.gov/energyexplained/electricity/prices-and-factors-affecting-prices.php',
                ),
            ),
            ContinuousInput(
                'tax_rate', 'Tax',
                unit='%',
                defaults=[Default(6.35)],
                validators=[validators.numeric(), validators.gt(0), validators.lt(100)],
                tooltip=Tooltip(
                    "The default value represents sales tax, which varies by states and specific use cases. 6.35% represents US averegae sales tax. For electricity-specific tax, 7% was found for North Carolina, and 6.25% for Texas non-residential use: https://comptroller.texas.gov/taxes/publications/96-1309.pdf.",
                    source_link='https://www.ncdor.gov/taxes-forms/sales-and-use-tax/electricity#:~:text=Gross%20receipts%20derived%20from%20sales,Sales%20and%20Use%20Tax%20Return.',
                ),
            ),

        ]

    def __init__(self, lca_pathway=None):
        self.lca_pathway = lca_pathway
        self.finance = pd.read_csv(PATH + "hydropower_finance.csv")
        self.cost_data = pd.read_csv(PATH + "hydropower_costs_v2.csv")
        super().__init__()

    def get_capacity_factor(self):
        return self.cap_fac

    def get_finance_values(self):
        finance_costs = {}
        filtered = self.finance[self.finance['Source'] == self.finance_source]
        for row in filtered.to_dict(orient='records'):
            finance_costs[row['Abbr']] = float(row['value'])
        return finance_costs

    def get_cost_values(self):
        costs = {}
        
        df = self.cost_data[(self.cost_data['Source'] == self.cost_source) & (self.cost_data['Type'] == self.resource_type) & (self.cost_data['Class'] == self.resource_class) & (self.cost_data['Scenario'] == self.resource_scenario) & (self.cost_data['Year'] == self.cost_year)]
        costs["OCC"] = df.loc[df['Variable'] == 'OCC']["Value"].item()
        if self.cost_source == 'NREL ATB':
            costs["FOM"] = df.loc[df['Variable'] == 'FOM']["Value"].item()
            costs["VOM"] = df.loc[df['Variable'] == 'VOM']["Value"].item() + self.user_trans_dist_cost
        else:
            costs["FOM"] = self.FOM
            costs["VOM"] = self.VOM + self.user_trans_dist_cost
        return costs

    def get_lcoe(self):
        cap_fac = self.get_capacity_factor()
        # cap_reg_mult = self.get_cap_reg_mult()
        cap_reg_mult = 1
        cost_values = self.get_cost_values()
        finance_values = self.get_finance_values()

        lifetime = 30
        grid_cost = 0
        fuel_cost = 0

        lcoe = LCOE(cap_fac, cap_reg_mult, cost_values['OCC'], cost_values['FOM'], cost_values['VOM'], finance_values, lifetime, grid_cost, fuel_cost, self.tax_rate)
        return lcoe

    def get_cost_breakdown(self):
        lcoe = self.get_lcoe()
        cost_breakdown = lcoe.get_cost_breakdown()
        return cost_breakdown