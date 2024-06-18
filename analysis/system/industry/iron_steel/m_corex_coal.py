"""model COREX
resources: 1.Prachethan Kumar, P., L. M. Garg, and S. S. Gupta. "Modelling of Corex process for optimisation of operational parameters." Ironmaking & steelmaking 33.1 (2006): 29-33.
2. Qu, Yingxia, Zongshu Zou, and Yanping Xiao. "A comprehensive static model for COREX process." ISIJ international 52.12 (2012): 2186-2193.
Default values used in this model are from the above resources"""

#Amount coal needed. assume linear correlation to amount of pellets/lump and fine ore needed. source 1
def m_corex_coal(m_pellet,m_fore, f_dri,hhv):
    #m_pellet: kg pellet
    #m_fore: kg fine ore
    #hhv: high heating value of fuel MJ/kg fuel
    core = 28.372 #linear correlation factor core=q_coal/(Fe from pellets+fe from fine ore)=35.274*953.2/(1297.87*0.902+147*0.098)
    q_coal = (m_fore*(1-f_dri) + m_pellet * f_dri) * core
    m_coal = q_coal/hhv
    return m_coal

# a=m_corex_coal(1297.87,147,0.902,35.27) #default values
# print(a)
