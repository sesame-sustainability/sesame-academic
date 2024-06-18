"""Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
The functional unit is 1 ton of steel"""

"""================================================================================================================"""
#calculate CO2 emission according to energy consumption via linear correlation
# CO2 emission source includes: coke, coal, cog, electricity, air, steam, fresh water, hot blast
#Dictionary to store carbon intensity of energy kg CO2/MJ:
#s_co2 = {"coke": 0.077297,"coal":0.083832,"cog":0.077297,"elec":0.086275,
#         "air":0.083908,"steam":0.088567,"fwater":0.122222,"hot_blast":0.083932}
import numpy as np
def m_e_co2(qs,i_co2):
    #q: amount of energy provided MJ
    #i_co2: carbon intensity of the energy kg CO2/MJ
    m_co2 = []
    for i, q in enumerate(qs):
        if q<0:
            q = 0
            m_co2_new = q
            #m_co2.append(m_co2_new)
        else:
            q = qs[i]
            m_co2_new = np.array(q) * np.array(i_co2[i])
            #m_co2.append(m_co2_new)
    return m_co2_new

#a=m_e_co2(10320.6, 0.077297)  #default value for coke i_co2 = (0.8076*269.4*44/12)/10320.6=0.0773
#print(a)  #a=797.757

"""qs = [12,-3,4,32]
i_co2 = [2,3,4,5]
a=m_e_co2(qs,i_co2)
print(a)"""