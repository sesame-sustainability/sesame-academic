"""Purchasing power parity. source:https://data.oecd.org/conversion/purchasing-power-parities-ppp.htm#indicator-chart"""

import os
import pandas as pd

dirname = os.path.dirname(__file__)
ppps = pd.read_csv(os.path.join(dirname, 'ppp.csv'), usecols=['TIME','United_States',"India",'China','Canada','EU-27','Australia'])

def pppv(country='India',year=2020):
    if country =='United_States': #upper and lower case of characters matter
        ppp =ppps['United_States'][year-1995] #get the specific year for the country's ppp
        return ppp
    elif country == 'India':
        ppp = ppps['India'][year-1995]
        return ppp
    elif country == 'China':
        ppp = ppps['China'][year-1995]
        return ppp
    else:# country.upper() == 'EU_27':
        ppp = ppps['EU-27'][year-1995]
        return ppp


#a =pppv('EU27',2018)
#print(a)
