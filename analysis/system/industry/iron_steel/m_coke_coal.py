"""Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
The functional unit is 1 ton of steel"""

"""================================================================================================================"""
#Calculate carbon needed in BF from coke and coal
#assume zero carbon associated with cog. c_coke = 269.4/337.3=0.7987
#  carbon content in coal=117.3/194.8=0.6021;

def m_coke_coal(m_bf_carbon0,f_coke,c_coke,c_coal): #m_bf_carbon0: amount of c needed in BF calculated in c_bf.py
    #f_coke: fraction of c from coke, default: 273.6*0.7987/(273.6*0.7987+194.8*0.6021)=0.65
    #c_coal: carbon content in coal (kg), default: 0.6021
    m_coke = f_coke*m_bf_carbon0/c_coke  #kg coke
    m_coal = (1-f_coke)*m_bf_carbon0/c_coal  #kg coal
    source = {"coke": m_coke,"coal":m_coal}
    return source

#a=m_coke_coal(293.762,0.6016,0.645,0.6021) # default values
#print(a)

