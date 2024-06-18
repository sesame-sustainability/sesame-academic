"""
Functional unit: 1 tonne Al Ingot.
source: European Aluminum Industry: https://european-aluminium.eu/media/3321/full-environmental-profile-report-2018.pdf
3. https://theicct.org/sites/default/files/publications/Well-to-wake-co2-mar2021-2.pdf (VLSO Marine Fuel)
"""

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

material_flow = pd.read_csv(csv_path, usecols=['Processes'] + countries).fillna(0)

def f_defaults(country):
    m_ingot = float(material_flow[country][90])
    m_aluminum = float(material_flow[country][72])/m_ingot
    m_al_alternative = float(material_flow[country][78])/m_ingot
    q_thermal = float(material_flow[country][87])/m_ingot
    f_vlso = 0
    f_heavy_oil = float(material_flow[country][84])/q_thermal * 100
    f_diesel_oil = float(material_flow[country][85])/q_thermal * 100
    f_ng = (100 - f_heavy_oil - f_diesel_oil) # remaining energy
    q_electricity = float(material_flow[country][88]) /m_ingot # kWh/tonne ingot

    return {
        'm_aluminum': m_aluminum,
        'm_al_alternative': m_al_alternative,
        'q_thermal': q_thermal,
        'f_heavy_oil': f_heavy_oil,
        'f_diesel_oil': f_diesel_oil,
        'f_vlso': f_vlso,
        'f_ng': f_ng,
        'q_electricity': q_electricity,
    }

def ingot_input(cls):
    return [
        InputGroup('ingot_energy','Ingot Production: Energy consumption', children=[
            ContinuousInput(
                'q_electricity','Electricity consumption',
                defaults=[
                    Default(f_defaults(country)['q_electricity'], conditionals=[conditionals.input_equal_to('country',country)])
                    for country in countries
                ],
                unit='kWh/tonne ingot',
                validators=[validators.numeric(), validators.gte(0)],
            ),
            ContinuousInput(
                'q_thermal','Total thermal energy',
                defaults=[
                    Default(f_defaults(country)['q_thermal'], conditionals=[conditionals.input_equal_to('country',country)])
                    for country in countries
                ],
                unit='MJ/tonne ingot',
                validators=[validators.numeric(), validators.gte(0)],
            ),
            ShareTableInput(
                'f_energy', '% of energy from:',
                columns=[None],
                rows=[
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
                ]
            ),
        ]),
        InputGroup('ingot_material','Ingot Production: Material consumption', children=[
            ContinuousInput(
                'm_aluminum','Liquid aluminum',
                defaults=[
                    Default(f_defaults(country)['m_aluminum'], conditionals=[conditionals.input_equal_to('country',country)])
                    for country in countries
                ],
                unit = 'tonne/tonne ingot',
                validators=[validators.numeric(), validators.gte(0)],
            ),
            ContinuousInput(
                'm_al_alternative','Aluminum alternatives',
                defaults=[
                    Default(f_defaults(country)['m_al_alternative'], conditionals=[conditionals.input_equal_to('country',country)])
                    for country in countries
                ],
                unit = 'tonne/tonne ingot',
                validators=[validators.numeric(), validators.gte(0)],
            ),
        ]),
    ]

def ingot(self,m_ingot, c_electricity):
    q_thermal = self.q_thermal # MJ
    f_energy = self.f_energy # %
    q_heavy_oil = f_energy[0] / 100 * q_thermal * m_ingot # MJ
    q_diesel_oil = f_energy[1] / 100 * q_thermal * m_ingot # MJ
    q_vlso = f_energy[2] / 100* q_thermal * m_ingot # MJ
    q_ng = f_energy[3] / 100 * q_thermal * m_ingot # MJ
    q_electricity = self.q_electricity * 0.0036 * m_ingot # GJ

    #c_heavy_oil,c_diesel_oil...: emisison factors kg co2/MJ
    #c_electricity: tonne CO2/GJ electricity
    #HHV: MJ/kg
    c_heavy_oil = 0.0851
    c_diesel_oil=0.0826
    c_ng = 0.0632
    hhv_heavy_oil=43.05
    hhv_diesel_oil=42.9
    hhv_ng = 49.5

    c_vlso = 3.188 / 0.0422  # g CO2 / MJ of VLSO # source 2
    co2_vlso_anode = q_vlso * c_vlso / 10 ** 6  # tonne of co2 from vlso
    co2_heavy_oil = q_heavy_oil * c_heavy_oil / 1000 # tonne of CO2
    co2_diesel_oil = q_diesel_oil * c_diesel_oil / 1000 # tonne CO2
    co2_ng = q_ng * c_ng / 1000 # tonne CO2
    co2_electricity = q_electricity * c_electricity # tonne CO2

    m_heavy_oil = q_heavy_oil / hhv_heavy_oil / 1000 # tonne heavy oil
    m_diesel_oil = q_diesel_oil / hhv_diesel_oil /1000 # tonne diesel oil
    e_content_vlso = 0.0422  # MJ/g fuel
    m_vlso = q_vlso / e_content_vlso * 10 ** -6  # tonne of VLSO source 2
    m_ng = q_ng / hhv_ng / 1000 # tonne ng
    m_aluminum = self.m_aluminum * m_ingot # tonne al
    m_al_alternative = self.m_al_alternative * m_ingot # tonne al alternative

    return {
        'q_electricity': q_electricity,
        'co2_heavy_oil': co2_heavy_oil,
        'co2_diesel_oil': co2_diesel_oil,
        'co2 vlso': co2_vlso_anode,
        'co2_ng': co2_ng,
        'co2_electricity':co2_electricity,
        'm_heavy_oil': m_heavy_oil,
        'm_diesel_oil': m_diesel_oil,
        'm_vlso': m_vlso,
        'm_ng':m_ng,
        'm_aluminum':m_aluminum,
        'm_al_alternative':m_al_alternative,
    }
