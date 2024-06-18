#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import us, statistics


from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from core.tea import TeaBase
from core import validators, conditionals

PATH = os.getcwd() + "/tea/chemical/LNG/"

class LNGTEA(TeaBase):
    unit = '$/MMBtu'

    @classmethod
    def user_inputs(cls):
        return [
            CategoricalInput('dest','Destination',
            defaults=[Default('Shanghai')],
                     tooltip = Tooltip(
            'Default is a representative transportation cost (2.6 $/MMBTU), from US to Shanghai. Minimum cost collected so far: US to Rotterdam (1.2 $/MMBTU); maximum: US to East India (2.9 $/MMBTU)',
            source='OIES',
            source_link='https://www.oxfordenergy.org/wpcms/wp-content/uploads/2019/03/Outlook-for-Competitive-LNG-Supply-NG-142.pdf',
            )
                        ),
            ContinuousInput('Power_Price','Electricity Price',
                            unit='$/MWh',
                            defaults=[Default(88)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(1000)],
                            tooltip=Tooltip(
                                'Power is used in LNG production. This includes 66 for power generation and 14 $/MWh distribution.',
                                source='Statistica',
                                source_link='https://www.statista.com/statistics/190680/us-industrial-consumer-price-estimates-for-retail-electricity-since-1970/; https://www.eia.gov/outlooks/aeo/data/browser/#/?id=8-AEO2021&region=0-0&cases=ref2021&star',
                            )
                            ),
            ContinuousInput('discount_rate', 'Discount Rate',
                            unit='%',
                            defaults=[Default(10)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                            tooltip=Tooltip(
                                'Amortized capital cost per year ($/yr) = capital recovery factor * total capital cost ($); crf = (discount_rate * ((1 + discount_rate)**lifetime)) / ((1 + discount_rate)**(lifetime) - 1). Havent found LNG-specific discount rate - using NREL biofuel project discount factor as a proxy for the default value.',
                                source='NREL 2011 biofuel as a proxy',
                                source_link='https://www.nrel.gov/docs/fy11osti/47764.pdf',
                            )
                            ),

            ContinuousInput('capacity_factor', 'Capacity Factor',
                            unit='%',
                            defaults=[Default(56)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                            tooltip=Tooltip(
                                'Percent of the facility design capacity is used to produce product, e.g., mathematically the number of hours in a year the facility runs, divided by 24*365 hours. No LNG-specific capacity factor has been found, so the natural gas to power capacity factor is used as a proxy here.',
                                source='EIA',
                                source_link='https://www.eia.gov/todayinenergy/detail.php?id=25652#:~:text=The%20capacity%20factor%20of%20the,over%20the%20past%20few%20years.',
                            )
                            ),

            ContinuousInput('lifetime', 'Lifetime',
                            unit='year',
                            defaults=[Default(30)],
                            validators=[validators.integer(), validators.gte(0)],
                            tooltip=Tooltip(
                                '30 year average from OIES is also consistent with NREL ATB model defaults for most technologies, such as natural gas power plant',
                                source='OIES',
                                source_link='https://www.oxfordenergy.org/wpcms/wp-content/uploads/2018/02/The-LNG-Shipping-Forecast-costs-rebounding-outlook-uncertain-Insight-27.pdf',
                            )
                            ),

            ContinuousInput('ng_price', 'Natural Gas Price',
                            unit='$/MMBtu',
                            defaults=[Default(3.9)],
                            validators=[validators.integer(), validators.gte(0)],
                            tooltip=Tooltip(
                                'Cost of the natural gas used as feedstock and energy source in the LNG production process. Note: this default represents price of natural gas sold to industrial users, which is different from the price sold to electric power producers (2.99 $/MMBTU, a 23% difference from the Industrial Price)',
                                source='EIA US 2019 value',
                                source_link='https://www.eia.gov/dnav/ng/ng_pri_sum_a_EPG0_PIN_DMcf_a.htm',
                            )
                            ),
            ContinuousInput(
                'tax_rate', 'Tax',
                unit='%',
                defaults=[Default(6.35)],
                validators=[validators.numeric(), validators.gt(0), validators.lt(100)],
                tooltip=Tooltip(
                    "The default value represents sales tax, which varies by states and specific use cases. 6.35% represents US averegae sales tax.",
                ),
            ),

        ]

    def __init__(self, lca_pathway=None):
        self.lca_pathway = lca_pathway
        self.shipping_distance = pd.read_csv(PATH + "shipping.csv")
        super().__init__()

#Read Data

    def get_destination_type(self):
        if self.lca_pathway:
            process_user_inputs = self.lca_pathway['Process']['user_inputs']
            dest_loc = process_user_inputs.get("Destination")
        else:
            dest_loc = self.dest
        return dest_loc
  
 #prepare to read table values come from OIES study p. 33 -- https://www.oxfordenergy.org/wpcms/wp-content/uploads/2019/03/Outlook-for-Competitive-LNG-Supply-NG-142.pdf      
    def get_cost_breakdown(self):
        dest= self.dest
        if dest == 'Rotterdam':
            index = 0
        elif dest == 'West India':
            index = 1
        elif dest == 'East India':
            index = 2
        elif dest == 'Taiwan':
            index = 3
        elif dest == 'Shanghai':
            index = 4
        elif dest == 'Beijing':
            index = 5
        elif dest == 'Osaka':
            index = 6
        elif dest == 'Tokyo':
            index = 7
        

        self.capacity_factor = self.capacity_factor/100
        self.discount_rate = self.discount_rate/100

#Assumptions

#Liequefaction

        MMBtu_per_ton = 48.6 # Confirmed LHV conversion based on Qatargas - https://qp.com.qa/en/Pages/ConversionFactor.aspx
        o_m = .04 # percentage of total CapEx - from https://era.library.ualberta.ca/items/4b665316-ad4c-41a6-9312-a971b0b2d8ce/view/831e3938-1be1-4a67-bf4c-a895fc2c57c5/SETA_18_140.pdf
        CapEx = 660 # $/tons per year capacity see p. 14 - https://www.oxfordenergy.org/wpcms/wp-content/uploads/2019/03/Outlook-for-Competitive-LNG-Supply-NG-142.pdf
        CapEx_MMBtu = CapEx / MMBtu_per_ton  # $/MMBtu per year
#        power_consumption = 141.86 * 2 # MW - For 10 Million ton per annum site from p. 23 of https://era.library.ualberta.ca/items/4b665316-ad4c-41a6-9312-a971b0b2d8ce/view/831e3938-1be1-4a67-bf4c-a895fc2c57c5/SETA_18_140.pdf
        plant_size = 10000000 #tons per year (10 Millon Tons Per Annum facility)
        plant_size_MMBtu = plant_size * MMBtu_per_ton


##################
##Upstream Model##
##################

    
#get values based off user input
        shipping_cost = self.shipping_distance.iloc[index,1]


#calculations

        LNG_output = self.capacity_factor * plant_size_MMBtu
        LNG_input = LNG_output* (10**6+96923)/10**6 #Input-output ratio is taken from GREET 2019 Cell AI41 of 'NG' tab, where 96923 is the natural gas in but needed in liquefaction per 1 mmbtu LNG produced, with zero feed loss
        crf = (self.discount_rate * ((1 + self.discount_rate)**self.lifetime)) / ((1 + self.discount_rate)**(self.lifetime) - 1) # %

        Overnight_CapEx = plant_size_MMBtu * CapEx_MMBtu
        annual_CapEx = Overnight_CapEx * crf

        FOM = Overnight_CapEx * o_m # o_m fraction=4% is taken from the referenced paper. There is no breakdown or further explanation for this 4%, but because it is applied on the capital cost basis, we consider it the FOM cost because VOM varies with LNG production level not capital cost. https://era.library.ualberta.ca/items/4b665316-ad4c-41a6-9312-a971b0b2d8ce/view/831e3938-1be1-4a67-bf4c-a895fc2c57c5/SETA_18_140.pdf

        Unit_power_cost = 1978 * self.Power_Price * 2.93*10**(-7)  #$/MMBtu LNG; 1978 btu electricity/MMBtu LNG needed in liquefaction (GREET 2019 Cell AI47 in 'NG' tab); 2.93*10^-7 MWh/btu
        Power_cost = Unit_power_cost*LNG_output
#        Power_cost = self.Power_Price * power_consumption * self.capacity_factor * 8760
        Fuel_cost = LNG_input*self.ng_price
        Unit_fuel_cost = Fuel_cost/LNG_output
        total_charge = annual_CapEx + FOM +  Power_cost + Fuel_cost + shipping_cost #before tax

        unit_cost = total_charge / (LNG_output) #before tax

        tax = self.tax_rate*unit_cost/100 #$/MMBtu
    


#####################
## Midstream Model ##
#####################

        DES_cost = shipping_cost + unit_cost #Delivered ex-ship -- shipper responsible for bearing cost of shipping

        FOB_cost = unit_cost #Free on Board -- shipper not responsible for shipping cost


        capital = {'Capital Cost': annual_CapEx / LNG_output} #capital cost of natural gas liquefaction
        fixed = {'FOM: Fixed Operation and Maintenance': FOM / LNG_output}
        vom = {'VOM: Power & transport': Unit_power_cost + shipping_cost }


        #####################
        ## Cost Breakdown  ##
        #####################

        cost_breakdown = {"Capital": capital,
                          "Fixed": fixed,
                          "Variable": vom,
                          "Fuel": Unit_fuel_cost,
                          "tax": tax
                              }

        return cost_breakdown