"""
Function unit: 1 tonne of steel
Equations to Calculate CAPEX of plants.
source: 1. Yang, F., J. C. Meerman, and A. P. C. Faaij. "Carbon capture and biomass in industry:
A techno-economic analysis and comparison of negative emission options." Renewable and Sustainable Energy Reviews 144 (2021): 111028.
2. Seider, Warren D., et al. "Product and process design principles: synthesis." Analysis and Evaluation 4 (2004)."""

import numpy as np
import os
import pandas as pd

dirname = os.path.dirname(__file__)
csv_path = os.path.join(dirname, 'capex.csv')

capexes = pd.read_csv(csv_path, usecols=['Equipments','shape factor','Base Scale','Process_plant_cost'])

#calculate the capex based on the reference cost, the capacity of the reference and the plant to be calculated, and the CEPCI value
def capexs(capacity2,cepci1,cepci2,ppp2):
    # assume six tenth rule for the capacity expansion. source: Warren D. Seider et al. - Product and Process Design Principles_ Synthesis, Analysis and Evaluation
    #capacity1,2: capacity of the units
    #sf: shap factor, usualy around 0.67.
    #cepci1,2: chemical engineering plant cost index
    #ppp1,2: purchasing power parity.
    #database
    processes = capexes['Equipments'][0:9] #processes
    sf = capexes['shape factor'][0:9] #shap factors
    capacity1 = capexes['Base Scale'][0:9] #base scale
    cost1 = capexes['Process_plant_cost'][0:9] #process plant cost. euro.
    ppp1 = 0.687 #the source base cost is based on 2017 EU27.
    cost2 = [np.array(cost1) * (np.array(capacity2) / np.array(capacity1)) ** np.array(sf) * \
            cepci2 / cepci1 * ppp2 / ppp1] # local unit currency. depends on ppp2.
    process_capex = [dict(zip(processes, cost)) for cost in cost2][0] #assign the value in a list to keys in a list one by one

    return process_capex #returns a dictionary of processes and its cost.

#achieve adding the capex according to the capacity. if the next year's capacity is higher, add additional cost, if lower or equal, keep the capex as previous.
def capex_add(plant,capacity2,cepci1,cepci2,ppp2):
    t_cost2=[]
    cost_add2 =[]
    for i, capacity in enumerate(capacity2):
        if i==0: #capacity ==capacity2[0]: #the first number, which in 2020
            cost_add = capexs(capacity,cepci1,cepci2,ppp2)[plant] #assume the cost is whatever the plant size needed
            t = cost_add
        elif i>=1:
            if capacity <= max(capacity2[0:i]): #if size is samller or equal, add no additional capacity
                cost_add = capexs(0,cepci1,cepci2,ppp2)[plant]
                t = t_cost2[-1]+cost_add
            elif capacity > max(capacity2[0:i]):
                cost_add = capexs(capacity - max(capacity2[0:i]),cepci1,cepci2,ppp2)[plant] #if size is bigger than previous one, add additional capacity
                t = t_cost2[-1] + cost_add
        cost_add2.append(cost_add) # local current unit. depends on ppp2
        t_cost2.append(t) # local current unit. depends on ppp2
    capex_result = {'Additional':cost_add2,'Total':t_cost2}
    return capex_result

# capacity2 = [1900000,2100000,6200000,320000,6100000]
# cepci1=576
# cepci2=594
# ppp2 = 21
# #cost = capexs(capacity2,cepci1,cepci2,ppp2)
# cost = capex_add('Coke plant',capacity2,cepci1,cepci2,ppp2)
# print(f'cost of coke plant: {cost}')


