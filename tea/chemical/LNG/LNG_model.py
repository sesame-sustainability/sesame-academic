"""
Created on Fri Nov 13 10:56:29 2020

@author: drakehernandez
"""




import pandas as pd
import numpy as np

def read_data_tables():
    shipping = pd.read_csv('shipping.csv')
    return shipping

shipping = read_data_tables()

print("Delivery Point")
ui = input()

print("Power Price [$/MWh]")
power_price = float(input())



discount_rate = .1  
lifetime_elect = 20 
capacity_factor = .95 
MMBtu_per_ton = 48.6 
o_m = .04 
CapEx = 660 
CapEx_MMBtu = CapEx / MMBtu_per_ton  
power_consumption = 141.86 * 2 
plant_size = 10000000 
plant_size_MMBtu = plant_size * MMBtu_per_ton



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
    
shipping_cost = shipping.iloc[index,1]



hours_operation = 8760 * capacity_factor 
LNG_output = capacity_factor * plant_size_MMBtu



crf = (discount_rate * ((1 + discount_rate)**lifetime_elect)) / ((1 + discount_rate)**(lifetime_elect) - 1) 

Overnight_CapEx = plant_size_MMBtu * CapEx_MMBtu
annual_CapEx = Overnight_CapEx * crf

FOM = Overnight_CapEx * o_m

Power_cost = power_price * power_consumption * capacity_factor * 8760

total_charge = annual_CapEx + FOM +  Power_cost

unit_cost = total_charge / (LNG_output)
    



DES_cost = shipping_cost + unit_cost 

FOB_cost = unit_cost 

