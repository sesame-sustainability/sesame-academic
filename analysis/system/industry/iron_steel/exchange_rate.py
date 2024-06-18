"""get the data for exchange rate from csv file.
source OECD: https://data.oecd.org/conversion/exchange-rates.htm#indicator-chart"""

import os
import pandas as pd

dirname = os.path.dirname(__file__)
csv_path = os.path.join(dirname, 'exchange_rates.csv')

exchange_rates = pd.read_csv(csv_path, usecols=['Year','United_States',"India",'China','EU_27'])

def exchange_country(country):
    if country.title() =='United_States':
        ex_rate =exchange_rates['United_States']
    elif country.title() == 'India':
        ex_rate = exchange_rates['India']
    elif country.title() == 'China':
        ex_rate = exchange_rates['China']
    else: # country.title() == 'EU_27':
        ex_rate = exchange_rates['EU_27']
    return ex_rate
