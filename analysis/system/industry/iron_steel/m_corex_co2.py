"""model COREX
resources: 1.Prachethan Kumar, P., L. M. Garg, and S. S. Gupta. "Modelling of Corex process for optimisation of operational parameters." Ironmaking & steelmaking 33.1 (2006): 29-33.
2. Qu, Yingxia, Zongshu Zou, and Yanping Xiao. "A comprehensive static model for COREX process." ISIJ international 52.12 (2012): 2186-2193.
Default values used in this model are from the above resources"""

#Amount co2 emission associated with coal used in corex
def m_corex_co2(m_coal,c):
    #m_coal: amount of coal consumed in corex. kg
    #c: carbon fraction in coal
    m_co2 = m_coal * c/100 *44/12  #amount of co2 emission kg
    return m_co2
#a=m_corex_co2(953.2,83.3) #default values from source 2
#print(a)
