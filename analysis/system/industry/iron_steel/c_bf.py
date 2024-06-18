"""Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
The functional unit is 1 ton of steel
@author: Lingyan Deng
"""

"""================================================================================================================"""
#Calculate total carbon needed for reduction in BF based on linear correlation of Fe in sinter+raw ore and C in coke+coal

def c_bf(fe_hi0_upstream):
    i_re = 0.3534 #(273.6*0.7987 + 194.8*0.6021)/(786.5+163.7)=0.3534 tonne C/tonne Fe. i_re: amount of C needed to reduce required amount of Fe. Assume fixed i_re
    m_bf_carbon0=fe_hi0_upstream*i_re #fe_hi0_upstream: amount of Fe from sinter + raw ore calculated in fe_bf_upstream.py
    return m_bf_carbon0 #amount of C (tonne) needed for BF Fe reduction

#a=c_bf(950.2)
#print(a)

