"""Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
The functional unit is 1 ton of steel"""

"""================================================================================================================"""
#calculate fuel (coal, coke, cog, bfg) mass based on its low heating value (lhv: MJ/kg)
#source_lhv={"coal":26.33727,"coke":30.5977,"cog":34.726,"bfg":14.901}
def m_fuel(q_fuel,lhv):
    m_fuel0 = q_fuel/lhv
    return m_fuel0

#a=m_fuel(10320.6,30.5977) # default value for coke
#print(a)
