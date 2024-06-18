#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
from us import STATES

from tea.chemical.SLCOE import SLCOE
from core import validators, conditionals
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from core.tea import TeaBase

PATH = os.getcwd() + "/tea/chemical/lpg/"

class LPGTEA(TeaBase):
    unit = '$/MJ'

    @classmethod
    def user_inputs(cls):
        return [
            OptionsInput('user_crude_price', 'Use user crude price', options=['Yes', 'No'],
                         defaults=[Default('No')],
                         tooltip=Tooltip(
                             'Default of No means US average price is used, including all the costs before a manufacturing facility receives the feedstock: raw material extraction, processing, transportation, profit margin, …; bbl=blue barrel. Note when yes is selected, the State input below still controls the other state-specific parameters (see tooltip there), but this should not cause major inconsistency because crude cost dominates the total cost.',
                             source='EIA',
                             source_link='https://www.eia.gov/dnav/pet/pet_pri_rac2_a_EPC0_PDT_dpbbl_a.htm',
                         )
                         ),
            ContinuousInput('user_crude_cost', 'Cost of crude',
                        unit='$/bbl',
                        defaults=[Default(70)],
                        validators=[validators.numeric(), validators.gte(0)],
                        conditionals=[conditionals.input_equal_to('user_crude_price', 'Yes')],
                        tooltip=Tooltip(
                        'Price includes all the costs before a manufacturing facility receives the feedstock: raw material extraction, processing, transportation, profit margin, …; bbl=blue barrel',
                        source='EIA',
                        source_link='https://www.eia.gov/dnav/pet/pet_pri_rac2_a_EPC0_PDT_dpbbl_a.htm',
        )
        ),

        OptionsInput('state', 'State', options=[state.abbr for state in STATES]+['US average'],
                    defaults=[Default('US average')],
                    tooltip=Tooltip(
                    'State selection impacts the cost of raw materials used in the production facility, including crude, hydrogen, electricity, natural gas, …',
                    source='EIA',
                    source_link='https://www.eia.gov/dnav/pet/pet_pri_rac2_a_EPC0_PDT_dpbbl_a.htm; https://en.wikipedia.org/wiki/Fuel_taxes_in_the_United_States',
        )
                     ),
        ContinuousInput('tax_gal', 'Tax',
                            unit='$/gal',
                            defaults=[Default(0.526)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(0.8)],
                            tooltip=Tooltip(
                                'Default assumes US average gasoline fuel tax because no data was found for US weighted LPG fuel tax. One data point mentioned similar tax between LPG and conventional motor fuel https://afdc.energy.gov/laws/5882. LPG 1 gal = 87664 btu LHV, so  0.526 $/gal = 0.000006$/btu',
                            ),
                            ),

        ]


    def __init__(self, lca_pathway=None):
        self.lca_pathway = lca_pathway
        self.cost_crude = pd.read_csv(PATH + "domesticcrude_refinerprice.csv")
        self.cost_residoil = pd.read_csv(PATH + "residoil_industrial.csv")
        self.cost_hydrogen = pd.read_csv(PATH + "hydrogen_industrial.csv")
        self.cost_electricity = pd.read_csv(PATH + "electricity_industrial.csv")
        self.cost_natgas = pd.read_csv(PATH + "natgas_industrial.csv")
        self.cost_other = pd.read_csv(PATH + "lpg_costpar.csv")
        self.input_fractions = pd.read_csv(PATH + "lpg_input_fractions.csv")
        self.cost_transportation = pd.read_csv(PATH + "lpg_transportation_costs.csv")

    def get_fuel_cost(self):
        filtered = self.input_fractions
        frac_natgas = float(filtered[filtered['Input'] == "Natural Gas"].iloc[0].value)
        frac_petroleum = float(filtered[filtered['Input'] == "Petroleum"].iloc[0].value)
        frac_electricity = float(filtered[filtered['Input'] == "Electricity"].iloc[0].value)
        frac_residoil = float(filtered[filtered['Input'] == "Residual Oil"].iloc[0].value)
        frac_hydrogen = float(filtered[filtered['Input'] == "Hydrogen"].iloc[0].value)

        residoil_cost = float(self.cost_residoil[self.cost_residoil["State"] == self.state].iloc[0].value)*frac_residoil
        hydrogen_cost = float(self.cost_hydrogen[self.cost_hydrogen["State"] == self.state].iloc[0].value)*frac_hydrogen
        electricity_cost = float(self.cost_electricity[self.cost_electricity["State"] == self.state].iloc[0].value)*frac_electricity
        natgas_cost = float(self.cost_natgas[self.cost_natgas["State"] == self.state].iloc[0].value)*frac_natgas
        other_fuel_cost = residoil_cost + hydrogen_cost + electricity_cost + natgas_cost

        if self.user_crude_price == 'No':
            crude_cost = float(self.cost_crude[self.cost_crude["State"] == self.state].iloc[0].value)*frac_petroleum
        else:
            crude_cost = float(self.user_crude_cost)*frac_petroleum/42/129670

        return crude_cost, other_fuel_cost


    def get_other_costs(self):
        filtered = self.cost_other
        lpg_vom = float(filtered[filtered['Item Type'] == "O&M"].iloc[0].value)
        lpg_capital = float(filtered[filtered['Item Type'] == "Capital"].iloc[0].value)
        taxes = self.tax_gal*0.000006/0.526 #$/Btu

        #transportation costs
        filtered = self.input_fractions
        frac_truck = float(filtered[filtered['Input'] == "Truck"].iloc[0].value)
        frac_rail = float(filtered[filtered['Input'] == "Rail"].iloc[0].value)
        frac_marine = float(filtered[filtered['Input'] == "Marine"].iloc[0].value)
        frac_pipeline = float(filtered[filtered['Input'] == "Pipeline"].iloc[0].value)

        filtered = self.cost_transportation
        costs = filtered[filtered['type'] == "cost"]
        distances = filtered[filtered['type'] == "distance"]

        truck = float(costs[costs['transportation method'] == "truck"].iloc[0].value) * float(
            distances[distances['transportation method'] == "truck"].iloc[0].value)
        rail = float(costs[costs['transportation method'] == "rail"].iloc[0].value) * float(
            distances[distances['transportation method'] == "rail"].iloc[0].value)
        marine = float(costs[costs['transportation method'] == "marine"].iloc[0].value) * float(
            distances[distances['transportation method'] == "marine"].iloc[0].value)
        pipeline = float(costs[costs['transportation method'] == "pipeline"].iloc[0].value) * float(
            distances[distances['transportation method'] == "pipeline"].iloc[0].value)

        transportation = ((truck * frac_truck) + (rail * frac_rail) + (marine * frac_marine) + (pipeline * frac_pipeline))

        return lpg_capital, lpg_vom, taxes, transportation


    def get_cost_breakdown(self):
        lpg_capital, lpg_vom, taxes, transportation = self.get_other_costs()
       # lpg_usage = self.get_amount_lpg()
        crude_cost, other_fuel_cost = self.get_fuel_cost()
        model = SLCOE(crude_cost + other_fuel_cost,
                            lpg_capital, 0, lpg_vom, 1, taxes, transportation)
        costs = model.get_cost_breakdown()
        costs = {key:val * 947.82 for key, val in costs.items()} # BTU to MJ conversion
        costs["Operational"] = {"Crude Cost": crude_cost*947.82,# BTU to MJ conversion
                       "Process Fuels & Utilities Cost": other_fuel_cost* 947.82}# BTU to MJ conversion
        return costs
