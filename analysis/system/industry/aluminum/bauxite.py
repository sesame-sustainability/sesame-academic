"""
Functional unit: 1 tonne of bauxite
source: 1. European Aluminum Industry: https://european-aluminium.eu/media/3321/full-environmental-profile-report-2018.pdf
2. IEA electricity carbon intensity: https://www.iea.org/reports/tracking-power-2020
@author: Lingyan Deng
"""

#import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

dirname = os.path.dirname(__file__)
csv_path = os.path.join(dirname, 'bayer_hall_heroult.csv')

countries = ['Global','EU-27']
"""countries = [
    'India','China','Global','EU-27','Gulf Cooperation Council region','Indonesia',
]"""
material_flow = pd.read_csv(csv_path, usecols=['Processes'] + countries)  # read and save material flow information


def bauxite(m_bauxite =1,f_heavy_oil_bauxite = 0.212,c_electricity = 0.063, country='EU-27',
            c_heavy_oil=0.0851,c_diesel_oil=0.0826,hhv_heavy_oil=43.05,hhv_diesel_oil=42.9):
    #m_bauxite: tonne of bauxite to be produced.
    #c_heavy_oil,c_diesel_oil: emisison factors kg co2/MJ
    q_thermal_bauxite = float(material_flow[country][7]) * m_bauxite #material_flow[country][7] #MJ
    q_heavy_oil_bauxite = f_heavy_oil_bauxite * q_thermal_bauxite      #MJ
    q_diesel_oil_bauxite= q_thermal_bauxite * (1 - f_heavy_oil_bauxite)   # MJ
    electricity_bauxite = float(material_flow[country][8]) * 0.0036 * m_bauxite #GJ electricity used in bauxite

    #print(q_thermal_bauxite)
    #f_heavy_oil_bauxite: fraction of thermal energy provided by heaby oil. The other part is provided by diesel oil.

    m_heavy_oil_bauxite = q_heavy_oil_bauxite/hhv_heavy_oil/1000 # tonne of heavy oil
    m_diesel_oil_bauxite = q_diesel_oil_bauxite/hhv_diesel_oil/1000 # tonne of diesel oil

    co2_heavy_oil_bauxite = c_heavy_oil * q_heavy_oil_bauxite/1000  # tonne co2 emission due to heavy oil used in bauxite
    co2_diesel_oil_bauxite = c_diesel_oil * q_diesel_oil_bauxite/1000  # tonne co2 emission due to diesel oil used in bauxite
    co2_electricity_bauxite = np.array(c_electricity) * electricity_bauxite # tonne co2 emission due to electricity used in bauxite
    #print(q_heavy_oil_bauxite,q_diesel_oil_bauxite,q_thermal_bauxite,electricity_bauxite)
    return {
         'heavy oil': m_heavy_oil_bauxite,
        'diesel oil': m_diesel_oil_bauxite,
        'electricity': electricity_bauxite,
        'co2 heavy oil': co2_heavy_oil_bauxite,
        'co2 diesel oil': co2_diesel_oil_bauxite,
        'co2 electricity': co2_electricity_bauxite,
    }
"""a = bauxite(1,0.212,0.063, 'EU-27',0.0851,0.0826,43.05,42.9)
print(f"a:{a}")
b = bauxite(1,0.25,0.063, 'EU-27',0.0851,0.0826,43.05,42.9)
print(f"a:{b}")"""

