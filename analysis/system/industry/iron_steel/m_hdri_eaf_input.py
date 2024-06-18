"""H-DRI-EAF system. source: 1. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019).
2. He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants." Energy Reports 3 (2017): 29-36. page 41""
3. https://www.metallics.org/dri.html """
#Material input in EAF
# Fe input in EAF
import pandas as pd
def m_fe_eaf(m_crude_steel,f_scrap,fe_dri): #calculate the material balance for Fe
    #m_crude_steel: amount of crude steel to be produced
    #Assume scrap steel and stainless steel are the same since they both has Fe content of 99%.
    # f_scrap = (0.12 * fe_scrap + 0.19 * fe_stainless_steel)/(0.98 * fe_dri + 0.12 * fe_scrap + 0.02553 * fe_carbon_steel + 0.19 * fe_stainless_steel) = 0.26094
    fe_scrap = 0.99 # Default scrap Fe content. source 2.
    # fe_dri = 0.861 #Default DRI Fe content. source 3.
    fe_carbon_steel = 0.997 # Default carbon steel Fe content. source 1.
    fe_stainless_steel = 0.99 # Default stainless steel Fe content. source 1.
    fe_crude_steel = 0.9996 #Default crude steel Fe content. source 1.
    n_fe_eaf = 1*fe_crude_steel / (0.98 * fe_dri + 0.12 * fe_scrap + 0.02553 * fe_carbon_steel + 0.19 * fe_stainless_steel) # Assumed fixed EAF Fe converison rate based on source 1. calculated to be n_fe_eaf = 0.765807
    #print(n_fe_eaf)

    f_carbon_steel = 0.02553 * fe_carbon_steel / (0.98 * fe_dri + 0.12 * fe_scrap + 0.02553 * fe_carbon_steel + 0.19 * fe_stainless_steel) # calculated to be 0.021642. Assume fixed value.
    #print(f_carbon_steel)

    #calcualte tonne of Fe source
    m_fe_eaf_upstream = m_crude_steel * fe_crude_steel / n_fe_eaf # tonne of Fe needed from input intot the EAF
    m_dri = m_fe_eaf_upstream * (1 - f_scrap - f_carbon_steel) / fe_dri  # tonne of DRI input in EAF
    m_scrap = m_fe_eaf_upstream * f_scrap /fe_scrap # tonne of scrap + stainless steel
    m_carbon_steel = m_fe_eaf_upstream * f_carbon_steel / fe_carbon_steel #tonne of carbon steel input in EAF.
    fe_source = {'dri':m_dri,'scrap':m_scrap,'carbon steel':m_carbon_steel}

    return fe_source

# a=m_fe_eaf(1,0.26094) #Default values
# print(a)

#calculate the limestone needed in EAF
def m_flux_eaf(m_crude_steel):
    cr_flux = 0.07 # Assume fixed consumption rate of limestone in EAF
    m_flux = m_crude_steel * cr_flux # tonne of limestone input in EAF
    return m_flux
#print(m_flux_eaf(1)) #default value

#Calculat the C needed for reduciton. Assume it linear correlation to crude steel production rate
def m_c_eaf(m_crude_steel, f_ng, c_coal):
    #Assume all carbon content needed for reduction are coming from coal+ng
    #f_ng: fraction of c from ng. default = (56.6*0.77/1000)/0.11=0.043582/0.11=0.3962
    #c_coal: C content in coal. default: 60.38. source 1.
    c_ng = 0.7641 #C content in NG. default: 0.7641. source 1. Assume HHV-ng = 49.5 MJ/kg
    cr_c_eaf = 0.03 # consumption rate of c in EAF. cr_c_eaf = 0.11*12/44/(1*0.99)
    m_coal = m_crude_steel * cr_c_eaf * (1-f_ng) / (c_coal/100) #tonne of coal needed
    m_ng = m_crude_steel * cr_c_eaf * f_ng / c_ng # tonne of ng needed.
    c_source = {'coal': m_coal,'ng':m_ng}
    return c_source
# print(m_c_eaf(1,0.3962,60.38)) #default values

#calculate amount of water needed. assume linear correlation.
def m_water_eaf(m_crude_steel):
    cr_water_eaf = 0.193 # Nm3/tonne of crude steel. source 1.
    m_water_eaf = m_crude_steel * cr_water_eaf
    return m_water_eaf
#print(m_water_eaf(1))

#calculate energy input from electricity. assume the amount of electricity is the difference of all energy needed minus the energy from coal & ng
def q_elec_eaf(m_crude_steel, m_coal, m_ng, hhv_coal):
    cr_e_eaf = 2.291 #Energy consumption rate in EAF MJ/kg = GJ/tonne steel
    q_eaf = m_crude_steel * cr_e_eaf # Energy needed for steel produced
    hhv_ng = 49.5 #Assume hhv_ng = 49.5 MJ/kg= GJ/tonne steel
    q_elec = q_eaf - m_coal * hhv_coal - m_ng * hhv_ng  # Energy input from electricity
    return q_elec
#print(q_elec_eaf(1,0.03,0.015556,28.7)) #defaul value. source 1. hhv_coal = 28.7 MJ/kg
# print(q_elec_eaf(pd.Series([1, 1, 1, 1, 1]),0.03,0.015556,28.7)) #defaul value. source 1. hhv_coal = 28.7 MJ/kg
# The oxygen needed in EAF is a small fraction of oxygen generated in water electrolysis. hence assume no co2 emission associated with it. All CO2 emisison are associated with H2.



