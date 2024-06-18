"""HIsarna steelmaking route. source: 1. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019).
2.He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants." Energy Reports 3 (2017): 29-36."""
# Linear correlation of material & energy input in HIsarna Reactor. source 1.
#Co2 emission associated with Hisarna reactor.
import numpy as np
def m_co2_hisarna_bof(m_pig_iron,q_elec_bof,fe_pig_iron,co2_elec):
    #q_elec_bof: MJ electricity/kg steel
    #co2_elec: electricity carbon intensity, assume India 2020 electricity carbon intensity g co2/kWh
    #fe_pig_iron: Fe content in pig iron. defaul: 0.965053. Assume balanced with c. source 2.
    m_co2_pig_iron = (1-fe_pig_iron)*m_pig_iron*44/12 #CO2 emission from pig iron c content. about 112.76 kg CO2/1 ton steel
    m_co2_elec_bof = np.array(q_elec_bof) * np.array(co2_elec) # CO2 emission from electricity. about 19.220581 kg CO2/kg steel
    co2_source = {'pig iron':m_co2_pig_iron,'elec':m_co2_elec_bof}
    return co2_source # kg CO2/ton steel

#a = m_co2_hisarna_bof(880,97.87,0.965053,707) #Default values
#print(a)





