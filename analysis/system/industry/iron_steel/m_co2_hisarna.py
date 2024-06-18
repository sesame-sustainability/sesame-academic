"""HIsarna steelmaking route. source: 1. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019).
2.He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants." Energy Reports 3 (2017): 29-36."""
# Linear correlation of material & energy input in HIsarna Reactor. source 1.
#Co2 emission associated with BOF.
import numpy as np
def m_co2_hisarna(m_coal,q_elec_hisarna,c_coal, co2_elec):
    #m_coal: coal comsumption rate in Hisarna reactor kg coal/kg pig iron
    #c_coal: c content in coal
    #co2_elec: g co2/kWh
    m_coal_co2 = m_coal * c_coal *44/12 #kg co2/kg pig iron
    m_elec_co2 = np.array(q_elec_hisarna) * np.array(co2_elec) # kg co2/kg pig iron
    co2_source = {'coal':m_coal_co2,'elec':m_elec_co2}
    return co2_source
#a = m_co2_hisarna(450,0.27, 0.637, 707) #Default values
#print(a)





