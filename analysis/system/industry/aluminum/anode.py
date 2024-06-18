"""
Functional unit: 1 tonne of anode
source: 1. European Aluminum Industry: https://european-aluminium.eu/media/3321/full-environmental-profile-report-2018.pdf
2. IEA electricity carbon intensity: https://www.iea.org/reports/tracking-power-2020
3. https://theicct.org/sites/default/files/publications/Well-to-wake-co2-mar2021-2.pdf (VLSO Marine Fuel)
"""

#import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

dirname = os.path.dirname(__file__)
csv_path = os.path.join(dirname, 'bayer_hall_heroult.csv')
from core.common import InputSource
import core.conditionals as conditionals
from core.inputs import OptionsInput, ContinuousInput, Default,Tooltip,InputGroup,ShareTableInput
import core.validators as validators

countries = ['Global','EU-27']
"""countries = [
    'India','China','Global','EU-27','Gulf Cooperation Council region','Indonesia',
]"""
material_flow = pd.read_csv(csv_path, usecols=['Processes'] + countries).fillna(0)  # read and save material flow information
# print(material_flow)
g = 0
"""c_coal = 0.0979   # emission factor kg co2/MJ
c_heavy_oil = 0.0851   # emission factor kg co2/MJ
c_diesel_oil = 0.0826 # emission factor kg co2/MJ
c_ng = 0.0632  # emission factor kg co2/MJ

hhv_coal = 27.05  # MJ/kg
hhv_heavy_oil = 43.05  # MJ/kg
hhv_diesel_oil = 42.9  # MJ/kg
hhv_ng = 49.5  # MJ/kg"""

def f_defaults(country):
    # energy related
    electricity_anode = float(material_flow[country][50]) / float(material_flow[country][53]) # kWh of electricity/tonne anode
    q_thermal_energy = float(material_flow[country][51])/ float(material_flow[country][53]) #MJ/tonne anode
    f_heavy_oil = float(material_flow[country][47])/q_thermal_energy * 100 # % of thermal energy
    f_diesel_oil = float(material_flow[country][48])/q_thermal_energy * 100
    f_vlso = 0
    f_ng = (100 - f_heavy_oil - f_diesel_oil) # the remaining energy

    # material related: mainly carbon source for carbon anode
    carbon_anode = float(material_flow[country][45])/ float(material_flow[country][53]) #tonne carbon / tonne anode
    f_carbon_coke = float(material_flow[country][37])/carbon_anode* 100 #%
    f_carbon_petroleum_coke = float(material_flow[country][37]) /carbon_anode* 100 #%
    f_carbon_bitumen = float(material_flow[country][37]) /carbon_anode* 100 #%
    f_carbon_anthracite = float(material_flow[country][37]) /carbon_anode* 100 #%
    f_carbon_calcined_coke = float(material_flow[country][37])/carbon_anode* 100  #%
    f_carbon_pitch = float(material_flow[country][37]) /carbon_anode* 100 #%
    f_carbon_butts = float(material_flow[country][37]) /carbon_anode* 100 #%
    f_carbon_green_anodes = (100 - f_carbon_coke - f_carbon_petroleum_coke - f_carbon_bitumen
        - f_carbon_anthracite -f_carbon_calcined_coke - f_carbon_pitch - f_carbon_butts) #%

    return {
        'electricity_anode': electricity_anode,
        'q_thermal_energy': q_thermal_energy,
        'f_heavy_oil': f_heavy_oil,
        'f_diesel_oil': f_diesel_oil,
        'f_vlso': f_vlso,
        'f_ng': f_ng,

        'carbon_anode': carbon_anode,
        'f_carbon_coke': f_carbon_coke,
        'f_carbon_petroleum_coke': f_carbon_petroleum_coke,
        'f_carbon_bitumen': f_carbon_bitumen,
        'f_carbon_anthracite':f_carbon_anthracite,
        'f_carbon_calcined_coke':f_carbon_calcined_coke,
        'f_carbon_pitch':f_carbon_pitch,
        'f_carbon_butts':f_carbon_butts,
        'f_carbon_green_anodes':f_carbon_green_anodes,
    }
