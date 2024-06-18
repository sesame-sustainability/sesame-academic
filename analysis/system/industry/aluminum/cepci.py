"""Get the CEPEI value from .csv file"""

import os
import pandas as pd

dirname = os.path.dirname(__file__)
cepcis = pd.read_csv(os.path.join(dirname, 'cepci.csv') ,usecols=['Years','Chemical Engineering'])
#print(cepcis)

def cepci_v(year):
    ind = cepcis.index[cepcis["Years"] == year].tolist() # get the index
    cepci = cepcis["Chemical Engineering"][ind] # get the cepci value
    return cepci


#a = [cepci_v(i)[i-1980] for i in range(2000,2021,5)] #get the specific year's cepci.
#print(a)
