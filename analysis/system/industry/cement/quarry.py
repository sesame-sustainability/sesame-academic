"""
Function unit: 1 tonne of limestone
This file is used to simulate the quarry process. It'll consider Energy input, carbon flow, material balance
source 1. Prakasan, Sanoop, Sivakumar Palaniappan, and Ravindra Gettu. "Study of Energy Use and CO 2 Emissions in the Manufacturing of Clinker and Cement."
Journal of The Institution of Engineers (India): Series A 101.1 (2020): 221-232. Table 3.
2.Marceau, Medgar, Michael A. Nisbet, and Martha G. Van Geem. Life cycle inventory of portland cement manufacture. No. PCA R&D Serial No. 2095b. Skokie, IL: Portland Cement Association, 2006.
3. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019). page 66.
"""

#quarry process
def quarry(m_limestone = 1,qua_distance = 0.05, elec_co2 = 707.2/3600,transport='diesel'):
    #m_limestone: tonne of limestone for 1 tonne of clinker. default = 1.165 tonne limestone. source 2
    #distance: limestone transportation distance. default = 1 km
    #transport: assume limestone transport default energy is diesel. alternative is electricity.
    #elec_co2: electricity carbon intensity. default = 707.2 g co2/kWh = 707.2/3600 tonne/GJ.
    q_elec_extract = (9.89/1000)/1.165 * m_limestone  # GJ of electricity needed for quarry. source 1.
    elec_extract_co2 = q_elec_extract * elec_co2  # tonne CO2 emitted due to limestone extraction using electricity
    m_diesel_extract = (73.51/42.68)/1000/1.165 * m_limestone # tonne of diesel needed for quarry. hhv_diesel = 42.68 MJ/kg
    c_co2 = 0.863  # carbon content of diesel. default = 86 wt%. source: https://www.iea-amf.org/content/fuel_information/diesel_gasoline
    diesel_extract_co2 = m_diesel_extract * c_co2 * 44 / 12 # tonne CO2 emission due to diesel used for extraction
    if transport == 'Diesel':
        m_transport = (30.6 / 42.68)/1000/1.165 * m_limestone * qua_distance # tonne of diesel needed for limestone transportation. 
        m_transport_co2 = m_transport * c_co2 * 44/12 # tonne of CO2 emitted due to limestone transportation
    elif transport == 'Electricity':
        m_transport = (30.6 / 1000)/1.165 * m_limestone * qua_distance  # GJ electricity needed is calculated according to 30.6 MJ/tonne of climestone/km.
        # diesel net calorific value =41.5 MJ/kg. assume 100% efficiency for diesel driving the truck. hence elec = 41.5 MJ/kg diesel * 2.29 kg diesel/(3.6 MJ/kWh)/ton clinker = 0.0264 kWh
        c_co2 = elec_co2 #  this could be a dynamic value input. (tonne/GJ)
        m_transport_co2 = m_transport * c_co2  # tonne of CO2 emitted due to limestone transportation
    elif transport == 'Natural Gas':
        m_transport = (30.6 / 49.5)/1000/1.165 * m_limestone * qua_distance # tonne NG needed is calculated according to 30.6 MJ/tonne of climestone/km. (tonne)
        #NG_hhv = 49.5 MJ/kg. NG carbon intensity: 56.6 kgco2/GJ. source 3. 
        c_co2 = 49.5*56.6/1000 # NG carbon intensity (tonne CO2/tonne NG)
        m_transport_co2 = m_transport * c_co2 # tonne CO2 emitted due to limestone transportation
    else: # transport =='Hydrogen'
        m_transport = (30.6 / 118.6)/1000/1.165 * m_limestone * qua_distance # tonne h2 needed is calculated according to 30.6 MJ/tonne of climestone/km.
        # H2_HHV = 118.6 MJ/kg H2. ref. https://www.nrel.gov/docs/fy10osti/47302.pdf
        c_co2 = 0 #assume renewable hydrogen. (tonne CO2/tonne H2)
        m_transport_co2 = m_transport * c_co2 # tonne CO2 emitted due to limestone transportation
    qua = {'q elec extract':q_elec_extract,'m diesel extract': m_diesel_extract,'transport':m_transport,
           'elec extract co2':elec_extract_co2,'diesel extract co2':diesel_extract_co2,'transport co2': m_transport_co2} #'transport' either gives tonne of fuel, or GJ of electricity.
    return qua

#a = quarry(1,1000,0.2,'Electricity')
#print(f"quary transport emission: {a}")

#limestone crushing, stacking and reclaiming, raw meal preparation
def crushing(m_limestone = 1.165, elec_co2 = 707.2/3600):
    #m_limestone: tonne of limestone for 1 tonne of clinker. default = 1.165 tonne limestone. source 2
    # elec_co2: electricity carbon intensity. default = 707.2 g co2/kWh=707.2/3600 tonne CO2/GJ.
    q_elec_crushing = (13.63+310.28)/1000/1.165 * m_limestone # GJ of electricity needed 
    elec_crushing_co2 = q_elec_crushing * elec_co2   # tonne CO2 emitted due to limestone extraction using electricity
    cru = {'q elec crushing': q_elec_crushing,'elec crushing co2':elec_crushing_co2}
    return cru



#b=crushing()
#print(b)