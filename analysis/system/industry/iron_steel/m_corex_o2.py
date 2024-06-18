"""model COREX
resources: 1.Prachethan Kumar, P., L. M. Garg, and S. S. Gupta. "Modelling of Corex process for optimisation of operational parameters." Ironmaking & steelmaking 33.1 (2006): 29-33.
2. Qu, Yingxia, Zongshu Zou, and Yanping Xiao. "A comprehensive static model for COREX process." ISIJ international 52.12 (2012): 2186-2193.
Default values used in this model are from the above resources"""

#Amount oxygen needed in corex. assume only related to amount of hot metal produced. source 1
def m_corex_o2(hm):
    r_o2 = 0.49076 #Assume oxygen amount has linear relation to amount of hot metal production. r_o2 = 490.76/1000. source 2.
    m_o2 = hm * r_o2 #normal cubic square meters Nm3.
    return m_o2

#a=m_corex_o2(1000) #default values
#print(a)




