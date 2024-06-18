"""Get data from EPPA prediction in year 2021 by Sergey Paltsev paltsev@mit.edu"""

import os
import pandas as pd

dirname = os.path.dirname(__file__)
eppa_csv = os.path.join(dirname, 'eppa.csv')

def eppa_senarios(senario='Reference'):
    ccs_percent = pd.read_csv(eppa_csv, usecols=['Year']+[f'{senario}'])[0:7] #read and save CCS percentage
    coal_use = pd.read_csv(eppa_csv, usecols=['Year']+[f'{senario}'])[8:15] #read and save coal use
    electricity_use = pd.read_csv(eppa_csv, usecols=['Year']+[f'{senario}'])[16:23] #read and save eledtricity use
    ng_use = pd.read_csv(eppa_csv, usecols=['Year']+[f'{senario}'])[24:31] #read and save ng use
    oil_use = pd.read_csv(eppa_csv, usecols=['Year']+[f'{senario}'])[32:39] #read and save oil + biofuel use
    coal_price = pd.read_csv(eppa_csv, usecols=['Year']+[f'{senario}'])[40:47] #read and save electricity price. base index, assume price in 2020 is 1.
    ng_price = pd.read_csv(eppa_csv, usecols=['Year']+[f'{senario}'])[48:55] #read and save ng price. base index, assume price in 2020 is 1.
    oil_price = pd.read_csv(eppa_csv, usecols=['Year']+[f'{senario}'])[56:63] #read and save oil price. base index, assume price in 2020 is 1.
    electricity_price = pd.read_csv(eppa_csv, usecols=['Year']+[f'{senario}'])[64:71] #read and save electricity price. base index, assume price in 2020 is 1.
    carbon_price = pd.read_csv(eppa_csv, usecols=['Year']+[f'{senario}'])[72:79] #read and save electricity price. base index, assume price in 2020 is 1.
    co2_emission = pd.read_csv(eppa_csv, usecols=['Year']+[f'{senario}'])[80:91] #read and save total co2 emissions.
    eppa_data = {'ccs%':ccs_percent,'coal use': coal_use,'elec use': electricity_use,'ng use': ng_use,
                 'oil use': oil_use,'coal price':coal_price,'ng price': ng_price,'oil price': oil_price,
                 'elec price': electricity_price,'carbon price': carbon_price, 'co2': co2_emission}
    return eppa_data

"""s = 'CCS and Low Carbon Price'
a= eppa_senarios()['co2']['Reference'][0:5]
b =  eppa_senarios()['co2']['Reference'][0:9]
print(b)"""
