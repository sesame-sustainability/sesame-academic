"""Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
The functional unit is 1 ton of steel"""

"""================================================================================================================"""
#Calculate sintering process energy requirement based on linear correlation q=x*(m_sinter+m_hearth).
def q_sinter(m_sinter):  #m_sinter: amount of sinter produced in sinter plant. the value calculated in m_sinter_ro.py
    e_sinter = 1.6542   #e_sinter: amount of energy need for amount of sinter produced
    # e_sinter= (67.6+1811.8+.3+5.2+180.4)MJ/1248.5 kg sinter = 2065.3/1248.5=1.6542 MJ/kg, assume fixed value
    q_sinter0=m_sinter*e_sinter
    return q_sinter0


#a=q_sinter(1248.5)     #default value
#print(a)  #result: 2065.3 MJ

