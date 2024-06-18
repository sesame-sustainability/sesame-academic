#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 10:56:29 2020

@author: drakehernandez
"""


###Notes###
# Ask for natural gas industrial price by state from Ragini


import pandas as pd
import numpy as np

#Read Data
def read_data_tables():
    shipping = pd.read_csv('shipping.csv')
    return shipping

shipping = read_data_tables()

print("Delivery Point")
ui = input()

print("Power Price [$/MWh]")
power_price = float(input())


#Assumptions

#Liequefaction
discount_rate = .1  # %
lifetime_elect = 20 # yrs
capacity_factor = .95 # %
MMBtu_per_ton = 48.6 # Confirmed LHV conversion based on Qatargas - https://qp.com.qa/en/Pages/ConversionFactor.aspx
o_m = .04 # percentage of total CapEx - from https://era.library.ualberta.ca/items/4b665316-ad4c-41a6-9312-a971b0b2d8ce/view/831e3938-1be1-4a67-bf4c-a895fc2c57c5/SETA_18_140.pdf
CapEx = 660 # $/tons per year capacity see p. 14 - https://www.oxfordenergy.org/wpcms/wp-content/uploads/2019/03/Outlook-for-Competitive-LNG-Supply-NG-142.pdf
CapEx_MMBtu = CapEx / MMBtu_per_ton  # $/MMBtu per year
power_consumption = 141.86 * 2 # MW - For 10 Million ton per annum site from p. 23 of https://era.library.ualberta.ca/items/4b665316-ad4c-41a6-9312-a971b0b2d8ce/view/831e3938-1be1-4a67-bf4c-a895fc2c57c5/SETA_18_140.pdf
plant_size = 10000000 #tons per year (10 Millon Tons Per Annum facility)
plant_size_MMBtu = plant_size * MMBtu_per_ton


##################
##Upstream Model##
##################

#prepare to read table values come from OIES study p. 33 -- https://www.oxfordenergy.org/wpcms/wp-content/uploads/2019/03/Outlook-for-Competitive-LNG-Supply-NG-142.pdf 
if ui == 'Rotterdam':
    index = 0
elif ui == 'West India':
    index = 1
elif ui == 'East India':
    index = 2
elif ui == 'Taiwan':
    index = 3
elif ui == 'Shanghai':
    index = 4
elif ui == 'Beijing':
    index = 5
elif ui == 'Osaka':
    index = 6
elif ui == 'Tokyo':
    index = 7
    
#get values based off user input
shipping_cost = shipping.iloc[index,1]


#calculations

hours_operation = 8760 * capacity_factor # hr/yr
LNG_output = capacity_factor * plant_size_MMBtu



crf = (discount_rate * ((1 + discount_rate)**lifetime_elect)) / ((1 + discount_rate)**(lifetime_elect) - 1) # %

Overnight_CapEx = plant_size_MMBtu * CapEx_MMBtu
annual_CapEx = Overnight_CapEx * crf

FOM = Overnight_CapEx * o_m

Power_cost = power_price * power_consumption * capacity_factor * 8760

total_charge = annual_CapEx + FOM +  Power_cost

unit_cost = total_charge / (LNG_output)
    


#####################
## Midstream Model ##
#####################

DES_cost = shipping_cost + unit_cost #Delivered ex-ship -- shipper responsible for bearing cost of shipping

FOB_cost = unit_cost #Free on Board -- shipper not responsible for shipping cost

