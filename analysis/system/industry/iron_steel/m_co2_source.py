"""H-DRI-EAF system. source: 1. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019).
2. He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants." Energy Reports 3 (2017): 29-36. page 41
3. https://www.tandfonline.com/doi/pdf/10.1179/174328108X301679?needAccess=true
4. https://www.metallics.org/dri.html """

#CO2 emission associated with energy source/carbon source
def m_co2_source(m_carbon_source, c): #calculate CO2 emission associated with its source
    #m_carbon_source: kg of carbon/energy source kg
    #c: carbon content in carbon/energy source %
    m_co2 = m_carbon_source * c/100 *44/12 #carbon weight converted to co2 weight. kg CO2/kg carbon/energy source
    return m_co2
#print(m_co2_source(0.03,0.6038)) #default value of coal in eaf. source 1














