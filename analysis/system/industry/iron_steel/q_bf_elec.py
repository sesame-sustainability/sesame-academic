"""Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
The functional unit is 1 ton of steel
@author: Lingyan Deng
"""

"""================================================================================================================"""
#Calculate electricity required in BF.
#amount of electricity is flexible, depends on the amount of energy from other source
#q_bf0: total energy required in BF calculated in q_bf
#q_coke: energy provided via coke in BF
#q_coal: energy provided via coal in BF
#q_hblast: energy provided via hot blast in BF
def q_bf_elec(m_hi,q_bf_coke,q_bf_coal,q_hblast):  #m_sinter_ro: m_sinter+m_ro
    cr_q_bof = 15.87579 #bf energy consumption rate (7779.8+5130.5+376.2+1795.5)/950 GJ/tonne
    q_bf_elec0 = cr_q_bof * m_hi - q_bf_coke - q_bf_coal - q_hblast
    for i in q_bf_elec0.index:
        if q_bf_elec0[i] < 0:
            q_bf_elec0[i]= 0
    return q_bf_elec0

#a=q_bf_elec(15082,7779.8,5130.5,1795.5)     #default value
#print(a)

