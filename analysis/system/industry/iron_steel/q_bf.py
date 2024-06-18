"""Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
The functional unit is 1 ton of steel"""

"""================================================================================================================"""
#Calculate total energy required in BF.
# Since the Fe content in Sinter (0.63) and Raw ore (0.64) is roughly the same, we can assume the total energy required is linearly related to the mass of sinter+raw ore
def q_bf(m_sinter,m_ro):  #m_sinter_ro: m_sinter+m_ro
    e_bf = 10.0266 #e_bf: energy intensity for hot iron produciton in BF. assume fixed value
    # e_bf=(7779.8+5130.5+376.2+1759.5)MJ/(1248.5+255.7) kg=15082MJ/1504.2kg=10.0266 MJ/kg (sinter+raw ore)
    q_bf0 = (m_sinter + m_ro) * e_bf
    return q_bf0

#a=q_bf(1504.2)     #default value
#print(a)

