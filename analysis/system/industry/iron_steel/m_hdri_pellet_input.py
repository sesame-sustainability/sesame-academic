"""H-DRI-EAF system. source: 1. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019).
2. He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants." Energy Reports 3 (2017): 29-36. page 41
3. https://www.tandfonline.com/doi/pdf/10.1179/174328108X301679?needAccess=true
4. https://www.metallics.org/dri.html """

#Material input in pellet plant
#calculate Fe input from iron fines
def m_iron_fines(m_pellet):
    fe_pellet = 0.635 # Assume fixed value. source 3.
    fe_iron_fine = 0.635 # Assume fixed value. source 3.
    n_pellet = (1.4*fe_pellet)/(1.51*fe_iron_fine) #Assume fixed conversion rate in pellet plant
    m_iron_fine = m_pellet * fe_pellet/n_pellet / fe_iron_fine  # kg of pellet
    return m_iron_fine
#print(m_iron_fines(1.4)) #Default values. source 1.

#calculate flux. Assume olivine and limestone are interexchangeble, and their associated CO2 emission are the same.
def m_flux_pellet(m_pellet):
    cr_flux = (0.00003262+0.00001986)/1.4 #Assume fixed flux (olivine, limestone) consumption rate. source 1.
    m_flux = m_pellet * cr_flux  # kg of flux needed. source 1.
    return m_flux
#print(m_flux_pellet(1.4)) #default values

# calculate c supply in pellet plant
def m_c_pellet(m_pellet, f_ng, c_coal):
    fe_pellet = 0.635 # Assume fixed value. source 3.
    cr_c_pellet = 0.018822 # Assume fixed consumption rate of C =(0.6038 * 0.01135 + 0.64/49.5*0.7641)/(1.4*0.635) , linearly related to Fe kg in pellet
    #f_ng = (0.64/49.5*0.7641)/(0.6038 * 0.01135 + 0.64/49.5*0.7641) =0.590428
    # c_coal: C content in coal. default: 60.38. source 1.
    c_ng = 0.7641 # C content in NG. default: 0.7641. source 1. Assume HHV-ng = 49.5 MJ/kg
    m_c = m_pellet * fe_pellet * cr_c_pellet #Amount of carbon needed
    m_coal = m_c * (1-f_ng)/(c_coal/100) # kg coal input in pellet
    m_ng = m_c * f_ng /c_ng  # kg of ng input in pellet
    c_source = {'coal': m_coal,'ng':m_ng}
    return c_source
#print(m_c_pellet(1.4,0.590428,0.6038)) #default value. m_ng = 0.01293 kg/kg steel

#calculate amount of electricity needed in pellet plant
def q_elec_pellet(m_pellet, m_coal, m_ng, hhv_coal):
    fe_pellet = 0.635 # Assume fixed value. source 3.
    cr_q_pellet =1.210062 # =(0.01135*28.7 + 0.64 + 0.11)/(1.4 * fe_pellet)  # Assume fixed energy consumption rate MJ/kg pellet
    q_pellet = m_pellet * fe_pellet * cr_q_pellet  # total energy input MJ per kg pellet
    hhv_ng = 49.5 # defaul value 49.5 MJ/kg
    q_elec = q_pellet - m_coal*hhv_coal - m_ng * hhv_ng #MJ per kg pellet
    return q_elec

#print(q_elec_pellet(1.4,0.01135,0.01293,28.7)) # default values