def anode_input(cls):
    return [
        InputGroup('anode_energy','Anode Production: Energy consumption', children = [
            ContinuousInput(
                'electricity_anode', 'Electricity consumption',
                defaults=[
                    Default(f_defaults(country)['electricity_anode'], conditionals=[conditionals.input_equal_to('country', country)])
                    for country in countries
                ],
                unit = 'kWh/tonne anode',
                validators=[validators.numeric(), validators.gte(0)],
            ),
            ContinuousInput(
                'q_thermal_energy', 'Total thermal energy',
                defaults=[
                    Default(f_defaults(country)['q_thermal_energy'], conditionals=[conditionals.input_equal_to('country', country)])
                    for country in countries
                ],
                unit = 'MJ/tonne anode',
                validators=[validators.numeric(), validators.gte(0)],
            ),
            ShareTableInput(
                'f_energy_anode', 'Fraction of energy from:',
                columns = [None],
                rows = [
                    ShareTableInput.Row(
                        'Heavy Oil',
                        cells = [
                            ShareTableInput.Cell(defaults=[
                                Default(f_defaults(country)['f_heavy_oil'], conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),
                    ShareTableInput.Row(
                        'Diesel Oil',
                        cells = [
                            ShareTableInput.Cell(defaults=[
                                Default(f_defaults(country)['f_diesel_oil'], conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),
                    ShareTableInput.Row(
                        'Very Low Sulfur Furnace Oil (VLSFO)',
                        cells=[
                            ShareTableInput.Cell(defaults=[
                                Default(f_defaults(country)['f_vlso'],
                                        conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),
                    ShareTableInput.Row(
                        'Natural Gas',
                        cells = [
                            ShareTableInput.Cell(defaults=[
                                Default(f_defaults(country)['f_ng'], conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),                    
                ] ),
        ]),
        InputGroup('anode_material','Anode Production: Material consumption', children = [
           ContinuousInput(
               'anode_carbon', 'Total amount of carbon needed',
               unit = 'tonne/tonne anode',
               defaults=[
                   Default(f_defaults(country)['carbon_anode'], conditionals=[conditionals.input_equal_to('country', country)])
                   for country in countries
               ],
               validators=[validators.numeric(), validators.gte(0)],
           ),

           ShareTableInput(
                'f_carbon_anode', 'Fraction of carbon from:',
                columns = [None],
                rows = [
                    ShareTableInput.Row(
                        'Coke',
                        cells = [
                            ShareTableInput.Cell(defaults=[
                                Default(f_defaults(country)['f_carbon_coke'], conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),
                    ShareTableInput.Row(
                        'Petroleum coke',
                        cells = [
                            ShareTableInput.Cell(defaults=[
                                Default(f_defaults(country)['f_carbon_petroleum_coke'], conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),
                    ShareTableInput.Row(
                        'Bitumen',
                        cells = [
                            ShareTableInput.Cell(defaults=[
                                Default(f_defaults(country)['f_carbon_bitumen'], conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),
                    ShareTableInput.Row(
                        'Anthracite',
                        cells = [
                            ShareTableInput.Cell(defaults=[
                                Default(f_defaults(country)['f_carbon_anthracite'], conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),
                    ShareTableInput.Row(
                        'Calcined coke',
                        cells = [
                            ShareTableInput.Cell(defaults=[
                                Default(f_defaults(country)['f_carbon_calcined_coke'], conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),
                    ShareTableInput.Row(
                        'Pitch',
                        cells = [
                            ShareTableInput.Cell(defaults=[
                                Default(f_defaults(country)['f_carbon_pitch'], conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),
                    ShareTableInput.Row(
                        'Butts',
                        cells = [
                            ShareTableInput.Cell(defaults=[
                                Default(f_defaults(country)['f_carbon_butts'], conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),
                    ShareTableInput.Row(
                        'Green anodes',
                        cells = [
                            ShareTableInput.Cell(defaults=[
                                Default(f_defaults(country)['f_carbon_green_anodes'], conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),
                    
                ]
            ),]),
         ]    


def anode_carbon(self,m_anode=1):
    m_total_raw_carbon = self.anode_carbon * m_anode #float(material_flow[country][45]) * m_anode #tonne of carbon
    f_carbon_anode = self.f_carbon_anode #%
    m_coke = f_carbon_anode[0]/100 * m_total_raw_carbon # tonne of carbon from coke
    m_petroleum_coke = f_carbon_anode[1]/100 * m_total_raw_carbon # tonne of carbon from petroleum coke
    m_bitumen = f_carbon_anode[2]/100 * m_total_raw_carbon # tonne of carbon from bitumen
    m_anthracite = f_carbon_anode[3]/100 * m_total_raw_carbon # tonne of carbon from anthracite
    m_calcined_coke = f_carbon_anode[4]/100 * m_total_raw_carbon # tonne of carbon from calcined coke
    m_pitch = f_carbon_anode[5]/100 * m_total_raw_carbon # tonne of carbon from pitch
    m_butts = f_carbon_anode[6]/100 * m_total_raw_carbon # tonne of carbon from butts
    m_green_anodes = f_carbon_anode[7]/100 * m_total_raw_carbon # tonne of carbon from green anodes


    co2_calcined_coke = m_calcined_coke * 44/12 # tonne CO2
    co2_pitch = m_pitch * 44/12 # tonne CO2
    co2_butts = m_butts* 44/12 # tonne CO2
    co2_green_anodes = m_green_anodes* 44/12 # tonne CO2
    co2_anode_carbon = m_total_raw_carbon * 44/12 # total tonne CO2 emitted from anode consumption
    return {
        'total raw carbon': m_total_raw_carbon,
        'co2 anode carbon': co2_anode_carbon,
    }

def anode_energy(self,m_anode=1, c_electricity = 0.063,c_coal=0.0979,c_heavy_oil=0.0851,
                c_diesel_oil=0.0826, c_ng=0.0632, hhv_coal=27.05, hhv_heavy_oil=43.05,hhv_diesel_oil=42.9,hhv_ng=49.5):
    q_thermal_energy = self.q_thermal_energy * m_anode # MJ of thermal energy
    f_energy = self. f_energy_anode # in %
    f_heavy_oil = f_energy[0] / 100
    f_diesel_oil = f_energy[1] / 100
    f_vlso = f_energy[2]/100
    f_ng = f_energy[3] / 100
    q_coal_anode = (1-f_ng-f_heavy_oil-f_diesel_oil-f_vlso)*q_thermal_energy # MJ
    q_heavy_oil = f_heavy_oil * q_thermal_energy # MJ
    q_diesel_oil = f_diesel_oil * q_thermal_energy # MJ
    q_vlso = f_vlso* q_thermal_energy #MJ
    q_ng = f_ng * q_thermal_energy # MJ
    q_electricity = self.electricity_anode * 0.0036 * m_anode #float(material_flow[country][50]) * 0.0036 * m_anode # GJ

    m_coal_anode = q_coal_anode/hhv_coal/1000 # tonne of coal
    m_heavy_oil_anode = q_heavy_oil/hhv_heavy_oil/1000 # tonne of heavy oil
    m_diesel_oil_anode = q_diesel_oil/hhv_diesel_oil/1000 # tonne of diesel oil
    m_ng_anode = q_ng/hhv_ng/1000 # tonne of NG
    e_content_vlso = 0.0422 #MJ/g fuel source 3
    m_vlso_anode = q_vlso/e_content_vlso*10**-6 #tonne of VLSO

    c_vlso = 3.188/0.0422 # g CO2 / MJ of VLSO # source 3
    co2_vlso_anode = q_vlso * c_vlso / 10 ** 6  # tonne of co2 from vlso
    co2_coal_anode = q_coal_anode * c_coal/1000  # tonne of co2 from coal
    co2_heavy_oil_anode = q_heavy_oil * c_heavy_oil/1000  # tonne of co2 from heavy oil
    co2_diesel_oil_anode = q_diesel_oil * c_diesel_oil/1000 # tonne of co2 from diesel oil
    co2_ng_anode = q_ng * c_ng/1000  # tonne of co2 from ng
    co2_electricity_anode = q_electricity * np.array(c_electricity) # tonne of co2 from electricity.

    return {
        'coal': m_coal_anode,
        'heavy oil': m_heavy_oil_anode,
        'diesel oil': m_diesel_oil_anode,
        'vlso': m_vlso_anode,
        'ng': m_ng_anode,
        'electricity': q_electricity,
        'co2 coal': co2_coal_anode,
        'co2 heavy oil': co2_heavy_oil_anode,
        'co2 diesel oil': co2_diesel_oil_anode,
        'co2 vlso': co2_vlso_anode,
        'co2 ng': co2_ng_anode,
        'co2 electricity': co2_electricity_anode,
    }





























