"""Typical BF-BOF route. Data based on a Chinese plant.
Source: 1.He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
2. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019).
The functional unit is 1 ton of steel
3.https://shaktifoundation.in/wp-content/uploads/2017/06/A_Study_of_Energy_Efficiency_in_the_Indian_IS.pd
4. Nishant R. Dey, Anil K. Prasad, Shravan K. Singh,Energy survey of the coal based sponge iron industry,
Case Studies in Thermal Engineering,Volume 6,2015,Pages 1-15,ISSN 2214-157X,https://doi.org/10.1016/j.csite.2015.04.001.
(https://www.sciencedirect.com/science/article/pii/S2214157X15000167)"""

"""================================================================================================================"""


import os
import pandas as pd

dirname = os.path.dirname(__file__)
csv_path = os.path.join(dirname, 'fuels.csv')

coal_l = pd.read_csv(csv_path, usecols=['Fuel type', 'M_C(%)', 'M_HHV(MJ/kg)'])
options = list(coal_l['Fuel type'])
"""options = [
    'lignite b',
    'lignite a',
    'sub-bituminous c',
    'sub-bituminous b',
    'sub-bituminous a',
    'bituminous_high volatile c', # close to default
    'bituminous_high volatile b',
    'bituminous_high volatile a',
    'bituminous medium volatile',
    'bituminous low volatile',
    'semi-anthracite',
    'anthracite',
    'meta-anthracite',
    'bf-bof',
    'corex-bof',
    'hisarna-bof',
    'h-dri-eaf',
    'ng-dri-eaf',
    'coal-dri-eaf (bituminous)',
    'scrap-eaf',
    'india-test-raniganj',
    'india-test-west-bokaro'
]"""

def fuel_type(i):
    """if i=='lignite b':
        c_coal = coal_l['M_C(%)'][0] # carbon content
        hhv_coal = coal_l['M_HHV(MJ/kg)'][0] # hhv of coal
    elif i=='lignite a':
        c_coal = coal_l['M_C(%)'][1] # carbon content
        hhv_coal = coal_l['M_HHV(MJ/kg)'][1] # hhv of coal
    elif i=='sub-bituminous c':
        c_coal = coal_l['M_C(%)'][2] # carbon content
        hhv_coal = coal_l['M_HHV(MJ/kg)'][2] # hhv of coal
    elif i=='sub-bituminous b':
        c_coal = coal_l['M_C(%)'][3] # carbon content
        hhv_coal = coal_l['M_HHV(MJ/kg)'][3] # hhv of coal
    elif i=='sub-bituminous a':
        c_coal = coal_l['M_C(%)'][4] # carbon content
        hhv_coal = coal_l['M_HHV(MJ/kg)'][4] # hhv of coal
    elif i=='bituminous_high volatile c':
        c_coal = coal_l['M_C(%)'][5] # carbon content
        hhv_coal = coal_l['M_HHV(MJ/kg)'][5] # hhv of coal
    elif i=='bituminous_high volatile b':
        c_coal = coal_l['M_C(%)'][6] # carbon content
        hhv_coal = coal_l['M_HHV(MJ/kg)'][6] # hhv of coal
    elif i=='bituminous_high volatile a':
        c_coal = coal_l['M_C(%)'][7] # carbon content
        hhv_coal = coal_l['M_HHV(MJ/kg)'][7] # hhv of coal
    elif i=='bituminous medium volatile':
        c_coal = coal_l['M_C(%)'][8] # carbon content
        hhv_coal = coal_l['M_HHV(MJ/kg)'][8] # hhv of coal
    elif i=='bituminous low volatile':
        c_coal = coal_l['M_C(%)'][9] # carbon content
        hhv_coal = coal_l['M_HHV(MJ/kg)'][9] # hhv of coal
    elif i=='semi-anthracite':
        c_coal = coal_l['M_C(%)'][10] # carbon content
        hhv_coal = coal_l['M_HHV(MJ/kg)'][10] # hhv of coal
    elif i=='anthracite':
        c_coal = coal_l['M_C(%)'][11] # carbon content
        hhv_coal = coal_l['M_HHV(MJ/kg)'][11] # hhv of coal
    elif i=='meta-anthracite':
        c_coal = coal_l['M_C(%)'][12] # carbon content
        hhv_coal = coal_l['M_HHV(MJ/kg)'][12] # hhv of coal
    elif i=='bf-bof default':
        c_coal = 60.2023 # default bf-bof
        hhv_coal = 26.33727 # default bf-bof
    elif i=='corex-bof default':
        c_coal = 71 # default corex
        hhv_coal = 21.1 # default corex
    elif i=='hisarna default':
        c_coal = 67.27273  # default hisarna. source 2
        hhv_coal = 28.7  # default hisarna. source 2
    elif i=='h-dri-eaf':
        c_coal = 60.38  # default hydrogen based DRI-EAF. source 2
        hhv_coal = 28.7  # default hydrogen based DRI-EAF. source 2
    elif i == 'ng-dri-eaf':
        c_coal = 60.38  # default hydrogen based DRI-EAF. source 2
        hhv_coal = 28.7  # default hydrogen based DRI-EAF. source 2
    elif i == 'coal-dri-eaf (bituminous)':
        c_coal = 60.60  # default hydrogen based DRI-EAF. source 2
        hhv_coal = 28.7  # default hydrogen based DRI-EAF. source 2
    elif i == 'india-raniganj':
        c_coal = 60.38  #for bf-bof. source 4
        hhv_coal = 17.919504  # for bf-bof. source 4
    elif i == 'india-west-bokaro':
            c_coal = 52.38  # for bf-bof source 4
            hhv_coal = 17.1575064 # for bf-bof. source 4
    else:"""
    c_coal = coal_l['M_C(%)'][i] #60.38  # default hydrogen based DRI-EAF. source 2
    hhv_coal = coal_l['M_HHV(MJ/kg)'][i] # 28.7  # default hydrogen based DRI-EAF. source 2
    fuel_characte = { 'c':c_coal,'hhv':hhv_coal,}
    return fuel_characte
