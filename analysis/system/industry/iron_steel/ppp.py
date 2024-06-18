"""Purchasing power parity. source:https://data.oecd.org/conversion/purchasing-power-parities-ppp.htm#indicator-chart"""

import os
import pandas as pd

dirname = os.path.dirname(__file__)
csv_path = os.path.join(dirname, 'ppp.csv')

ppps = pd.read_csv(csv_path, usecols=['TIME','United_States',"India",'China','Canada','EU_27','Australia'])

def pppv(country,year):
    ppp =ppps[country][year-1995] #get the specific year for the country's ppp
    return ppp

# a =pppv('United States',2020)
# print(a)
