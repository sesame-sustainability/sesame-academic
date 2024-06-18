"""
Functional unit: 1 tonne of alumina
source: 1. European Aluminum Industry: https://european-aluminium.eu/media/3321/full-environmental-profile-report-2018.pdf
2. IEA electricity carbon intensity: https://www.iea.org/reports/tracking-power-2020
3.https://theicct.org/sites/default/files/publications/Well-to-wake-co2-mar2021-2.pdf (VLSO Marine Fuel)

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

material_flow = pd.read_csv(csv_path, usecols=['Processes'] + countries).fillna(0)

#country = input("location of the plant: EU-27")

def f_defaults(country): # energy default
    # f_heavy_oil_alumina, f_coal_alumina, f_ng_alumina, f_steam_alumina: % of energy from heavy oil, coal, ng, steam used in alumina produciton
    #%
    electricity_alumina = float(material_flow[country][28]) /float(material_flow[country][31])  # kWh of electricity/tonne alumina
    q_thermal_energy = float(material_flow[country][29])/float(material_flow[country][31]) #MJ/tonne alumina
    f_coal_alumina = float(material_flow[country][23])/q_thermal_energy * 100
    f_heavy_oil_alumina = float(material_flow[country][24])/q_thermal_energy * 100
    f_diesel_oil_alumina = float(material_flow[country][25])/q_thermal_energy * 100
    f_ng_alumina = 0#float(material_flow[country][26])/q_thermal_energy * 100
    f_steam_alumina = (100-f_coal_alumina-f_heavy_oil_alumina-f_diesel_oil_alumina-f_ng_alumina)  #the reminder energy
    f_vlso_alumina = 0
    return {
        'electricity_alumina': electricity_alumina,
        'q_thermal_energy_alumina': q_thermal_energy,
        'f_coal_alumina': f_coal_alumina,
        'f_heavy_oil_alumina': f_heavy_oil_alumina,
        'f_diesel_oil_alumina': f_diesel_oil_alumina,
        'f_vlso_alumina': f_vlso_alumina,
        'f_ng_alumina':f_ng_alumina,
        'f_steam_alumina':f_steam_alumina,
    }

def m_defaults(country): # material default
    m_alumina = float(material_flow[country][31])
    m_bauxite = float(material_flow[country][16])/ m_alumina # tonne of bauxite / tonne alumina
    m_naoh = float(material_flow[country][17]) / m_alumina # tonne of NaOH / tonne alumina
    m_caoh2 = float(material_flow[country][18]) / m_alumina # tonne of CaOH2/ tonne alumina
    m_flocullant = float(material_flow[country][19])/ m_alumina  # tonne of flocullant/ tonne alumina
    m_cao = float(material_flow[country][20]) / m_alumina # tonne of CaO/ tonne alumina
    return {
        'm_bauxite':m_bauxite,
        'm_naoh':m_naoh,
        'm_caoh2':m_caoh2,
        'm_flocullant':m_flocullant,
        'm_cao':m_cao,
    }



def alumina_input(cls):
    return [
        InputGroup('alumina_energy','Alumina Refining: Energy consumption', children =[
            ContinuousInput(
                'electricity_alumina', 'Electricity consumption',
                defaults=[
                    Default(f_defaults(country)['electricity_alumina'], conditionals=[conditionals.input_equal_to('country', country)])
                    for country in countries
                ],
                unit = 'kWh/tonne alumina',
                validators=[validators.numeric(), validators.gte(0)],
            ),
            ContinuousInput(
                'q_thermal_energy_alumina', 'Total thermal energy',
                defaults=[
                    Default(f_defaults(country)['q_thermal_energy_alumina'], conditionals=[conditionals.input_equal_to('country', country)])
                    for country in countries
                ],
                unit = 'MJ/tonne alumina',
                validators=[validators.numeric(), validators.gte(0)],
            ),
            ShareTableInput(
                'f_energy_alumina', '% of energy from:',
                columns = [None],
                rows = [
                    ShareTableInput.Row(
                        'Coal',
                        cells = [
                            ShareTableInput.Cell(defaults=[
                                Default(f_defaults(country)['f_coal_alumina'], conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),
                    ShareTableInput.Row(
                        'Heavy Oil',
                        cells = [
                            ShareTableInput.Cell(defaults=[
                                Default(f_defaults(country)['f_heavy_oil_alumina'], conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),
                    ShareTableInput.Row(
                        'Diesel Oil',
                        cells = [
                            ShareTableInput.Cell(defaults=[
                                Default(f_defaults(country)['f_diesel_oil_alumina'], conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),
                    ShareTableInput.Row(
                        'Very Low Sulfur Furnace Oil (VLSFO)',
                        cells=[
                            ShareTableInput.Cell(defaults=[
                                Default(f_defaults(country)['f_vlso_alumina'],
                                        conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),
                    ShareTableInput.Row(
                        'Natural Gas',
                        cells = [
                            ShareTableInput.Cell(defaults=[
                                Default(f_defaults(country)['f_ng_alumina'], conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),

                    ShareTableInput.Row(
                        'Steam',
                        cells = [
                            ShareTableInput.Cell(defaults=[
                                Default(f_defaults(country)['f_steam_alumina'], conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),

                ],

            ),
            # OptionsInput(
            #     'steam_source', 'Steam Generation Fuel (for Boiler)',
            #     defaults=Default('Coal'),
            #     tooltip=Tooltip('Assuming boiler generates steam onsite, choose fuel to determine associated emissions. Defaults based on GREET process emissions (see SESAME "Build")')
            # ),
            ]),
       InputGroup('alumina_material','Alumina Refining: Material consumption', children = [
           ContinuousInput(
               'm_bauxite', 'Amount of bauxite needed',
               unit = 'tonne/tonne alumina',
               defaults=[
                   Default(m_defaults(country)['m_bauxite'], conditionals=[conditionals.input_equal_to('country', country)])
                   for country in countries
               ],
               validators=[validators.numeric(), validators.gte(0)],
           ),
           ContinuousInput(
               'm_naoh', 'Amount of NaOH needed',
               unit = 'tonne/tonne alumina',
               defaults=[
                   Default(m_defaults(country)['m_naoh'], conditionals=[conditionals.input_equal_to('country', country)])
                   for country in countries
               ],
               validators=[validators.numeric(), validators.gte(0)],
           ),
           ContinuousInput(
               'm_caoh2', 'Amount of Ca(OH)2 needed',
               unit = 'tonne/tonne alumina',
               defaults=[
                   Default(m_defaults(country)['m_caoh2'], conditionals=[conditionals.input_equal_to('country', country)])
                   for country in countries
               ],
               validators=[validators.numeric(), validators.gte(0)],
           ),
           ContinuousInput(
               'm_flocullant', 'Amount of flocullant needed',
               unit = 'tonne/tonne alumina',
               defaults=[
                   Default(m_defaults(country)['m_flocullant'], conditionals=[conditionals.input_equal_to('country', country)])
                   for country in countries
               ],
               validators=[validators.numeric(), validators.gte(0)],
           ),
           ContinuousInput(
               'm_cao', 'Amount of CaO needed',
               unit = 'tonne/tonne alumina',
               defaults=[
                   Default(m_defaults(country)['m_cao'], conditionals=[conditionals.input_equal_to('country', country)])
                   for country in countries
               ],
               validators=[validators.numeric(), validators.gte(0)],
           ),
       ]),
    ]


def alumina(self, m_alumina, c_electricity):
    #print (f"m_caoh2:{m_defaults(country)['m_caoh2']};m_flocullant:{m_defaults(country)['m_flocullant']}")
    #m_alumina: tonne of alumina to be produced.
    #print(f"alumina energy %: {f_defaults(country)}")
    #Energy consumption input from user
    f_energy_alumina = self.f_energy_alumina # %
    print(f"f energy alumina: {f_energy_alumina}")
    f_coal_alumina = f_energy_alumina[0] / 100 # fractions
    f_heavy_oil_alumina = f_energy_alumina[1] / 100
    f_vlso_alumina = f_energy_alumina[2] / 100
    f_diesel_oil_alumina = f_energy_alumina[3] / 100
    f_ng_alumina = f_energy_alumina[4] / 100
    f_steam_alumina = f_energy_alumina[5] / 100

    # Material consumption input from user * m_alumina = total material consumption (tonne)
    m_bauxite = self.m_bauxite * m_alumina # tonne of bauxite needed
    m_naoh = self.m_naoh * m_alumina # tonne of NaOH (100%) needed
    m_caoh2 = self.m_caoh2 * m_alumina # tonne of CaOH2
    m_flocullant = self.m_flocullant * m_alumina # tonne of flocullant
    m_cao = self.m_cao * m_alumina # tonne of CaO

    # thermaal energy needed
    q_thermal_energy_alumina = self.q_thermal_energy_alumina * m_alumina  # MJ of thermal energy
    q_coal_alumina = f_coal_alumina * q_thermal_energy_alumina  # MJ of coal
    q_heavy_oil_alumina = f_heavy_oil_alumina * q_thermal_energy_alumina  # MJ of heavy oil
    q_diesel_oil_alumina = f_diesel_oil_alumina * q_thermal_energy_alumina  # MJ of diesel oil
    q_vlso_alumina = f_vlso_alumina * q_thermal_energy_alumina  # MJ
    q_ng_alumina = f_ng_alumina * q_thermal_energy_alumina  # MJ of NG
    q_steam_alumina = f_steam_alumina * q_thermal_energy_alumina  # MJ of steam

    electricity_alumina = self.electricity_alumina *0.0036* m_alumina #float(material_flow[country][28]) * 0.0036 * m_alumina # GJ of electricity

    # f_heavy_oil_bauxite: fraction of thermal energy provided by heaby oil. The other part is provided by diesel oil.
    #c_heavy_oil,c_diesel_oil...: emisison factors kg co2/MJ
    #c_electricity: tonne CO2/GJ electricity
    #  hhv: MJ/kg


    c_coal = 0.0979
    c_heavy_oil = 0.0851
    c_diesel_oil=0.0826
    c_ng = 0.0632
    c_steam = 0.0702
    hhv_coal = 27.05
    hhv_heavy_oil=43.05
    hhv_diesel_oil=42.9
    hhv_ng = 49.5
    steam_heat_content = 25.86

    m_coal_alumina = q_coal_alumina / hhv_coal/1000 # tonne coal used in alumina production
    m_heavy_oil_alumina = q_heavy_oil_alumina / hhv_heavy_oil/1000  # tonne of heavy oil
    m_diesel_oil_alumina = q_diesel_oil_alumina / hhv_diesel_oil/1000  # tonne of diesel oil
    e_content_vlso = 0.0422  # MJ/g fuel
    m_vlso_alumina = q_vlso_alumina / e_content_vlso * 10 ** -6  # tonne of VLSO source 3
    m_ng_alumina = q_ng_alumina / hhv_ng/1000  # tonne of natural gas
    m_steam_alumina = q_steam_alumina / steam_heat_content/1000  # tonne of steam

    c_vlso = 3.188 / 0.0422  # g CO2 / MJ of VLSO # source 3
    co2_vlso_alumina = q_vlso_alumina * c_vlso / 10 ** 6  # tonne of co2 from vlso
    co2_coal_alumina = q_coal_alumina * c_coal /1000 # tonne of CO2
    co2_heavy_oil_alumina = q_heavy_oil_alumina * c_heavy_oil/1000  # tonne of CO2
    co2_diesel_oil_alumina = q_diesel_oil_alumina * c_diesel_oil/1000  # tonne of CO2
    co2_ng_alumina = q_ng_alumina * c_ng/1000  # tonne of CO2
    co2_steam_alumina = q_steam_alumina * c_steam/1000 # tonne of CO2.
    co2_electricity_alumina = electricity_alumina * np.array(c_electricity) # tonne of CO2

    return {
        'bauxite': m_bauxite,
        'naoh': m_naoh,
        'caoh2': m_caoh2,
        'flocullant': m_flocullant,
        'cao': m_cao,
        'coal': m_coal_alumina,
        'heavy oil': m_heavy_oil_alumina,
        'diesel oil': m_diesel_oil_alumina,
        'vlso': m_vlso_alumina,
        'natural gas': m_ng_alumina,
        'steam': m_steam_alumina,
        'total thermal energy': q_thermal_energy_alumina,
        'electricity alumina': electricity_alumina,

        'co2 coal': co2_coal_alumina,
        'co2 heavy oil': co2_heavy_oil_alumina,
        'co2 diesel oil': co2_diesel_oil_alumina,
        'co2 vlso': co2_vlso_alumina,
        'co2 ng': co2_ng_alumina,
        'co2 steam': co2_steam_alumina,
        'co2 electricity': co2_electricity_alumina,

        'f energy alumina': f_energy_alumina,
    }
"""a = alumina(1, f_defaults(country)['f_heavy_oil_alumina'],f_defaults(country)['f_coal_alumina'],
            f_defaults(country)['f_ng_alumina'],f_defaults(country)['f_diesel_oil_alumina'], 'EU-27')
print(f"alumina: {a}")"""
