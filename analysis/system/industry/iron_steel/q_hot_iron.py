"""
Functional unit: 1 tonne of steel
Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
"""

"""================================================================================================================"""
#Calculate energy associated with hot iron input in BOF
def q_hot_iron(m_hi0):
    e_hi=9.68       #"Assume hot iron energy intensity is fixed with default value 9.68 GJ/tonne Hot iron, #9195.7/950=9.68
    q_hi = m_hi0*e_hi  #total energy required for the amount of hot iron input
    return q_hi


#a=q_hot_iron(950)
#print(a)

