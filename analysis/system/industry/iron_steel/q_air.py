"""Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
The functional unit is 1 ton of steel"""

"""================================================================================================================"""
#Calculate energy associated with air input in BOF
def q_air(m_air):
    e_air=8.386 #float(input("Input air energy intensity MJ/kg air, default: 8.386:"))
    #(598.7+270.9)/(73+28.9+1.8)=8.386
    q_air = m_air*e_air
    return q_air

#m_air=103.7 # get air in kg
#a=q_air(m_air)
#print(a)

