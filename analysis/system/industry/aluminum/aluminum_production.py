"""
Functional unit: 1 tonne of aluminum
source: 1. European Aluminum Industry: https://european-aluminium.eu/media/3321/full-environmental-profile-report-2018.pdf
2. IEA electricity carbon intensity: https://www.iea.org/reports/tracking-power-2020
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
material_flow = pd.read_csv(csv_path, usecols=['Processes'] + countries)  # read and save material flow information

def aluminum_production(country='EU-27'): # functional unit: 1 tonne aluminum
    m_aluminum = float(material_flow[country][66]) # referenced amount of aluminum produced for specific ocuntry
    m_alumina = float(material_flow[country][57]) / m_aluminum # tonne of alumina needed
    m_anode = float(material_flow[country][58]) / m_aluminum # tonne of anode needed
    m_aluminum_fluoride = float(material_flow[country][59]) / m_aluminum # tonne of aluminum fluoride
    m_cathode_carbon = float(material_flow[country][60]) / m_aluminum # tonne of cathode carbon
    m_steel = float(material_flow[country][61]) / m_aluminum # tonne of steel

    q_electricity = float(material_flow[country][64]) / m_aluminum  # kWh of electricity
    
    #co2_electricity = q_electricity * np.array(c_electricity) # tonne of Co2 emitted due to electricity use.

    return {
        'alumina': m_alumina,
        'anode': m_anode,
        'aluminum fluoride': m_aluminum_fluoride,
        'cathode carbon': m_cathode_carbon,
        'steel': m_steel,
        'electricity': q_electricity,
        #'co2 electricity': co2_electricity,
    }

def aluminum_input(cls):
    return [
        InputGroup('aluminum_energy','Aluminum Smelting: Energy consumption', children = [
            ContinuousInput(
                'electricity', 'Amount of electricity needed',
                unit = 'kWh/tonne aluminum',
                defaults=[
                    Default(aluminum_production(country)['electricity'], conditionals=[conditionals.input_equal_to('country', country)])
                    for country in countries
                ],
                validators=[validators.numeric(), validators.gte(0)],
            ),
        ]),
        InputGroup('aluminum_material','Aluminum Smelting: Material consumption', children = [
           ContinuousInput(
               'm_alumina', 'Amount of alumina needed',
               unit = 'tonne/tonne aluminum',
               defaults=[
                   Default(aluminum_production(country)['alumina'], conditionals=[conditionals.input_equal_to('country', country)])
                   for country in countries
               ],
               validators=[validators.numeric(), validators.gte(0)],
           ),
           ContinuousInput(
               'm_anode', 'Amount of anode needed',
               unit = 'tonne/tonne aluminum',
               defaults=[
                   Default(aluminum_production(country)['anode'], conditionals=[conditionals.input_equal_to('country', country)])
                   for country in countries
               ],
               validators=[validators.numeric(), validators.gte(0)],
           ),
           ContinuousInput(
               'm_aluminum_fluoride', 'Amount of aluminum fluoride needed',
               unit = 'tonne/tonne aluminum',
               defaults=[
                   Default(aluminum_production(country)['aluminum fluoride'], conditionals=[conditionals.input_equal_to('country', country)])
                   for country in countries
               ],
               validators=[validators.numeric(), validators.gte(0)],
           ),
           ContinuousInput(
               'm_cathode_carbon', 'Amount of cathode carbon needed',
               unit = 'tonne/tonne aluminum',
               defaults=[
                   Default(aluminum_production(country)['cathode carbon'], conditionals=[conditionals.input_equal_to('country', country)])
                   for country in countries
               ],
               validators=[validators.numeric(), validators.gte(0)],
           ),
           ContinuousInput(
               'm_steel', 'Amount of steel needed',
               unit = 'tonne/tonne aluminum',
               defaults=[
                   Default(aluminum_production(country)['steel'], conditionals=[conditionals.input_equal_to('country', country)])
                   for country in countries
               ],
               validators=[validators.numeric(), validators.gte(0)],
           ),
           
       ]),
    ]

def aluminum_user(self, m_aluminum, c_electricity):
    # material consumption input from user
    m_alumina = self.m_alumina * m_aluminum 
    m_anode = self.m_anode * m_aluminum
    m_aluminum_fluoride = self.m_aluminum_fluoride * m_aluminum
    m_cathode_carbon = self.m_cathode_carbon * m_aluminum
    m_steel = self.m_steel * m_aluminum
    q_electricity = self.electricity * 0.0036 * m_aluminum # GJ
    print(f"separate aluminum electricity: {q_electricity}")
    co2_electricity = q_electricity * np.array(c_electricity) # tonne of Co2 emitted due to electricity use.
    return {
        'alumina': m_alumina,
        'anode': m_anode,
        'aluminum fluoride': m_aluminum_fluoride,
        'cathode carbon': m_cathode_carbon,
        'steel': m_steel,
        'electricity': q_electricity,
        'co2 electricity': co2_electricity,
    }
#print(material_flow['EU-27'][57]*2)
        