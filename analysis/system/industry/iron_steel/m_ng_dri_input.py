"""Based on m_hdri_input
1. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019).
2. He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants." Energy Reports 3 (2017): 29-36. page 41
3.https://www.tandfonline.com/doi/pdf/10.1179/174328108X301679?needAccess=true
4. https://www.metallics.org/dri.html
5. (3)“Modeling MIDREX Based Process Configurations for Energy and Emission Analysis - Sarkar - 2018 - steel research international - Wiley Online Library.” https://onlinelibrary.wiley.com/doi/full/10.1002/srin.201700248 (accessed Mar. 14, 2022).
"""
#Material input in ULCORED
# Fe input in DRI
def m_pellet_dri(m_dri,ng_furn): #calculate amount of pellet needed

    if ng_furn == 'ULCOS':
        fe_dri = 0.861 # assume fixed value. source 4.
        fe_pellet = 0.635 # Assume fixed value. source 3.
        mpdri = 1.13/0.98 #source 1 - amt of pellets per dri
        n_dri = m_dri*fe_dri/(mpdri*fe_pellet) # Assume fixed conversion rate. n_dri = 0.98*fe_dri/(1.4*fe_pellet) = 0.949134
        m_pellet = m_dri * fe_dri /n_dri / fe_pellet # tonne of pellet needed
    else:
        fe_dri = 0.90 # source 5
        fe_pellet = ((55.845*2)/159.69)*1285/1367.27 # source 5 -- > mass of iron in iron oxide multiplied by mass of iron oxide in simulation divided by total pellet mass.
        n_dri = 1 # assume all iron ends up in DRI #portion of iron that ends up in dri ( source 5) (rest become FeO)
        m_pellet = m_dri * fe_dri / n_dri / fe_pellet #tonnes

    return m_pellet



# calculate natural gas input in GJ.
def m_ng_dri(m_dri,ng_furn):
    if ng_furn == 'ULCOS':
        cr_ng = 7.79/0.98  # source 1 - comsumption rate of natural gas in GJ/tonne
    else: #MIDREX
        cr_ng =  2.14*4.184 # convert net Gcal to GJ per tonne of DRI
    ng_en = cr_ng*m_dri
    return ng_en

# print(m_ng_dri(0.98)) # default value







