"""Projectory. source: 1. https://www.iea.org/data-and-statistics/charts/development-of-co2-emission-intensity-of-electricity-generation-in-selected-countries-2000-2020
2.https://ourworldindata.org/grapher/carbon-intensity-electricity?tab=table&time=2000..latest
3. https://www.iea.org/reports/tracking-power-2020"""

import os
import pandas as pd

dirname = os.path.dirname(__file__)
csv_path = os.path.join(dirname, 'electricity.csv')

countries = [

    'China', 'India', 'Korea', 'United States', 'Canada', 'Global','Austria', 'Belgium', 'Bulgaria', 'Croatia','Cyprus',
    'Czechia', 'Denmark', 'EU-27', 'EU27+1', 'Estonia', 'Finland', 'France', 'Germany', 'Greece','Hungary',
    'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Melta', 'Netherlands', 'Poland', 'Portugal',
    'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'United Kingdom','Global'
]

#years = range(2000, 2021, 1)  # data available from 2000 to 2020
elec_countries_year_co2 = pd.read_csv(csv_path, usecols=['Year'] + countries)
#print(elec_countires_year_co2)

def elec_co2(country='India'):
    years = elec_countries_year_co2['Year']
    co2_elec = elec_countries_year_co2[country]  #tonne CO2/GJ
    elec = {'co2':co2_elec,'years':years,'country':country}
    return elec

#print(elec_co2('India')['co2'][20:25])
