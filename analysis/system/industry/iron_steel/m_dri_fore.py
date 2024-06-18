"""
Functional unit: 1 tonne of hot metal
model COREX
resources: 1.Prachethan Kumar, P., L. M. Garg, and S. S. Gupta. "Modelling of Corex process for optimisation of operational parameters." Ironmaking & steelmaking 33.1 (2006): 29-33.
2. Qu, Yingxia, Zongshu Zou, and Yanping Xiao. "A comprehensive static model for COREX process." ISIJ international 52.12 (2012): 2186-2193.
Default values used in this model are from the above resources"""
#Amount of Fe from fine ore and dri input in melter-gasifier
def m_dri_fore(hm,f_dri,fe_dri,fe_fore):
    #hm: hot metal produced tonne
    #f_dri:Fraction of DRI, balanced by fine ore, default:0.902
    #fe_dri: Fe content in DRI. default: 0.88. Source: Prakash, S., et al. "Simulation of energy dynamics of electric furnace steelmaking using DRI.Ironmaking & steelmaking 34.1 (2007): 61-70.
    #fe_fore: Fe content in fine ore. default:0.64, from source 1.
    conv_mg = 0.99756 # conversion efficiency of DRI and fine ore to hot metal in melter-gasifier. Assume fixed value
    fe_hm = 0.954 #Fe content in hot metal. defaul: 0.954, from source 1
    fe_mg_upstream = hm * fe_hm/conv_mg  #Total Fe needed from melter-gasifier uperstream: DRI + fine ore tonne.
    m_dri = fe_mg_upstream * f_dri / fe_dri  #Amount of DRI needed tonne
    m_fore = fe_mg_upstream * (1-f_dri) / fe_fore #Amount of fine ore needed tonne
    source = {"dri":m_dri,"fine ore":m_fore}
    return source
#a=m_dri_fore(1000,0.902,0.88,0.64) #default values
#print(a)





