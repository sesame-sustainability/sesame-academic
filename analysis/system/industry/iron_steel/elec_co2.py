"""
Function unit: 1 tonne of steel
Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
"""

"""================================================================================================================"""

import os
import pandas as pd

dirname = os.path.dirname(__file__)
csv_path = os.path.join(dirname, 'electricity.csv')

countries = [
    'China', 'India', 'Korea', 'United States', 'Canada', 'Austria', 'Belgium', 'Bulgaria', 'Croatia',
    'Cyprus',
    'Czechia', 'Denmark', 'EU-27', 'EU27+1', 'Estonia', 'Finland', 'France', 'Germany', 'Greece',
    'Hungary',
    'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Melta', 'Netherlands', 'Poland', 'Portugal',
    'Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'United Kingdom',
]
#years = range(2000, 2021, 1)  # data available from 2000 to 2020
#read electricity related information (carbon intensity kg CO2/kWh) from csv file.
elec_countires_year_co2 = pd.read_csv(csv_path, usecols=['Year'] + countries)  # read and save electricity intensity information
#a=elec_countires_year_co2['India'][2020-2000]

def elec_co2(country='India'):
    """country = input("Chose which contry's electricity to be used:"
                    "\n'China', 'India', 'Korea', 'United States', 'Canada', 'Austria', 'Belgium', 'Bulgaria', 'Croatia',"
                 "\n'Cyprus', 'Czechia', 'Denmark', 'EU-27', 'EU27+1', 'Estonia', 'Finland', 'France', 'Germany', 'Greece',"
                 "\n'Hungary', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Melta', 'Netherlands', 'Poland',"
                "\n'Portugal','Romania', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'United Kingdom':")"""
    if ((country.title()=='India') or (country.title()=='China') or (country.title()=='US')):
        year = float(input("\nWhich year, chose between 2000 to 2020:"
                           "\nOr chose from the following prediction senarios:"
                           "\n1. IEA Sustianable Development Senario 2025"
                           "\n2. IEA Sustianable Development Senario 2030"
                           "\n3. IEA Sustianable Development Senario 2035"
                           "\n4. IEA Sustianable Development Senario 2040: "))
        if ((year ==1) or (year==2025)):
            co2_elec = elec_countires_year_co2[country.title()][21]
        elif ((year ==2) or (year==2030)):
            co2_elec = elec_countires_year_co2[country.title()][22]
        elif ((year ==3) or (year==2035)):
            co2_elec = elec_countires_year_co2[country.title()][23]
        elif ((year ==4) or (year==2040)):
            co2_elec = elec_countires_year_co2[country.title()][24]
        else:
            co2_elec = elec_countires_year_co2[country.title()][year - 2000]  # index for the specific country and year. GJ/t
    else:
        year = float(input("\nWhich year, chose between 2000 to 2020:"))
        co2_elec = elec_countires_year_co2[country.title()][year-2000]  #index for the specific country and year. GJ/t
    return co2_elec

# a=elec_co2()
# print(a)