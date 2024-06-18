"""H-DRI-EAF system. source: 1. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019).
2. He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants." Energy Reports 3 (2017): 29-36. page 41
3. https://www.tandfonline.com/doi/pdf/10.1179/174328108X301679?needAccess=true
4. https://www.metallics.org/dri.html """

#Material input in water electrolyser
# water consumption
def m_water(m_h2):
    cr_water = 9 # assume 100% water electrolized to H2 and O2
    m_water_input = m_h2 * cr_water # water needed
    return m_water_input
#print(m_water(0.043333)) # default amount of hydrogen produced

def q_elec_water(m_h2):
    cr_elec = 244153.846154 # default electricity consumption = 10.58/(0.00039*2/18) GJ/tonne h2
    q_elec = m_h2 * cr_elec
    return q_elec
# print(q_elec_water(0.043333))















