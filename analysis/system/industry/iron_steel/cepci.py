"""Get the CEPEI value from .csv file"""

import os
import pandas as pd

dirname = os.path.dirname(__file__)
csv_path = os.path.join(dirname, 'cepci.csv')

cepcis = pd.read_csv(csv_path, usecols=['Years','Chemical Engineering'])

def cepci_v(year):
    ind = cepcis.index[cepcis["Years"] == year].tolist() # get the index
    cepci_series = cepcis["Chemical Engineering"][ind] # get the cepci value
    cepci = cepci_series.to_numpy()
    return cepci

# print(f'cepci: {cepci_v(2017)[0]}')
