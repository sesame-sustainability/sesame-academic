"""Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
The functional unit is 1 ton of steel"""

"""================================================================================================================"""
#Calculate electricity needed in coke plant.

def q_coking(m_coke): #m_coke: amunt of coke produced in coking plant
    e_coking = 4.182   #e_coking: energy needed/ kg coke roduced = (1368.2+42.5)MJ/337.3 kg = 1410.7/337.3=4.182 MJ/kg
    q_coking0 = m_coke*e_coking
    return q_coking0 # energy input required for coking plant (not counting coke's energy


#a=q_coking(337.3)     #default value
#print(a)    #q_coking0 = 1410.7 MJ

