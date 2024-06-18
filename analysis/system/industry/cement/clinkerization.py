"""
Function unit: 1 tonne of clinker
calcularte clinkerization energy consumption and CO2 emissions.
source 1. Prakasan, Sanoop, Sivakumar Palaniappan, and Ravindra Gettu. "Study of Energy Use and CO 2 Emissions in the Manufacturing of Clinker and Cement."
Journal of The Institution of Engineers (India): Series A 101.1 (2020): 221-232. Table 3.
2. Devaki's ppt: 90% cement industry ppt. page 106
3. Devaki's excel: Specific Heat Consumption for various kiln preheater + precalciner stages. Desk Study on waste heat recovery in the Indian Cement Industry
"""

def kiln(m_clinker=1,preheat_stage = 4,hhv=32,c_fuel=60,elec_co2 = 707.2/3600,f_h2o = 0.08):
    # m_clinker: tonne of clinker. default = 1 tonne
    #limestone_h2o: water content in limestone wt.%. this will affect the amount of fuel used in kilm
    #preheating stages, default 4. fuel input is different with different preheating stages
    #hhv: high heating value MJ/kg=GJ/tonne.
    #c_fuel: carbon content in fuel. wt.%
    # elec_co2: electricity carbon intensity. default = 707.2 g co2/kWh=707.2/3600 tonne/GJ.
    #f_h2o: moisture content in limestone wt%
    # Heat required for raw material drying GJ/tonne
    q_limestone_dry = 0.0827 * f_h2o - 0.0604 #GJ of heat required
    m_dry_fuel = q_limestone_dry/hhv # tonne of fuel needed for limestone drying. assume use the same fuel as clinkerization
    q_limestone_dry_co2 = m_dry_fuel * c_fuel/100 *44/12 # tonne of CO2 emitted due to limestone drying out.
    # get the energy consumption rate for different preheat stages. source 3
    if preheat_stage == 4:
        q_kiln = 3.14 * m_clinker # GJ of energy input needed
    elif preheat_stage == 5:
        q_kiln = 3.01 * m_clinker  # GJ of energy input needed
    elif preheat_stage == 6:
        q_kiln = 2.93 * m_clinker  # GJ of energy input needed
    else:
        raise Exception('not a valid preheat stage')
    q_elec_kiln = (399.22/1000)  * m_clinker # GJ electricity needed for clinkerization, cooling and storing. source 1. (GJ)
    elec_kiln_co2 = q_elec_kiln * elec_co2 # tonne CO2 emission due to electricity used for clinkerization, cooling and storing. (tonne)
    m_fuel = q_kiln / hhv   # tonne of fuel needed in kiln and preheater.
    m_fuel_co2 = m_fuel * c_fuel / 100 * 44 / 12  # tonne of CO2 emitted due to fuel consumpiton in kiln
    m_limestone = m_clinker * 1.165 #tonne of limestone

    #fuel preparation energy supply is electricity, source 1
    q_fuel_prep_elec = (79.72/1000) * m_clinker # GJ electricity needed to prepare fuel
    m_fuel_prep_elec_co2 = q_fuel_prep_elec * elec_co2 # tonne CO2 emisison due to fuel preparation

    #CO2 emission from raw material clinkerization reaction itself.  CaCo3--->CaO + CO2
    m_limestone_co2 = 0.51486 * m_clinker # tonne CO2 emission due to clinkerization reaction. source 1.
    kil = {'m limestone':m_limestone,'fuel kiln':m_fuel+m_dry_fuel,'fuel kiln co2':m_fuel_co2,'elec kiln co2':elec_kiln_co2,
           'q fuel prepare':q_fuel_prep_elec,'m fuel prepare co2':m_fuel_prep_elec_co2,'clinkerization':m_limestone_co2,
           'm drying co2':q_limestone_dry_co2}
    return kil
#a=kiln()
#print(a)
