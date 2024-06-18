"""function to calculate material cost. materials mainly including iron ore, coal, natural gas, limestone, dolomite, olivine, scrap, electricity, water.
 Assume intermediate reactant/product, such as cog, bgf, dri are free.
1. Yang, F., J. C. Meerman, and A. P. C. Faaij. "Carbon capture and biomass in industry: A techno-economic analysis and comparison of negative emission options." Renewable and Sustainable Energy Reviews 144 (2021): 111028.
"""

import numpy as np
import os
import pandas as pd

dirname = os.path.dirname(__file__)
csv_path = os.path.join(dirname, 'material_cost.csv')

material_cost = pd.read_csv(csv_path, usecols = ['Year','iron ore','coal','ng','limestone','dolomite','olivine', 'scrap', 'electricity','oxygen'])

def water(m_water): 
    #m_water: tonne of water
    #water price vary when usage changes. https://www.cityofbryan.net/commercialindustrial-metering-rates/. [accessed Dec.15,2021]. [ US/ ohio rates ]
    # 1 ft3 of water =28.32 kg of water
    if m_water < 849.6:  # 30.000*28.32 tonne of water
        p_water = 1.095 # price of water p_water =$3.1/(100*28.32/1000)= 1.095 ($/tonne of water)
        cost_water = p_water * np.array(m_water) # ($)
    elif ((m_water >= 849.6) and (m_water < 5664)):  # 200.000*28.32 tonne of water
        p_water = 0.918 # $2.6/2.832 ($/tonne of water)
        cost_water = p_water * (np.array(m_water)-849.6) + 1.095*849.6 #($)
    else: #m_water > 5664:  #200.000*28.32 tonne of water
        p_water = 0.742 # 2.1/2.832 ($/tonne of water)
        cost_water = p_water * (np.array(m_water) - 5664) + 0.918*4814.4 + 1.095 * 849.6 #($)
    return cost_water

"""l=[6500,85,5452,7569458]
for w in l:
    print(f'water cost: {water(w)}')"""

def c_materials(): #material unit price.
    return material_cost.copy()

#print(f"iron ore cost: {float(c_materials()['iron ore'][1])*6}")

"""a=320
p_item = water(a)
c_item = c_materials(a,p_item)
print(c_item)"""