"""Calculate the amount of CO2 emitted from iron and steel for India.
Based on world's total steel demand, today's co2 emission intensity for steel industry,
total co2 emission reduction according to IEA's sds scenario, and india's predicted steel production"""

import os
import pandas as pd

dirname = os.path.dirname(__file__)

wsd_path = os.path.join(dirname, 'worldsteel_demand_predict.csv')
wsd = pd.read_csv(wsd_path, usecols=['Year', 'Demand(tonne)'])  # get the world steel demand. (2020,2040,5)  tonnes.

iscr_path = os.path.join(dirname, 'co2_emission_predictions.csv')  # get the location of IEA SDS scenario co2 emission reduction data. (2019,2050,1)
iscr = pd.read_csv(iscr_path, usecols=['Year', 'SDS'])  # get the IEA SDS scenario co2 emission reduction data. (2019,2050,1) tonnes co2/year

def co2_ub(m_steel):
    # print(wsd)
    # print(iscr)
    i_co2_steel = 1.83  # Today's co2 emission intensity for steel production. tonne co2/tonne of steel. ref. https://www.worldsteel.org/about-steel/steel-facts.html
    f_india_steel = m_steel / wsd['Demand(tonne)']  # fraction of steel demand from India. tonne steel in India/tonne steel worldwide
    # print(f_india_steel)
    world_co2 = wsd['Demand(tonne)'] * i_co2_steel  # tonnes of co2 emitted based on today's co2 emission intensity (2020,2040,5)
    ub_co2_emission = iscr['SDS']  # world_co2 -  # upper bound of allowed co2 emission from worldwide steel production. tonnes of co2/year.
    india_avg = 2.5  #https://steel.gov.in/energy-environment-management-steel-sector
    up_co2_emission_india = ub_co2_emission * f_india_steel*india_avg/i_co2_steel#[india_avg/i_co2_steel, i_co2_steel,i_co2_steel,i_co2_steel,i_co2_steel]  # upper bound of allowed co2 emission from India's steel production. tonnes of co2/year.
    return up_co2_emission_india

# k = [100981478.60000001, 120950027.6, 158105467.7, 199336209.6, 247544410.2]
# a = co2_ub(k)
# print(a)
