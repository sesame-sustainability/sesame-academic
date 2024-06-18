"""H-DRI-EAF system. source: 1. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019).
2. He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants." Energy Reports 3 (2017): 29-36. page 41
3.https://www.tandfonline.com/doi/pdf/10.1179/174328108X301679?needAccess=true
4. https://www.metallics.org/dri.html """

#Material input in H-DRI
# Fe input in DRI
def m_pellet_dri(m_dri): #calculate amount of pellet needed
    fe_dri = 0.861 # assi,e foxed value. source 4.
    fe_pellet = 0.635 # Assume fixed value. source 3.
    n_dri = 0.949134 # Assume fixed conversion rate. n_dri = 0.98*fe_dri/(1.4*fe_pellet) = 0.949134
    m_pellet = m_dri * fe_dri /n_dri / fe_pellet # tonne of pellet needed
    return m_pellet
#print(m_pellet_dri(0.98))


# calculate H2 input in H-DRI. Assume water converted 100% to H2 and O2.
def m_h2_dri(m_dri): #tonne of H2 needed for specific tonne of dri
    cr_h2 = (0.39*10**-3*2/18)/m_dri  # comsunption rate of hydrogen. kg calculated based on water input for electrolyser. source 1.
    m_h2 = m_dri * cr_h2  # m_pellet of H2 needed.
    return m_h2

#print(m_h2_dri(0.98)) # default value







