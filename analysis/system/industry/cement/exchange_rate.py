"""get the data for exchange rate from csv file.
source OECD: https://data.oecd.org/conversion/exchange-rates.htm#indicator-chart"""

import os
import pandas as pd

dirname = os.path.dirname(__file__)
exchange_rates = pd.read_csv(os.path.join(dirname, 'exchange_rates.csv'), usecols=['Year','United_States',"India",'China','EU_27'])

def exchange_country(country):
    if country =='United_States':
        ex_rate = exchange_rates['United_States']
    elif country == 'India':
        ex_rate = exchange_rates['India']
    elif country == 'China':
        ex_rate = exchange_rates['China']
    else: # country.title() == 'EU_27':
        ex_rate = exchange_rates['EU_27']
    return ex_rate

# print(exchange_country('Euro Zone'))
