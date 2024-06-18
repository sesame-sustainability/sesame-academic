"""HIsarna steelmaking route. source: 1. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019)."""

# Linear correlation of material & energy input in HIsarna Reactor. source 1.
#CO2 emission associated with electricity use in Hisarna-CCS
import numpy as np
def m_co2_ccs_hisarna(m_coal_co2,co2_elec):
    #m_coal_co2: CO2 emission from Hisarna reactor that's associated with coal. Coal is the only energy input in HIsarna reactor
    #m_co2_hisarna: amount of CO2 to be captured using cryogenic distillation+compression process and sent for storage.
    #co2_elec: electricity carbon intensity. tonne co2/GJ
    cr_elec_ccs_hisarna =0.504505 #electricity consumpiton rate for hisarna-ccs. default = (0.84-0.28)PJ/1.11 Mton.
    q_elec_ccs = cr_elec_ccs_hisarna * m_coal_co2 # 1PJ/Mton= 1MJ/kg = GJ/tonne
    #print(q_elec_ccs)
    m_co2_ccs_hisarna = np.array(q_elec_ccs) * np.array(co2_elec) #kg CO2/kg of steel
    output = {'co2':m_co2_ccs_hisarna,'elec':q_elec_ccs}
    return output

#a = q_elec_ccs_hisarna(1.11,0.707) #Default values, Indian 2020 electricity carbon intensity=0.707
#print(a)





