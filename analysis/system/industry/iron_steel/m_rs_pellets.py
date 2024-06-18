"""model COREX
resources: 1.Prachethan Kumar, P., L. M. Garg, and S. S. Gupta. "Modelling of Corex process for optimisation of operational parameters." Ironmaking & steelmaking 33.1 (2006): 29-33.
2. Qu, Yingxia, Zongshu Zou, and Yanping Xiao. "A comprehensive static model for COREX process." ISIJ international 52.12 (2012): 2186-2193.
Default values used in this model are from the above resources"""

#Amount of lump or pellets input in reduced shaft
def m_rs_pellets(m_dri,fe_dri,fe_pellets):
    #m_dri: kg of dri needed calculated in m_dri_fore.py
    conv_rs = 0.99187 #Fe in DRI/Fe in pellets = (980*0.88)/(1297.87*0.67)=0.99187. Calculated assume fe content in pellets is 0.67. assume fixed conversion rate.source 1 & 2
    m_pellet = m_dri*fe_dri/conv_rs/fe_pellets
    return m_pellet

#a=m_rs_pellets(980.14,0.88,0.67) #default values
#print(a)




