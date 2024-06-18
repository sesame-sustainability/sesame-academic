"""
Function unit: 1 tonne of steel
HIsarna steelmaking route. source: 1. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019).
2.He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants." Energy Reports 3 (2017): 29-36.
"""
import numpy as np
#Calculate CO2 emission in ASU
def m_co2_asu(v_o2, co2_elec): # CO2 emisison due to electricity utilization for air seperation
    #v_o2: Nm3 of oxygen needed
    #co2_elec: electricity carbon intensity tonne CO2/GJ.
    cr_elec = 0.0015 #default electricity consumption rate cr_elec = 52.5 GJ/(35000) Nm3 O2. source 1.
    q_elec_asu = cr_elec * v_o2 # GJ electricity needed. 
    m_asu_co2 = np.array(q_elec_asu) * np.array(co2_elec) # tonne CO2
    m_asu_o2 = v_o2/22.4*32/1000 # tonne of o2 separated
    asu_elec = {'elec': q_elec_asu,'co2':m_asu_co2,'o2':m_asu_o2}
    return asu_elec

#a= m_co2_asu(35000,707.2/3600) #Default values for EAF
#print(a)

