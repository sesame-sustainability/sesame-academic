#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed August 4 10:00:29 2021

@author  Jon-Marc McGregor ExxonMobil CSR Intern (jon-marc.mcgregor@utexas.edu)
"""

# ##Notes### This is a TEA for corn ethanol production All data are based on the NREL study "Determining the Cost of
# Producing Ethanol from Corn Starch and Lignocellulosic Feedstocks" https://www.nrel.gov/docs/fy01osti/28893.pdf


import os
import pandas as pd
# import us, statistics


from core import validators, conditionals
from core.inputs import ContinuousInput, Default, OptionsInput, CategoricalInput, Tooltip
from core.tea import TeaBase
from tea.chemical.corn_ethanol.corn_ethanol_ccs_tea import BECCSTea

PATH = os.getcwd() + "/tea/chemical/corn_ethanol/"


class corn_EthanolTEA(TeaBase):
    unit = '$/GJ'

    @classmethod
    def user_inputs(cls):
        return [

            ContinuousInput('ethanol_production_rate', 'Ethanol Production Rate',
                            unit='MMgal/yr',
                            defaults=[Default(25)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(800)],
                            tooltip=Tooltip(
                                'Plant capacity influences capital cost (economy of scale); MMgal=million gallon. This parameter impacts both capital cost (with built-in economy of scale equation) and feedstock cost, but the user should manually adjust the feedstock cost per guidance from the Feedstock & Handling cost tooltip. The default 25 MMGal/yr corn ethanol corresponds to 633 dry tonne/day corn input.',
                                source='NREL 2000',
                                source_link='https://www.nrel.gov/docs/fy01osti/28893.pdf',
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
                                'Amortized capital cost per year = crf (capital recovery factor) * total capital cost; crf = (discount_rate * ((1 + discount_rate)**lifetime)) / ((1 + discount_rate)**(lifetime) - 1)',
                                source='NREL 2011, assuming corn and corn stover ethanol plants have same lifetime and discount rate',
                                source_link='https://www.nrel.gov/docs/fy11osti/47764.pdf',
                            ),
                            ),

            ContinuousInput('feedstock_cost', 'Feedstock & Handling Cost',
                            unit='$/dry ton corn',
                            defaults=[Default(139)],  # Deafualt is based on US average price in April 2019, from (https://www.nass.usda.gov/Publications/Todays_Reports/reports/agpr0519.pdf)
                            validators=[validators.numeric(), validators.gte(90), validators.lte(300)],
                            tooltip=Tooltip(
                                'Biomass feedstock cost (paid by the biorefinery, including purchase, transportation and handling) varies with collection radius and thus biorefinery capacity. The default 139 $/dry ton corn is for a 25 MM gal ethanol/yr facility (i.e., 633 dry tonne/day corn input). The users are encouraged to fine tune this cost per facility capacity (Ethanol Production Rate input) because the larger the facility the longer the transportation distance. However, since corn purchase cost usually dominates the total feedstock cost, lack of modification to the transportation cost due to capacity variations is not expected to cause major error if the specified capacity does not deviate too much from the base case (25 MMgal/yr) ',
                                source='USDA 2019',
                                source_link='https://www.nass.usda.gov/Publications/Todays_Reports/reports/agpr0519.pdf',
                            ),
                            ),

            ContinuousInput('Capex_adjust_factor', 'Capital Cost Adjustment Factor',
                            defaults=[Default(1)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(3)], # Capex adjusment factor between 10% to 300%
                            tooltip=Tooltip(
                                'This input provides flexibility to capital cost adjustment. Put 1 to use the NREL cost assumption; 2 to represent doubling NREL cost.',
                                source='NREL 2000',
                                source_link='https://www.nrel.gov/docs/fy01osti/28893.pdf',
                            ),
                            ),
            ContinuousInput('scaling_factor', 'Capital Cost Scaling Factor',
                            defaults=[Default(0.6)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(1)],
                            tooltip=Tooltip(
                                'Capital cost for Capacity X = capital cost for base capacity*(X/base capacity)^scaling factor; 0.6 is a common assumption for facilities made up of tanks and pipes, such as a refinery. The default 25 MMGal/yr ethanol capacity corresponds to 633 dry tonne/day corn input. Caveat: the further away from the base capacity of 25 MMGal/yr, the less accurate the capital cost prediction for the new capacity.',
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

            # Portion of code to factor in Biofuel + CCS pathway

            OptionsInput('use_ccs', 'Use CCS (Carbon Capture & Sequester)', options=['Yes', 'No']),
            OptionsInput('ferment_ccs', 'Capture CO\u2082 from Fermenter ?', options=['Yes'],
                         conditionals=[conditionals.input_equal_to('use_ccs', 'Yes')]),
            OptionsInput('ferment_cap_tech', 'CCS Technology', options=['compression + dehydration'],
                         conditionals=[conditionals.input_equal_to('use_ccs', 'Yes'),
                                       conditionals.input_equal_to('ferment_ccs', 'Yes')]),
            ContinuousInput('ferment_co2_cap_percent', 'Carbon Capture Percent from the Fermenter ?',
                            defaults=[Default(85)],
                            validators=[validators.numeric(), validators.gte(0), validators.lt(100)],
                            conditionals=[conditionals.input_equal_to('ferment_ccs', 'Yes')]),

            OptionsInput('boilerstack_ccs', 'Capture CO\u2082 from Boilerstack ?', options=['Yes', 'No'],
                         conditionals=[conditionals.input_equal_to('use_ccs', 'Yes')]),
            OptionsInput('boiler_cap_tech', 'CCS Technology', options=['amine'],
                         conditionals=[conditionals.input_equal_to('boilerstack_ccs', 'Yes')]),
            ContinuousInput('boiler_co2_cap_percent', 'CO\u2082 Captured from Boilerstack (%)',
                            defaults=[Default(85)],
                            validators=[validators.numeric(), validators.gte(0), validators.lt(100)],
                            conditionals=[conditionals.input_equal_to('boilerstack_ccs', 'Yes')]),
            OptionsInput('amine_regen_ccs', 'Capture CO\u2082 from Amine Regeneration ?', options=['Yes', 'No'],
                         conditionals=[conditionals.input_equal_to('boilerstack_ccs', 'Yes')]),
            ContinuousInput('amine_co2_cap_percent', 'CO\u2082 Captured from Amine Regeneration (%)',
                            defaults=[Default(85)],
                            validators=[validators.numeric(), validators.gte(0), validators.lt(100)],
                            conditionals=[conditionals.input_equal_to('amine_regen_ccs', 'Yes')]),

            OptionsInput('biorefinery_model', 'Choose the Bio-refinery Model', options=['AECOM', 'Avg 88'],
                         conditionals=[conditionals.input_equal_to('boilerstack_ccs', 'Yes')]),
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
        self.ethanol_production_param = pd.read_csv(PATH + "corn_ethanol_production_tech.csv")
        self.cost_transportation = pd.read_csv(PATH + "corn_ethanol_transportation_costs.csv")
        super().__init__()

    def get_cost_breakdown(self):
        # Assumptions
        # get values based off user input
        index = 1
        base_cost = self.ethanol_production_param.iloc[0, index]  # MM$ 1997, from the reference
        base_size = self.ethanol_production_param.iloc[1, index]  # MMgal/yr , from the reference
        ethanol_yield = self.ethanol_production_param.iloc[2, index]  # gal/dry ton corn stover
        CEPCI_base = self.ethanol_production_param.iloc[3, index]  # Chemical Engineering Plant Cost Index-(base 1997)
        CEPCI_current = self.ethanol_production_param.iloc[4, index]  # Chemical Engineering Plant Cost Index-current
        scaling_factor = self.scaling_factor
        taxes = self.tax_gal * 0.00124 / 0.1 # see conversion factor in tooltip

        # Fuel specifications and conversion factors
        ethanol_density = 787.6  # ethanol density at 25 C and 1 bar in kg/m3
        Conversion_gal_to_m3 = 264.17  # gal to m3
        LHV_ethanol = 26.82  # Ethanol Lower Heating Value in MJ/kg

        # Calculation for Feedstock cost and CAPEx Cost
        dry_corn = self.ethanol_production_rate * 1e6 / ethanol_yield  # dry corn stover needed
        feedstock_cost_total = self.feedstock_cost * dry_corn / 1e6  # feedstock & handling cost in MM$

        capex_scaled = base_cost * (
                self.ethanol_production_rate / base_size) ** scaling_factor * (
                               CEPCI_current / CEPCI_base) * self.Capex_adjust_factor

        crf = (self.discount_rate * ((1 + self.discount_rate) ** self.lifetime)) / (
                (1 + self.discount_rate) ** (self.lifetime) - 1)  # CRF: Capital recovery factor

        print('Capital charge factor (CRF)=', '%.3f' % crf)

        capex_cost = crf * capex_scaled  # MM$/yr
        variable_operational_cost= (self.ethanol_production_rate*2.02/base_size)*CEPCI_current/CEPCI_base + feedstock_cost_total # MM$/yr, number 2.02 is the operational cost except feedstock cost - Byproducts credits  (From data in page 41)

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
        capture_capital = 0
        capture_fom = 0
        capture_vom = 0
        capture_taxes = 0
        capture_transp = 0
        capture_storage = 0

        if self.use_ccs == 'No':
            pass
        elif self.boilerstack_ccs == 'No':  # For fermenter
            capturecost = BECCSTea("Ethanol Production", self.ethanol_production_rate, self.ferment_cap_tech,
                                   0, self.ferment_co2_cap_percent, 0,
                                   0, 0, self.boilerstack_ccs,
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
                                   0, self.biorefinery_model, self.boilerstack_ccs,
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



        elif self.amine_regen_ccs == 'Yes':  # For fermenter, boilerstack and amine regn
            capturecost = BECCSTea("Ethanol Production", self.ethanol_production_rate, self.ferment_cap_tech,
                                   self.boiler_cap_tech, self.ferment_co2_cap_percent, self.boiler_co2_cap_percent,
                                   self.amine_co2_cap_percent, self.biorefinery_model, self.boilerstack_ccs,
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

        capital_fixed = capex_cost / (
            self.ethanol_production_rate) * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol \
                        + capture_capital + capture_fom  # $/MJ

        variable_cost = variable_operational_cost / (
            self.ethanol_production_rate) * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol + capture_vom  #$/MJ

        maintenance = 0.01 * base_cost / (
            self.ethanol_production_rate) * Conversion_gal_to_m3 / ethanol_density / LHV_ethanol  #$/MJ

        trans_storage_cost = transportation + capture_transp + capture_storage  #$/MJ
        # transportation

        # total = (capital_fixed + operational + taxes + transportation + variable_cost)  # $/MJ

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
