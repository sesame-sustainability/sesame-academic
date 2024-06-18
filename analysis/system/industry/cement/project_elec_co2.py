"""Projectory. source: 1. https://www.iea.org/data-and-statistics/charts/development-of-co2-emission-intensity-of-electricity-generation-in-selected-countries-2000-2020
2.https://ourworldindata.org/grapher/carbon-intensity-electricity?tab=table&time=2000..latest
3. https://www.iea.org/reports/tracking-power-2020"""

import os
import pandas as pd

dirname = os.path.dirname(__file__)

elec_csv = os.path.join(dirname, 'electricity.csv')
countries = ['China', 'India', 'Korea', 'United States', 'Canada', 'Austria', 'Belgium', 'Bulgaria', 'Croatia','Cyprus',
                 'Czechia', 'Denmark', 'EU-27', 'EU27+1', 'Estonia', 'Finland', 'France', 'Germany', 'Greece','Hungary',
                 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Melta', 'Netherlands', 'Poland', 'Portugal',
                 'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'United Kingdom']
#years = range(2000, 2021, 1)  # data available from 2000 to 2020
elec_countires_year_co2 = pd.read_csv(elec_csv, usecols=['Year'] + countries)  # read and save electricity intensity information
#a=elec_countires_year_co2 #['India'][2020-2000]
#print(elec_countires_year_co2)

def elec_co2(country='India'):
    """country = input("Chose which contry's electricity to be used:"
                    "\n'China', 'India', 'Korea', 'United States', 'Canada', 'Austria', 'Belgium', 'Bulgaria', 'Croatia',"
                    "\n'Cyprus', 'Czechia', 'Denmark', 'EU-27', 'EU27+1', 'Estonia', 'Finland', 'France', 'Germany', 'Greece',"
                    "\n'Hungary', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Melta', 'Netherlands', 'Poland',"
                    "\n'Portugal','Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'United Kingdom':")"""
    if ((country.title() == 'India') or (country.title() == 'China') or (country.title() == 'United States')):
        years = elec_countires_year_co2['Year']
        co2_elec = elec_countires_year_co2[country.title()] #g/kwh
    else:
        years = elec_countires_year_co2['Year'][0:21]
        co2_elec = elec_countires_year_co2[country.title()][0:21] #g/kwh
    elec = {'co2':co2_elec,'years':years,'country':country}
    return elec

#print(elec_co2()['co2'])

"""import matplotlib.pyplot as plt
elec = elec_co2()
year = elec['years']
co2_elec = elec['co2']
plt.plot(year,co2_elec)
plt.title('Electricity carbon content vs year')
plt.xlabel('Year')
plt.ylabel('Electricity carbon content: g CO2/kWh')
plt.show()"""
