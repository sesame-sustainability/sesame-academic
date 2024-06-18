"""operation cost according to cement plant with/witout MEA-based CO2 capture.
source: 1. Roussanaly, Simon, et al. "Techno-economic analysis of MEA CO2 capture from a cement kiln–impact of steam supply scenario." Energy Procedia 114 (2017): 6229-6239.
"""

import pandas as pd
"""file = 'C:\Work\Cement\cement_codes/material_cost.csv'
material_cost = pd.read_csv(file,usecols=['material','price'])
print(material_cost['price'][0])"""

from exchange_rate import exchange_country as ec
def input_cost(m_material, price, lcu_ex, ref_ex):
    c_material = m_material * price *lcu_ex / ref_ex #material cost = amount of material*price of material * local current unit exchange rate/reference price exchange rate
    return c_material
"""def opex():
    #m_limestone,m_fuel,q_elec,m_ng=0,m_steam=0,m_cwater=0: mass flow of limestone. tonne;fuel GJ; electricity MWh; natural gas GJ;steam MWh; coling water m3
    c_limestone = input_cost(m_limestone, material_cost['price'][0], ec['India'],ec['Euro Zone']) #India ruppee spend for limestone
    c_fuel = m_limestone * material_cost['price'][0] * ec['India']/ec['Euro Zone'] #India ruppee spend for limestone"""
