"""
Functional unit: 1 tonne of aluminum
@author: Lingyan Deng
"""

import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

from core.common import InputSource, Color
import core.conditionals as conditionals
from core.inputs import OptionsInput, ContinuousInput, PercentInput, Default,Tooltip,InputGroup, ShareTableInput
import core.validators as validators
from analysis.system.industry.aluminum.project_elec_co2 import elec_co2
from analysis.system.industry.cement.elec_input import user_inputs_ft_cap,co2_int
from analysis.system.industry.aluminum.capex import capexs
from analysis.system.industry.aluminum.cepci import cepci_v
from analysis.system.industry.aluminum.ppp import pppv
from analysis.system.industry.aluminum.exchange_rate import exchange_country
from analysis.system.industry.aluminum.opex_remelt import opex_input


#########################################
dirname = os.path.dirname(__file__)
csv_path = os.path.join(dirname, 'recycle.csv')

countries = ['Global','EU-27']
"""countries = [
    'India','China','Global','EU-27','Gulf Cooperation Council region','Indonesia',
]"""
material_flow = pd.read_csv(csv_path, usecols=['Processes'] + countries)  # read and save material flow information
#########################################
def remelt_default(country): # functional unit: 1 tonne aluminum
    m_aluminum = float(material_flow[country][8]) 
    q_total = float(material_flow[country][6]) / m_aluminum  # MJ of energy
    m_scrap = float(material_flow[country][1]) / m_aluminum  # tonne scrap
    f_electricity = float(material_flow[country][2]) *1000 / q_total *100 # % energy from electricity
    f_heavy_oil = float(material_flow[country][3]) / q_total *100 # % energy from heavy oil
    f_diesel_oil = float(material_flow[country][4]) / q_total *100 # % energy from diesel oil
    f_ng = float(material_flow[country][5]) / q_total *100 # % energy from ng
    

    return {
        'm_scrap': m_scrap,
        'f_electricity': f_electricity,
        'f_heavy_oil': f_heavy_oil,
        'f_diesel_oil': f_diesel_oil,
        'f_ng': f_ng,
        'q_total': q_total,
    }


