"""
function unit: 1 tonne of CO2.
This file includes capex, opex, utility usage of various ccs methods
source: 1. Manzolini, Giampaolo, et al. "Economic assessment of novel amine based CO2 capture technologies integrated in
power plants based on European Benchmarking Task Force methodology." Applied Energy 138 (2015): 546-558.
2. Romeo, Luis M., Irene Bolea, and Jesús M. Escosa. "Integration of power plant and amine scrubbing to reduce CO2
capture costs." Applied Thermal Engineering 28.8-9 (2008): 1039-1046.
3. Seider, Warren D., et al. "Product and process design principles: synthesis." Analysis and Evaluation 4 (2004).
4. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019). page 66.
"""

#MEA solvent for Carbon capture
#m_co2:  tonne of CO2 to be captured
#volume percentage of CO2 in flue gas. f=1 give a default value. Assume this only affect opex.
#cap_r: capture rate.cap=89.7 give default capture rate of 89.7% = (1-36.15/351.67)*100%. Assume this only affect opex
#reg_u: regeneration utility, suppose NG is the default utility.
#m_co2: referenced capacity = 7500h * 351.67kgco2/MWh * 833.6 MW = 2198641 tonne CO2/year. plant operation time 7500 h/year, which gives time for maintinance. source 1.
#c_u: utility price. 68.99 euro/kwh. source 1.
import numpy as np
from analysis.system.industry.cement.project_elec_co2 import elec_co2 as ec #get the carbon intensity of elecity
def ccs(m_co2,method='MEA',cap_r=89.7,reg_u='NG',country='India',c_u = 69.88/3.6):
    #MEA CAPEX related. source 1&3
    capacity1_mea = 2198641  # referenced amount of co2 emitted. source 1.tonne co2
    capacity2_mea = capacity1_mea    # Assume the MEA plant is the same size as the reference one. 
    tpc1_mea = 163180000 # euro. total plant cost. year 2008.
    n_ccs_mea = m_co2/capacity2_mea # number of ccs plant needed in India
    sf_mea = 1 # 0the MEA plant mainly contains colomuns, which according to Sider's book (source 3, page 591), the shape factor is usually 1.
    tpc2_mea = n_ccs_mea * tpc1_mea * (capacity2_mea/capacity1_mea)**sf_mea #tpc of the plant size interested. need further adjustment in each routes, regarding cepci and ppp

    # CESAR-1 CAPEX related. source 1
    capacity1_cesar = 2198641 # referenced amount of co2 emitted. source 1. tonne co2
    capacity2_cesar = capacity1_cesar #total amount of co2 emitted and used for capture
    tpc1_cesar = 146000000 # euro. total plant cost. year 2008
    sf_cesar = 1 # the CESAR plant mainly contains colomuns, which according to Sider's book (source 3, page 591), the shape factor is usually 1.
    n_ccs_cessar = m_co2/capacity2_cesar
    tpc2_cesar = n_ccs_cessar * tpc1_cesar * (capacity2_cesar/capacity1_cesar)**sf_cesar #tpc of the plant size interested. need further adjustment in each routes, regarding cepci and ppp

    #MEA OPEX related. source 1. assume linear correlation with carbon capture rate
    elec_mea = 1.47365/89.7 * m_co2 *  cap_r * 3.6 #MWh/ tonne CO2 *  tonne of CO2. MWh (=3.6 GJ) of electricity consumed. (829.9-709.9)*7500/(351.67*833.6/1000*7500)*3.6 (GJ)
    c_mea_raw_material = 6200000/(351.67*833.6/1000*7500)/89.7 *  m_co2 *  cap_r # cost for raw material (euro)
    c_mea_tom = 13900000/(351.67*833.6/1000*7500)/89.7 *  m_co2 *  cap_r # total fixed cost for operation and maintenance (euro)

    #m_mea_makeup = 1.5/1000/89.7 * m_co2 *  cap_r  # Amount of CO2 to be captured in this source 1. = 1.5 KG/Tonne co2. (tonne)
    #m_h2o_makeup = 135.4/89.7 * m_co2 *  cap_r   # m ake up rate = (1188628/0.191*1000)kg water/(473956.637*0.097tonneCO2)= 135.4 tonne water/tonne CO2. source 2.

    # CESAR OPEX related. source 1. assume linear correlation with carbon capture rate
    elec_cesar = 1.31768/89.7 * m_co2 *  cap_r * 3.6  #MWh/ tonne CO2 *  tonne of CO2. MWh of electricity consumed. (829.9-722.6)*7500/(351.67*833.6/1000*7500)*3.6 (GJ)
    c_cesar_raw_material = 2950000/(351.67*833.6/1000*7500)/89.7 *  m_co2 *  cap_r # cost for raw material (euro)
    c_cesar_tom = 25430000/(351.67*833.6/1000*7500)/89.7 *  m_co2 *  cap_r # total fixed cost for operation and maintenance (euro)
    #q_reg_u_cesar = 0.8083/89.7 * m_co2 *  cap_r # MWh/ tonne CO2 *  tonne of CO2. MWh of heat utility used for cesar 2.91/3.6 MWH/tonne co2
    #m_amp_makeup = 0.00123/89.7 * m_co2 *  cap_r #  tone of cesar needed. Amount of CO2 to be captured in this source (cesar:the cost ratio of AMP over piperzine =1.3,AMP price: 8, PZ price 6. which means cesar is maid 50:50 of AMP and PZ)
    #m_piprazine_makeup = 0.00123/89.7 * m_co2 *  cap_r  #make up rate. the same as amp

    if method =='MEA':
        if reg_u == 'NG':
            c_u = 117/3.6/1.3 #electricity price. euro/GJ
            c_utility = 6350000/(120*7500)/(351.67/1000)/89.7 *  m_co2 *  cap_r/(69.88/3.6)*c_u # utility cost. (euro)
            reg_u_co2 = 120*7500*3.6* 56.6/1000/(351.67*833.6/1000*7500)/89.7 *  m_co2 *  cap_r  # NG carbon intensity: 56.6 kgco2/GJ. source 4. (tonne)
        elif reg_u =='Electricity':
            c_u = 5.27/1.3 #euro/GJ
            c_utility = 6350000/(120*7500)/(351.67/1000)/89.7 *  m_co2 *  cap_r/(69.88/3.6)*c_u # utility cost. (euro)
            reg_u_co2 = np.array(ec(country)['co2'][4:9])/3600 * 120*7500*3.6/(351.67*833.6/1000*7500)/89.7 *  m_co2 *  cap_r # tonne CO2 emitted
        cost ={"tpc":tpc2_mea,"elec":elec_mea, "operation_management":c_mea_tom,"raw material": c_mea_raw_material, "utility": c_utility,"CO2":reg_u_co2}
        return cost
    elif method =='CESAR':
        if reg_u == 'NG':
            c_u = 117/3.6/1.3 #electricity price. euro/GJ
            c_utility = 2950000/(107.3*7500)/(351.67/1000)/89.7 *  m_co2 *  cap_r/(69.88/3.6)*c_u # utility cost. (euro)
            reg_u_co2 = 107.3*7500*3.6* 56.6/1000/(351.67*833.6/1000*7500)/89.7 *  m_co2 *  cap_r  # (tonne) CO2
        elif reg_u =='Electricity':
            c_u = 5.27/1.3 #euro/GJ
            c_utility = 2950000/(120*7500)/(351.67/1000)/89.7 *  m_co2 *  cap_r/(69.88/3.6)*c_u # utility cost. (euro)
            reg_u_co2 = np.array(ec(country)['co2'][4:9])/3600 * 107.3*7500*3.6/(351.67*833.6/1000*7500)/89.7 *  m_co2 *  cap_r # tonne CO2 emitted
        cost = {"tpc": tpc2_cesar, "elec": elec_cesar, "operation_management":c_cesar_tom,"raw material": c_cesar_raw_material, "utility": c_utility,"CO2": reg_u_co2}
        return cost

#m_co2 = [0.1,2]
#ccsi = ccs(0.1,"mea",0.097,65,'ng','India')
#print(ccsi)