"""Typical BF-BOF route. Data based on a Chinese plant.
Source: 1.He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
2. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019).
The functional unit is 1 ton of steel"""

"""================================================================================================================"""

import os
import pandas as pd

dirname = os.path.dirname(__file__)
fuel_csv = os.path.join(dirname, 'fuels.csv')
coal_l = pd.read_csv(fuel_csv, usecols=['Fuel type', 'M_C(%)', 'M_HHV(MJ/kg)'])
options = list(coal_l['Fuel type'])

def fuel_type(i):
    #read fuel related information (type, C%, HHV, etc.) from csv file.

    c_coal = coal_l['M_C(%)'][i] # carbon content
    hhv_coal = coal_l['M_HHV(MJ/kg)'][i] # hhv of coal
    fuel_characte = {"c":c_coal,'hhv':hhv_coal}
    return fuel_characte
