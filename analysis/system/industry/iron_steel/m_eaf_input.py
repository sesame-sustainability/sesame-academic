"""
Function unit: 1 tonne of steel
DRI-EAF. source: 1. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019). page 39
2.Unal Camdali and Murat Tunc. Modelling of electric energy consumption in the AC electric arc furnace. 2002.
"""

#Material flow in EAF. All assume linear correlation to produciton of steel. source 1.
def m_eaf_input(m_steel, f_scrap, f_ng, c_coal):
    #m_steel: tonne steel to be produced.
    #f_scrap: Fe input from scrap. default: f_scrap = 1.42*0.99/(1.42*0.99+0.02553*0.997)=0.982216. source 1.
    c_ng = 0.7641 # default carbon content in NG, source 1.
    #f_ng: C input from NG. default: 0.77/49.5*0.7641/(0.77/49.5*0.7641+0.03*0.6038)=0.3962
    n_steel_upstream = 0.698409 # n_steel_upstream = 1*0.9996/(1.42*0.99+0.02553*0.997). Assume scrap steel and stainless steel are the same because their Fe content are the same 99%. source 1.
    fe_steel = 0.9996 # default. source 1
    m_steel_upstream = m_steel*fe_steel/n_steel_upstream #Amoun of Fe needed from scrap+pig iron
    # print(m_steel_upstream/m_steel)
    fe_scrap = 0.99 #Default scrap Fe content. source 2.
    fe_carbon_steel = 0.997  #Default scrap Fe content. source 2.
    cr_fluxes = 0.07   # consumpiton rate of limestone in EAF. source 1.
    cr_o2 = 0.035 # consumption rate of oxygen in EAF Nm3 O2/tonne steel
    cr_water = 0.193 # water consumption rate in EAF Nm3 water/tonne steel
    cr_c = 0.030012 # carbon consumption rate = (0.77/49.5*0.7641+0.03*0.6038)/(1*0.9996) tonne/tonne steel

    # mass input
    m_eaf_scrap = m_steel_upstream * f_scrap/fe_scrap  # tonne of scrap+stainless steel input in EAF
    #Beginning to consider other plants
    # m_eaf_carbon_steel = m_steel*0.025 #25.53 ktons per Mton of steel
    # fe_dri = 0.835
    # m_eaf_dri = m_steel_upstream*(1-f_scrap)/fe_dri
    # print(m_eaf_dri)
    m_eaf_carbon_steel = m_steel_upstream * (1-f_scrap)/fe_carbon_steel  # tonne of carbon steel input in EAF
    m_eaf_fluxes = m_steel * cr_fluxes  # tonne of limestone input in EAF
    m_eaf_ng = m_steel * fe_steel * cr_c * f_ng / c_ng  # tonne of NG input in EAF
    m_eaf_coal = m_steel * fe_steel * cr_c * (1-f_ng) / (c_coal/100)  # tonne of coal input in EAF
    m_eaf_water = m_steel * cr_water  # Nm3 of water input in EAF
    v_eaf_o2 = m_steel * cr_o2 #Nm3 of oxygen input in EAF


    # Associated CO2 emissions
    m_co2_coal = m_eaf_coal * c_coal/100 *44/12 # tonne CO2. co2 emission from coal consumption.
    m_co2_ng = m_eaf_ng * c_ng * 44/12 # tonne CO2. co2 emission from ng consumption.

    inputs = {"scrap": m_eaf_scrap, "carbon steel":m_eaf_carbon_steel,"fluxes":m_eaf_fluxes,"coal":m_eaf_coal,"ng":m_eaf_ng,"o2":v_eaf_o2,'water':m_eaf_water,
              'co2_coal':m_co2_coal,'co2_ng': m_co2_ng}
    return inputs

# a=m_eaf_input(1,0.6,0.3962, 60.38)
# print(a)