"""
Functional unit: 1 tonne of aluminum
starting from old scrap

1. https://legacy-assets.eenews.net/open_files/assets/2014/01/11/document_cw_01.pdf (North America)
2.Joint Research Centre, Institute for Energy and Transport, Slingerland, S., Gancheva, M., Visschedijk, A., et al., Energy efficiency and GHG emissions : prospective scenarios for the aluminium industry, Publications Office, 2015, https://data.europa.eu/doi/10.2790/9500
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from core.inputs import Tooltip
from core.common import InputSource,Color
import core.conditionals as conditionals
from core.inputs import OptionsInput, ContinuousInput, PercentInput, Default, InputGroup
import core.validators as validators
from analysis.system.industry.cement.elec_input import user_inputs_ft_cap,co2_int
from analysis.system.industry.aluminum.project_elec_co2 import elec_co2
from analysis.system.industry.aluminum.capex import capexs
from analysis.system.industry.aluminum.cepci import cepci_v
from analysis.system.industry.aluminum.ppp import pppv
from analysis.system.industry.aluminum.exchange_rate import exchange_country
from analysis.system.industry.aluminum.opex_recycle import opex_input


class RECYCLEALUMINUM(InputSource):

    @classmethod
    def user_inputs(cls):
        countries = ['United States']
        elec_default = [Default('United States')]

        return user_inputs_ft_cap(cls,countries) + [
            # OptionsInput(
            #     'country', 'The location of the plant',
            #     defaults = [Default('United States')],
            #     options = ['United States'],# ['India','China','World','EU-27','Gulf Cooperation Council region','Indonesia']
            #     tooltip = Tooltip('Country informs data, such as IEA 2020 Grid Intensity ')
            # ),
            InputGroup('prep_scrap', 'Scrap Preparation', children=[
                ContinuousInput(
                    'pro_scrap', 'Mass of Preprocessed (Old) Scrap Required for Prepping',
                    defaults=[Default(1.05)],
                    validators=[validators.numeric(), validators.gte(0)],
                ),
                ContinuousInput(
                    'prep_elec_req', 'Electricity for Prepping Scrap ',
                    defaults=[Default(110.32)],
                    validators=[validators.numeric(), validators.gte(0)],
                    unit='kWh',
                    tooltip=Tooltip('Includes separation, sorting, and cleaning for scrap before melting',
                                    source='Aluminum Association',
                                    source_link='https://legacy-assets.eenews.net/open_files/assets/2014/01/11/document_cw_01.pdf'),
                ),
                ContinuousInput(
                    'prep_ng_req', 'Natural Gas for Prepping Scrap',
                    defaults=[Default(0.90)],
                    validators=[validators.numeric(), validators.gte(0)],
                    unit='GJ',
                    tooltip=Tooltip('Includes separation, sorting, and cleaning for scrap before melting',source='Aluminum Association',
                                    source_link='https://legacy-assets.eenews.net/open_files/assets/2014/01/11/document_cw_01.pdf'),
                )
                       ]


            ),
            InputGroup('melt_cast', 'Scrap Melting & Casting', children=[
                ContinuousInput(
                    'mc_scrap', 'Mass of Processed Scrap Required for Melting',
                    defaults=[Default(1.05)],
                    validators=[validators.numeric(), validators.gte(0)],
                ),
                ContinuousInput(
                    'melt_elec_req', 'Electricity for Melting and Casting',
                    defaults=[Default(115.25)],
                    validators=[validators.numeric(), validators.gte(0)],
                    unit='kWh',
                    tooltip=Tooltip(source='Aluminum Association',
                                    source_link='https://legacy-assets.eenews.net/open_files/assets/2014/01/11/document_cw_01.pdf'),
                ),
                ContinuousInput(
                    'melt_ng_req', 'Natural Gas for Melting and Casting',
                    defaults=[Default(4.78)],
                    validators=[validators.numeric(), validators.gte(0)],
                    unit='GJ',
                    tooltip = Tooltip(source='Aluminum Association',source_link='https://legacy-assets.eenews.net/open_files/assets/2014/01/11/document_cw_01.pdf'),
            )
                ]
                       ),
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
        m_aluminum = pd.Series([1, 1, 1, 1, 1])  # 1 tonne of aluminum
        #electricity source
        years = elec_co2(country)['years'][20:25]
        c_electricity = co2_int(self, years)
        # print(c_electricity)

        #SCRAP MELTING / INGOT CASTING
        mc_scrap = self.mc_scrap*np.ones(5)
        #if adding Al primary
        mc_scrap_th = 0.967592 #tonnes
        melt_cast_alloys = 0.0145028/mc_scrap_th*mc_scrap
        melt_cast_prim_alm = 0.06542/mc_scrap_th*mc_scrap  # tonnes

        #if only scrap
        mc_scrap_th = 1048*10**-3 # tonnes
        melt_cast_elec = self.melt_elec_req/mc_scrap_th/277.778*mc_scrap#GJ
        melt_cast_ng = self.melt_ng_req/ mc_scrap_th*mc_scrap #GJ from ng
        # # melt_eff = self.furn_eff
        # print(melt_cast_ng)
        # print(melt_cast_elec)

        # SCRAP PROCESSING ( may include shipping/handling, separatoin, agglomeration, cleaning,recovery/handlnig, treatment), more_
        m_th_scrap = 1.048  # tonnes  #old scrap required
        m_us_scrap = self.pro_scrap # user input for pre processed scrap
        m_scrap = np.ones(5) * self.mc_scrap*m_us_scrap
        m_water = 1.4978 * 10 ** -3 / m_th_scrap * m_scrap  # tonnes
        proc_elec = self.prep_elec_req / m_th_scrap * m_scrap / 277.778  # GJ per tonne of scrap
        proc_ng = self.prep_ng_req / m_th_scrap * m_scrap  # GJ
        # print(proc_ng)
        # print(proc_elec)
        # add waste generated

        #co2 by stage
        co2_pro_elec = proc_elec*np.array(c_electricity)
        co2_pro_ng = proc_ng*np.ones(5)*0.0566# emission factor per GJ is 0.0566 tCO2/GJ of nat gas


        co2_cast_elec = melt_cast_elec*np.array(c_electricity)
        co2_cast_ng = melt_cast_ng*np.ones(5)*0.0566
        co2_pro = co2_pro_elec + co2_pro_ng
        co2_cast = co2_cast_ng + co2_cast_elec

        #co2 by source
        co2_ng = co2_pro_ng + co2_cast_ng
        co2_elec = co2_pro_elec + co2_cast_elec
        # print(co2_ng)
        # print(co2_elec)
        t_co2 = co2_pro + co2_cast
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
        c_material = m_scrap * self.scrap_price * (1 + self.scrap_price_change/100)
        c_ng = (melt_cast_ng + proc_ng) * (1 + self.ng_price_change/100)
        c_elec = (melt_cast_elec + proc_elec) * (1 + self.elec_price_change/100)
        c_utility = c_ng + c_elec
        c_onm = 5.44 * 2 # assume a fixed value related to plant size
        c_co2 = self.carbon_tax * t_co2 
        opex = (c_material + c_utility + c_onm + c_co2)*np.ones(5)
        print('opex',opex)
        results = {
            't_co2':t_co2,
            'co2_pro':co2_pro,
            'co2_cast':co2_cast,
            'co2_ng':co2_ng,
            'co2_elec':co2_elec,

            'capex': capex,
            'c_material':c_material,
            'c_utility': c_utility,
            'c_onm':c_onm,
            'carbon_tax': c_co2,
            'opex':opex,
    }
        return results

    def figures(self, results):
            return [
                {
                    'label': 'GHG Emissions by Source',
                    'unit': 'tonne CO\u2082 / tonne aluminum',
                    'axis': 0,
                    'datasets': [
                        {
                            'label': 'Electricity',
                            'color': Color(name='blueviolet'),
                            'data': results['co2_elec'],
                        },
                        {
                            'label': 'Natural Gas',
                            'color': Color(name='blue'),
                            'data': results['co2_ng'],
                        },

                    ]
                },
                {
                    'label': 'GHG Emissions by Stage',
                    'unit': 'tonne CO\u2082 / tonne aluminum',
                    'axis': 0,
                    'datasets': [
                        {
                            'label': 'Scrap Preparation',
                            'color': Color(name='slateblue'),
                            'data': results['co2_pro'],
                        },
                        {
                            'label': 'Melting and Casting',
                            'color': Color(name='grey'),
                            'data': results['co2_cast'],
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
                            'data': results['t_co2'],
                        },
                    ],
                },
            ]
    def plot (self,results):
        return[]