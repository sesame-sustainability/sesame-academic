"""
Function unit: 1 tonne CO2
source: 1. Koelbl, B. S., et al. "Uncertainty in the deployment of Carbon Capture and Storage (CCS): A sensitivity analysis to techno-economic parameter uncertainty." International Journal of Greenhouse Gas Control 27 (2014): 81-102.
goal of this file: calculate the cost of ccs transportation and storage. 
"""

import numpy as np
import os
import pandas as pd

dirname = os.path.dirname(__file__)
co2_transport_path = os.path.join(dirname, 'carbon_transport.csv')
ccs_transport = pd.read_csv(co2_transport_path, usecols=['Transport distance','cost'])

co2_storage_path = os.path.join(dirname, 'carbon_storage.csv')
ccs_storage = pd.read_csv(co2_storage_path, usecols=['CO2 storage type','cost'])
options_storage = list(ccs_storage['CO2 storage type'])

def co2_transport(distance):
    if (distance <50):
        price = ccs_transport['cost'][0] # co2 transportation cost ($_2005/tCO2/km)
    elif ((distance >=50) and (distance < 200)):
        price = ccs_transport['cost'][1] # co2 transportation cost ($_2005/tCO2/km)
    elif ((distance >=200) and (distance < 500)):
        price = ccs_transport['cost'][2] # co2 transportation cost ($_2005/tCO2/km)
    elif ((distance >=500) and (distance < 2000)):
        price = ccs_transport['cost'][3] # co2 transportation cost ($_2005/tCO2/km)
    else: #distance >=2000
        price = ccs_transport['cost'][4] # co2 transportation cost ($_2005/tCO2/km)
    cost_transport = price * distance * 1.33 #($_2020/tCO2). 1.33 inflation rate conversion: Ref. https://www.in2013dollars.com/us/inflation/2005?endYear=2020&amount=1 [Accessed Ja. 3rd, 2022]
    return cost_transport


def co2_storage(i):
    price = ccs_storage['cost'][i] # co2 storage cost ($_2005/tco2 stored)
    cost_storage = price * 1.33 #($_2020/tCO2). 1.33 inflation rate conversion: Ref. https://www.in2013dollars.com/us/inflation/2005?endYear=2020&amount=1 [Accessed Ja. 3rd, 2022]
    return cost_storage