class REMELTALUMINUM(InputSource):

    @classmethod
    def user_inputs(cls):
        return user_inputs_ft_cap(cls,countries) + [
            # OptionsInput(
            #     'country', 'The location of the plant',
            #     defaults = [Default('EU-27')],
            #     options = ['Global','EU-27'] #['India','China','Global','EU-27','Gulf Cooperation Council region','Indonesia']
            # ),
            InputGroup('aluminum_material','Aluminum Remelting', children = [
                ContinuousInput(
                    'm_scrap', 'Amount of scrap needed',
                    unit = 'tonne/tonne aluminum',
                    defaults=[
                        Default(remelt_default(country)['m_scrap'], conditionals=[conditionals.input_equal_to('country', country)])
                        for country in countries
                    ],
                    validators=[validators.numeric(), validators.gte(0)],
                ),
                ContinuousInput(
                    'q_total', 'Total thermal energy',
                    unit = 'MJ/tonne aluminum',
                    defaults=[
                        Default(remelt_default(country)['q_total'], conditionals=[conditionals.input_equal_to('country', country)])
                        for country in countries
                    ],
                    validators=[validators.numeric(), validators.gte(0)],
                ),
               ShareTableInput(
                'f_energy_aluminum', 'Fraction of energy from:',
                columns = [None],
                rows = [
                    ShareTableInput.Row(
                        'Heavy Oil',
                        cells = [
                            ShareTableInput.Cell(defaults=[
                                Default(remelt_default(country)['f_heavy_oil'], conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),
                    ShareTableInput.Row(
                        'Diesel Oil',
                        cells = [
                            ShareTableInput.Cell(defaults=[
                                Default(remelt_default(country)['f_diesel_oil'], conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),
                    ShareTableInput.Row(
                        'Natural Gas',
                        cells = [
                            ShareTableInput.Cell(defaults=[
                                Default(remelt_default(country)['f_ng'], conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),
                    ShareTableInput.Row(
                        'Electricity',
                        cells = [
                            ShareTableInput.Cell(defaults=[
                                Default(remelt_default(country)['f_electricity'], conditionals=[conditionals.input_equal_to('country', country)])
                                for country in countries
                            ]),
                        ]
                    ),
                ]
            ) 
            ]),
            InputGroup('capex', 'Cost Analysis', children=[
                ContinuousInput(
                    'plant_lifetime', 'Plant life time',
                    unit = 'years',
                    defaults=[Default(10)],
                    validators=[validators.numeric(), validators.gte(0)],
                ),
                ContinuousInput(
                    'capacity_aluminum', 'Aluminum plant capacity',
                    unit = 'million tonnes annually',
                    defaults=[Default(1.09)],
                    validators=[validators.numeric(), validators.gte(0)],
                ),
            
                ])
        ] + opex_input(cls)

    def run(self):
        country = self.country
        m_aluminum = pd.Series([1,1,1,1,1]) # 1 tonne of aluminum
        years = elec_co2(country)['years'][20:25]
        c_electricity = co2_int(self, years)


        q_total = self.q_total * m_aluminum
        f_energy_aluminum = self.f_energy_aluminum # #
        m_scrap = self.m_scrap * m_aluminum # tonne scrap
        q_heavy_oil = f_energy_aluminum[0] / 100 * q_total # MJ of energy
        q_diesel_oil = f_energy_aluminum[1] / 100 * q_total # MJ of energy
        q_ng = f_energy_aluminum[2] / 100 * q_total # MJ of energy
        q_electricity = f_energy_aluminum[3] / 100 * q_total/1000  # GJ of electricity
        print(f_energy_aluminum, m_scrap,q_total)

        # emission factor of fuel
        c_heavy_oil =0.0851 / 1000 # tonne co2/MJ
        c_ng = 0.0632 / 1000 # tonne co2/MJ
        c_diesel_oil = 0.0826 / 1000 # tonne co2/MJ

        # high heating value of fuel
        hhv_heavy_oil = 43.05 #self.hhv_heavy_oil # MJ/kg
        hhv_ng = 49.5 #self.hhv_ng # MJ/kg
        hhv_diesel_oil = 42.9 #self.hhv_diesel_oil # MJ/kg
        print(hhv_heavy_oil*10)
        # mass of fuel
        m_heav_oil = q_heavy_oil / hhv_heavy_oil / 1000 # tonne heavy oil
        m_ng = q_ng / hhv_ng / 1000 # tonne
        m_diesel_oil = q_diesel_oil / hhv_diesel_oil / 1000 # tonne

        # CO2 emission
        co2_electricity = q_electricity * np.array(c_electricity) # tonne co2
        co2_heavy_oil = q_heavy_oil * c_heavy_oil  # tonne co2
        co2_ng = q_ng * c_ng  # tonne co2
        co2_diesel_oil = q_diesel_oil * c_diesel_oil  # tonne co2

        t_direct_co2 = co2_heavy_oil + co2_ng + co2_diesel_oil
        t_indirect_co2 = co2_electricity
        t_co2 = t_direct_co2 + t_indirect_co2
        #print(t_co2)
        #===================================================================================================================
        #Economic analysis
        # CAPEX
        cepci2 = cepci_v(years[20])
        ppp2 = pppv(country,years[20])/exchange_country(country) # converted Euro to USD
        plant_lifetime = self.plant_lifetime
        capacity_aluminum = self.capacity_aluminum * 1e6
        capex_aluminum = np.array(capexs(capacity_aluminum,cepci2, ppp2)['capex_2ndaluminum'])
        capex = capex_aluminum*m_aluminum/plant_lifetime
        print('capex', capex)

        #opex
        c_material = m_scrap * self.ingot_price * (1 + self.ingot_price_change)
        c_heavy = m_heav_oil * self.heavy_price * (1 + self.heavy_price_change/100)
        c_diesel = m_diesel_oil * self.diesel_price * (1+ self.diesel_price_change/100)
        c_ng = q_ng/1000 * self.ng_price * (1+ self.ng_price_change/100)
        c_elec = q_electricity * self.elec_price*(1 + self.elec_price_change/100)
        c_utility = c_heavy + c_diesel + c_ng + c_elec
        c_onm = 5.44 * 2 # assume a fixed value related to plant size
        c_co2 = self.carbon_tax * t_co2 
        opex = (c_material + c_utility + c_onm + c_co2)*np.ones(5)
        print('opex',opex)

        return {
            'country': country,
            'years': years,

            'co2 heavy oil': co2_heavy_oil,
            'co2 diesel oil': co2_diesel_oil,
            'co2 ng': co2_ng,
            'co2 electricity': co2_electricity,

            'direct co2': t_direct_co2,
            'indirect co2': t_indirect_co2,
            'total co2': t_co2,

            'capex': capex,
            'opex':opex,
        }

    def figures(self, results):
        return [
            {
                'label': 'GHG Emissions by Source',
                'unit': 'tonne CO\u2082 / tonne aluminum',
                'axis': 0,
                'datasets': [
                    {
                        'label': 'Heavy oil',
                        'color': Color(name='darkred'),
                        'data': results['co2 heavy oil'],
                    },
                    {
                        'label': 'Diesel oil',
                        'color': Color(name='brown'),
                        'data': results['co2 diesel oil'],
                    },
                    {
                        'label':'Electricity',
                        'color': Color(name='blueviolet'),
                        'data': results['co2 electricity'],
                    },
                    {
                        'label':'Natural Gas',
                        'color': Color(name='blue'),
                        'data': results['co2 ng'],
                    },

                ]
            },
            {
                'label': 'GHG Emissions by Stage',
                'unit': 'tonne CO\u2082 / tonne aluminum',
                'axis': 0,
                'datasets': [
                    {
                        'label': 'Remelting',
                        'color': Color(name='slateblue'),

                        'data': results['total co2'],
                    },
                ],
            },
            {
                'label': 'Costs',
                'unit': 'USD $ / tonne Aluminum',
                'axis': 0,
                'datasets': [
                    {
                        'label': 'Operating',
                        'color': Color(name='darkslategrey'),
                        'data': results['opex'],
                    },
                    {
                        'label': 'Capital',
                        'color': Color(name='teal'),
                        'data': results['capex'],
                    },
                ],
            },
            {
                'label': 'Total GHG Emissions',
                'unit': 'tonne CO\u2082 / tonne aluminum',
                'axis': 1,
                'datasets': [
                    {
                        'label': 'Total CO\u2082 Emissions',
                        'data': results['total co2'],
                    },
                ],
            },
        ]

    def plot(self, results):
        print(f"co2 electricity: {results['co2 electricity']}")
        country = results['country'].title()
        plot1 = plt.figure(1)
        plt.plot(results['years'], results['co2 heavy oil'], marker='*', label='Heavy oil', color='darkred')
        plt.plot(results['years'], results['co2 diesel oil'], marker='1', label='Diesel oil', color='brown')
        plt.plot(results['years'], results['co2 ng'], marker='s', label='Natural gas', color='blue')
        plt.plot(results['years'], results['co2 electricity'], marker = 'v', label='Electricity', color='blueviolet')
        plt.plot(results['years'], results['total co2'], marker = 'o', label='Total', color='red')
        plt.plot(results['years'], results['capex'], marker = 'o', label='CAPEX ($/tonne Al Ingot)', color='black')
        plt.plot(results['years'], results['opex'], marker = 'o', label='OPEX ($/tonne Al Ingot)', color='green')
      
        #plt.vlines(2020, 0, 20, label='Past/future', color='black', linestyles='dashed')  # plot vertical lines
        plt.xticks(np.arange(min(results['years']),max(results['years'])+1,5))
        plt.title('CO\u2082 emission for remelt routes')
        plt.xlabel('Year')
        plt.ylabel('CO\u2082 emissions (tonne CO\u2082/tonne aluminum)')
        plt.legend()
        plt.show()
