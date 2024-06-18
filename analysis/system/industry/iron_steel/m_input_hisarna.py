"""HIsarna steelmaking route. source: 1. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019)."""

# Linear correlation of material & energy input in HIsarna Reactor. source 1.
# material, energy input in hisarna reactor
def m_input_hisarna(m_pig_iron,c_coal,hhv_coal):
    #m_pig_iron: kg of pig iron produced in Hisarna reactor. default = 880 kg
    #q_coal: energy content in coal. Assume pulverized coal is used (table 11). default 0.45 Mton coal * 28.7 MJ/kg coal/1Mton steel =12.915 MJ/kg steel
    #c_coal: carbon content in coal. default = (1.11/44*12)/0.45 = 0.6727273 kg c/kg coal. Calculated based on 1.11 Mton of CO2 emission in Hisarna. Assuming all C are coming form coal.
    #hhv_coal: high heating value of coal. default: 28.7 MJ/kg coal.

    n_hisarna = 0.61972 #Fe conversion efficiency in Hisarna reactor. Assume Fe content in iron ore = pig iron: fe_iron_ore=fe_pig_iron =1, defaul n_hisarna = 0.88/1.42=0.61972
    cr_c_hisarna = 0.34401  # amount of c needed for pig iron production. default = c_coal*0.45/0.88. Assume fixed number.
    m_coal_hisarna = cr_c_hisarna * m_pig_iron/c_coal #kg of coal
    q_coal_hisarna = m_coal_hisarna * hhv_coal  #MJ of coal

    m_iron_ore = m_pig_iron / n_hisarna # kg of iron ore needed. assume fe content in iron ore and pig iron are 1.

    cr_q_hisarna = 14.982955 #q_cr_hisarna: total energy consumption in Hisarna. assume linear correlation to pig iron produciton. q_cr_hisarna = (0.27 PJ + 0.45 Mton*28.7 MJ/kg)/0.88 Mton = 14.982955 MJ/kg pig iron
    q_elec_hisarna = cr_q_hisarna * m_pig_iron - q_coal_hisarna #GJ of elec
    #print(q_elec_hisarna)
    """if q_elec_hisarna <0:
        q_elec_hisarna = 0
    else:
        q_elec_hisarna = cr_q_hisarna * m_pig_iron - q_coal_hisarna"""

    cr_o2_hisarna = 807.95455  # Assume linear consumption rate of oxygen in hisarna. default: 711 Nm3/ 0.88 kg steel.
    v_o2_hisarna = cr_o2_hisarna * m_pig_iron  # Nm3 of oxygen/kg of steel

    inputs = {'coal':m_coal_hisarna,'iron ore':m_iron_ore,'elec': q_elec_hisarna, 'oxygen': v_o2_hisarna}
    return inputs

#a = m_input_hisarna(0.88,0.6727273,28.7) #Default values
#print(a)





