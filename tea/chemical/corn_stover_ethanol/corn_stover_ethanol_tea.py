#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed August 4 10:00:29 2021

@author  Jon-Marc McGregor ExxonMobil Intern
"""

###Notes###
# This is a TEA for corn stover ethanol production
# All data are based on the NREL study "Process Design and Economics for Biochemical Conversion of Lignocellulosic Biomass to Ethanol"
# https://www.nrel.gov/docs/fy11osti/47764.pdf
#

import os
import pandas as pd
# import us, statistics


from core import validators, conditionals
from core.inputs import ContinuousInput, Default, OptionsInput, CategoricalInput, Tooltip
from core.tea import TeaBase
from tea.chemical.corn_stover_ethanol.corn_stover_ethanol_ccs_tea import BECCSTea

PATH = os.getcwd() + "/tea/chemical/corn_stover_ethanol/"


class corn_stover_EthanolTEA(TeaBase):
    unit = '$/GJ'

    @classmethod
    def user_inputs(cls):
        return [

            ContinuousInput('ethanol_production_rate', 'Ethanol Production Rate',
                            unit='MMgal/yr',
                            defaults=[Default(60)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(800)],
                            tooltip=Tooltip(
                                'Plant capacity influences capital cost (economy of scale); MMgal=million gallon. This parameter impacts both capital cost (with built-in economy of scale equation) and feedstock cost, but the user should manually adjust the feedstock cost per guidance from the Feedstock & Handling cost tooltip. The default 60 MMGal/yr stover ethanol corresponds to 2000 dry tonne/day stover input and ~ 50 mi collection radius.',
                                source='NREL 2011, assuming corn and corn stover ethanol plants have same lifetime and discount rate',
                                source_link='https://www.nrel.gov/docs/fy11osti/47764.pdf',
                            ),
                            ),

            ContinuousInput('lifetime', 'Lifetime',
                            unit='yr',
                            defaults=[Default(30)],
                            validators=[validators.integer(), validators.gte(0)],
                            tooltip=Tooltip(
                                'Plant lifetime impacts capital cost levelization (see crf equation in Discount Rate tooltip)',
                                source='NREL 2011, assuming corn and corn stover ethanol plants have same lifetime and discount rate',
                                source_link='https://www.nrel.gov/docs/fy11osti/47764.pdf',
                            ),
                            ),

            ContinuousInput('discount_rate', 'Discount Rate',
                            defaults=[Default(0.1)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(1)],
                            tooltip=Tooltip(
                                'levelized capital cost = crf (capital recovery factor) * capital cost; crf = (discount_rate * ((1 + discount_rate)**lifetime)) / ((1 + discount_rate)**(lifetime) - 1)',
                                source='NREL 2011, assuming corn and corn stover ethanol plants have same lifetime and discount rate',
                                source_link='https://www.nrel.gov/docs/fy11osti/47764.pdf',
                            ),
                            ),

            ContinuousInput('feedstock_cost', 'Feedstock & Handling Cost',
                            unit='$/dry ton stover',
                            defaults=[Default(68)],
                            # Deafualt is based on US average price in April 2019, from (https://www.nass.usda.gov/Publications/Todays_Reports/reports/agpr0519.pdf)
                            validators=[validators.numeric(), validators.gte(0), validators.lte(300)],
                            tooltip=Tooltip(
                                'Biomass feedstock cost (paid by the biorefinery, including purchase, transportation and handling) varies with collection radius and thus biorefinery capacity. The Applied Energy paper (Fig 10A) developed an optimization model to find the cost-optimal transportation mode (combination of truck, depot usage, and rail) for different stover ethanol biorefinery capacity. As a reference, with the default 60 MM gal/yr (i.e., 2000 dry tonne/day stover input) capacity and 68 $/dry ton stover price as the base case, the feedstock cost multipliers to the base case are: 4000 tonne/day ~ 1.1, 8000 ~ 1.16, 16000 ~1.22. So, if the user accepts 68 $/dry ton as the price for a 2000 tonne/day facility, then one could multiply 68 by 1.1 to roughly predict the feedstock cost for a 4000 tonne/day facility. A fitting function from the paper is generated for the users to use at their own risk: Y=0.53*X^0.086, where Y=feedstock cost multiplier, and X=biorefinery capacity (dry tonne/day stover). Also note that users aiming for a benchmark analysis may not need to adjust the capacity and feedstock price, because the total cost (Fig 10B in the paper, minus the MESP) does not change very much with capacity, because the economy of scale from capital cost and dis-economy of scale from feedstock cost somewhat offset each other.',
                                source='NREL 2011, assuming corn and corn stover ethanol plants have same lifetime and discount rate; Applied Energy papers',
                                source_link='"https://www.nrel.gov/docs/fy11osti/47764.pdf; Figure 4 of https://www.sciencedirect.com/science/article/pii/S0306261918302022; Figure 10A of https://www.sciencedirect.com/science/article/pii/S0306261917311807',
                            ),
                            ),

            ContinuousInput('Capex_adjust_factor', 'Capital Cost Adjustment Factor',
                            defaults=[Default(1)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(3)],
                            # Capex adjusment factor between 10% to 300%
                            tooltip=Tooltip(
                                'This input provides flexibility to capital cost adjustment. Put 1 to use the NREL cost assumption; 2 to represent doubling NREL cost.',
                                source='NREL 2011, assuming corn and corn stover ethanol plants have same lifetime and discount rate',
                                source_link='https://www.nrel.gov/docs/fy11osti/47764.pdf',
                            ),
                            ),
            ContinuousInput('scaling_factor', 'Capital Cost Scaling Factor',
                            defaults=[Default(0.6)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(1)],
                            tooltip=Tooltip(
                                'Capital cost for Capacity X = capital cost for base capacity*(X/base capacity)^scaling factor; 0.6 is a common assumption for facilities made up of tanks and pipes, such as a refinery. The default 60 MMGal/yr stover ethanol capacity corresponds to 2000 dry tonne/day stover input and ~ 50 mi collection radius; MM= million. Caveat: the further away from the base capacity of 60 MMGal/yr, the less accurate the capital cost prediction for the new capacity.',
                                source='ECPE paper, ChemE text book',
                                source_link='https://www.sciencedirect.com/science/article/abs/pii/0167188X86900534#:~:text=The%20value%20of%20%CE%B1%20%3D%200.6,level%20of%20capacity%20V1; https://www.osti.gov/biblio/293030',
                            ),
                            ),
            ContinuousInput('tax_gal', 'Tax',
                            unit='$/gal',
                            defaults=[Default(0.1)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(0.8)],
                            tooltip=Tooltip(
                                'Default tax value = fuel tax, which varies by states. 0.1 $/gal is a reasonable benchmark. Ethanol 1 gal = 80.53 MJ LHV, so 0.1 $/gal = 0.00124 $/MJ',
                                source='NCSL',
                                source_link='https://www.ncsl.org/research/transportation/taxation-of-alternative-fuels.aspx#:~:text=Ethyl%20alcohol%20and%20methyl%20alcohol,%240.20%20per%20gasoline%20gallon%20equivalent.',
                            ),
                        ),
            # Capex adjusment factor between 10% to 300%

            OptionsInput('use_ccs', 'Use CCS (Carbon Capture & Sequester)', options=['Yes', 'No']),
            OptionsInput('ferment_ccs', 'Capture CO\u2082 from Fermenter ?', options=['Yes'],
                         conditionals=[conditionals.input_equal_to('use_ccs', 'Yes')]),
            OptionsInput('ferment_cap_tech', 'CCS Technology', options=['compression + dehydration'],
                         conditionals=[conditionals.input_equal_to('use_ccs', 'Yes'),
                                       conditionals.input_equal_to('ferment_ccs', 'Yes')]),
            ContinuousInput('ferment_co2_cap_percent', 'Carbon Capture Percent from the Fermenter ?',
                            validators=[validators.numeric(), validators.gte(0), validators.lt(100)],
                            conditionals=[conditionals.input_equal_to('ferment_ccs', 'Yes')]),

            OptionsInput('boilerstack_ccs', 'Capture CO\u2082 from Boilerstack ?', options=['Yes', 'No'],
                         conditionals=[conditionals.input_equal_to('use_ccs', 'Yes')]),
            OptionsInput('boiler_cap_tech', 'CCS Technology', options=['amine'],
                         conditionals=[conditionals.input_equal_to('boilerstack_ccs', 'Yes')]),
            ContinuousInput('boiler_co2_cap_percent', 'CO\u2082 Captured from Boilerstack (%)',
                            validators=[validators.numeric(), validators.gte(0), validators.lt(100)],
                            conditionals=[conditionals.input_equal_to('boilerstack_ccs', 'Yes')]),
            OptionsInput('amine_regen_ccs', 'Capture CO\u2082 from Amine Regeneration ?', options=['Yes', 'No'],
                         conditionals=[conditionals.input_equal_to('boilerstack_ccs', 'Yes')]),
            ContinuousInput('amine_co2_cap_percent', 'CO\u2082 Captured from Amine Regeneration (%)',
                            validators=[validators.numeric(), validators.gte(0), validators.lt(100)],
                            conditionals=[conditionals.input_equal_to('amine_regen_ccs', 'Yes')]),

            ContinuousInput('fuel_adj_factor', 'Adjustment Factor for Natural Gas Needed for Amine Regeneration '
                                               '(e.g 1 ~ assumes the value of 2.95,MJ/kg CO2, 1.3 assumes a 30% '
                                               'increase) ',
                            defaults=[Default(1)],
                            validators=[validators.numeric(), validators.gte(1), validators.lt(1.7)],
                            conditionals=[conditionals.input_equal_to('boilerstack_ccs', 'Yes')]),

            ContinuousInput('pipeline_miles', 'Pipeline Distance from Capture to Sequester (mi)',
                            unit='mi',
                            defaults=[Default(240)],
                            validators=[validators.numeric(), validators.gte(0)],
                            conditionals=[conditionals.input_equal_to('use_ccs', 'Yes')],
                            tooltip=Tooltip(
                                'The distance could vary significantly by projects. 240 mi roughly translates to ~ 20 $/T CO2 for transportation and sequestration, assuming storage costs 8 $/T CO2, and transportation costs 0.05 $/T CO2/mi.',
                                source='NPC 2020',
                                source_link='https://dualchallenge.npc.org/files/CCUS-Chap_2-060520.pdf',
                            )),

        ]

    def __init__(self, lca_pathway=None):

        self.lca_pathway = lca_pathway
        self.ethanol_production_param = pd.read_csv(PATH + "corn_stover_ethanol_production_tech.csv")
        self.cost_transportation = pd.read_csv(PATH + "corn_stover_ethanol_transportation_costs.csv")
        super().__init__()

    # Read Data from excel file

    def get_cost_breakdown(self):
        global capture_capital, capture_fom, capture_vom, capture_transp, capture_storage, capture_taxes

        # Assumptions
        # get values based off user input
        index = 1
        base_cost = self.ethanol_production_param.iloc[0, index]  # MM$ 2007, from the reference
        base_size = self.ethanol_production_param.iloc[1, index]  # MMgal/yr , from the reference
        ethanol_yeild = self.ethanol_production_param.iloc[2, index]  # gal/dry ton corn stover
        CEPCI_base = self.ethanol_production_param.iloc[3, index]  # Chemical Engineering Plant Cost Index-(base 2007)
        CEPCI_current = self.ethanol_production_param.iloc[4, index]  # Chemical Engineering Plant Cost Index-current
        scaling_factor = self.scaling_factor
        fixed_operational_cost = self.ethanol_production_param.iloc[6, index]  # MM$
        taxes = self.tax_gal * 0.00124 / 0.1 # see conversion factor in tooltip

        ethanol_density = 787.6  # ethanol density at 25 C and 1 bar in kg/m3
        Conversion_gal_to_m3 = 264.17  # gal to m3
        LHV_ethanol = 26.82  # Ethanol Lower Heating Value in MJ/kg

        # calculations

        fixed_operational_cost_current = fixed_operational_cost * CEPCI_current / CEPCI_base
        dry_corn = self.ethanol_production_rate * 1e6 / ethanol_yeild  # dry corn stover needed
        feedstock_cost_total = self.feedstock_cost * dry_corn / 1e6  # feedstock & handling cost in MM$
        capex_scaled = base_cost * (self.ethanol_production_rate / base_size) ** scaling_factor * (
                CEPCI_current / CEPCI_base) * self.Capex_adjust_factor

        crf = (self.discount_rate * ((1 + self.discount_rate) ** self.lifetime)) / (
                    (1 + self.discount_rate) ** (self.lifetime) - 1)  # % CRF: Capital recovery factor

        print('Capital charge factor (CRF)=', '%.3f' % crf)
        capex_cost = crf * capex_scaled  # MM$/yr
        variable_operational_cost= (20.13)*CEPCI_current/CEPCI_base + feedstock_cost_total # MM$/yr, Number 20.13 from Table 30 on page 63 of the reference

        #####################
        ## Midstream Model ##
        #####################
        filtered = self.cost_transportation

        costs = filtered[filtered['type'] == "cost"]
        distances = filtered[filtered['type'] == "distance"]
        fractions = filtered[filtered['type'] == "fraction"]

        truck = float(costs[costs['transportation method'] == "truck"].iloc[0].value) * float(
            distances[distances['transportation method'] == "truck"].iloc[0].value)
        rail = float(costs[costs['transportation method'] == "rail"].iloc[0].value) * float(
            distances[distances['transportation method'] == "rail"].iloc[0].value)
        marine = float(costs[costs['transportation method'] == "marine"].iloc[0].value) * float(
            distances[distances['transportation method'] == "marine"].iloc[0].value)
        pipeline = float(costs[costs['transportation method'] == "pipeline"].iloc[0].value) * float(
            distances[distances['transportation method'] == "pipeline"].iloc[0].value)

        frac_truck = float(fractions[fractions['transportation method'] == "truck"].iloc[0].value)
        frac_rail = float(fractions[fractions['transportation method'] == "rail"].iloc[0].value)
        frac_marine = float(fractions[fractions['transportation method'] == "marine"].iloc[0].value)
        frac_pipeline = float(fractions[fractions['transportation method'] == "pipeline"].iloc[0].value)

        transportation = ((truck * frac_truck) + (rail * frac_rail) + (marine * frac_marine) + (
                    pipeline * frac_pipeline))  # $/gal

        transportation = transportation * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol  # $/gal*gal/m3 *1/density *LHV =$/MJ,   For pipeline mode of transport

        #####################
        ## Cost related to CCS  ##
        #####################
        if self.use_ccs == 'No':
            capture_capital = 0
            capture_fom = 0
            capture_vom = 0
            capture_taxes = 0
            capture_transp = 0
            capture_storage = 0

        elif self.boilerstack_ccs == 'No':  # For fermenter
            capturecost = BECCSTea("Ethanol Production", self.ethanol_production_rate, self.ferment_cap_tech,
                                   0, self.ferment_co2_cap_percent, 0,
                                   0, self.boilerstack_ccs,
                                   0, 1, self.pipeline_miles, crf)

            capture_capital = capturecost.get_capture_cost_breakdown()[1] / (
                self.ethanol_production_rate) / 1e6 * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol  # $/MJ

            capture_fom = capturecost.get_capture_cost_breakdown()[2] / (
                self.ethanol_production_rate) / 1e6 * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol  # $/MJ

            capture_vom = capturecost.get_capture_cost_breakdown()[3] / (
                self.ethanol_production_rate) / 1e6 * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol  # $/MJ

            capture_taxes = capturecost.get_capture_cost_breakdown()[4] / (
                self.ethanol_production_rate) / 1e6 * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol  # $/MJ

            capture_transp = capturecost.get_capture_cost_breakdown()[5] / (
                self.ethanol_production_rate) / 1e6 * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol  # $/MJ

            capture_storage = capturecost.get_capture_cost_breakdown()[6] / (
                self.ethanol_production_rate) / 1e6 * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol  # $/MJ

        elif self.amine_regen_ccs == 'No':  # For fermenter + boilerstack

            capturecost = BECCSTea("Ethanol Production", self.ethanol_production_rate, self.ferment_cap_tech,
                                   self.boiler_cap_tech, self.ferment_co2_cap_percent, self.boiler_co2_cap_percent,
                                   0, self.boilerstack_ccs, self.amine_regen_ccs, self.fuel_adj_factor,
                                   self.pipeline_miles, crf)

            capture_capital = capturecost.get_capture_cost_breakdown()[1] / (
                self.ethanol_production_rate) / 1e6 * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol  # $/MJ

            capture_fom = capturecost.get_capture_cost_breakdown()[2] / (
                self.ethanol_production_rate) / 1e6 * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol  # $/MJ

            capture_vom = capturecost.get_capture_cost_breakdown()[3] / (
                self.ethanol_production_rate) / 1e6 * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol  # $/MJ

            capture_taxes = capturecost.get_capture_cost_breakdown()[4] / (
                self.ethanol_production_rate) / 1e6 * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol  # $/MJ

            capture_transp = capturecost.get_capture_cost_breakdown()[5] / (
                self.ethanol_production_rate) / 1e6 * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol  # $/MJ

            capture_storage = capturecost.get_capture_cost_breakdown()[6] / (
                self.ethanol_production_rate) / 1e6 * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol  # $/MJ

        elif self.amine_regen_ccs == 'Yes':  # For fermenter, boilerstack and amine regn
            capturecost = BECCSTea("Ethanol Production", self.ethanol_production_rate, self.ferment_cap_tech,
                                   self.boiler_cap_tech, self.ferment_co2_cap_percent, self.boiler_co2_cap_percent,
                                   self.amine_co2_cap_percent, self.boilerstack_ccs,
                                   self.amine_regen_ccs, self.fuel_adj_factor, self.pipeline_miles, crf)

            capture_capital = capturecost.get_capture_cost_breakdown()[1] / (
                self.ethanol_production_rate) / 1e6 * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol  # $/MJ

            capture_fom = capturecost.get_capture_cost_breakdown()[2] / (
                self.ethanol_production_rate) / 1e6 * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol  # $/MJ

            capture_vom = capturecost.get_capture_cost_breakdown()[3] / (
                self.ethanol_production_rate) / 1e6 * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol  # $/MJ

            capture_taxes = capturecost.get_capture_cost_breakdown()[4] / (
                self.ethanol_production_rate) / 1e6 * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol  # $/MJ

            capture_transp = capturecost.get_capture_cost_breakdown()[5] / (
                self.ethanol_production_rate) / 1e6 * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol  # $/MJ

            capture_storage = capturecost.get_capture_cost_breakdown()[6] / (
                self.ethanol_production_rate) / 1e6 * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol  # $/MJ

        #####################
        ## Cost Breakdown  ##
        #####################

        capital_fixed = (capex_cost + fixed_operational_cost_current) / (
            self.ethanol_production_rate) * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol \
                        + capture_capital + capture_fom  # $/gal*gal/m3 *1/density *1/LHV =$/MJ

        maintenance = 0.00
        variable_cost = variable_operational_cost / (
            self.ethanol_production_rate) * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol \
                        + capture_vom

        trans_storage_cost = transportation + capture_transp + capture_storage  # $/gal*gal/m3 *1/density *LHV =$/MJ

        # total= (capital_fixed + operational+ taxes + transportation) #  $/MJ

        cost_breakdown = {
            "Capital & Fixed": capital_fixed,
            "Maintenance": maintenance,
            "Transportation & Storage": trans_storage_cost,
            "Variable Cost": variable_cost,
            "Taxes": taxes,
        }

        # return costs as $/GJ
        return {
            key: value * 1000
            for key, value in cost_breakdown.items()
        }
