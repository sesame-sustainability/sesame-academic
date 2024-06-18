"""Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
The functional unit is 1 ton of steel"""

"""================================================================================================================"""
#Calculate air input in BOF based on hot iron mass flow.
#Scrap is relatively pure (99% Fe). Assume the air is only needed for hot iron reduction.
def m_air(m_hi0):
    cr_air=float(input("Input air consumption rate in kg air/kg hot iron, default: 0.11:"))  #(73+28.9+1.8)/950=0.11
    m_air0 = m_hi0*cr_air
    return m_air0

# a=m_air(950) #default hot iron amount
# print(a)
