"""
Calculate operation cost. including: material cost, operation & management cost
"""
import numpy as np
import os
import pandas as pd

from core.common import InputSource
import core.conditionals as conditionals
from core.inputs import OptionsInput, ContinuousInput, Default,Tooltip,InputGroup,ShareTableInput
import core.validators as validators


def opex_input(cls):
    return [
        InputGroup('prices','2020 Fuel & Material Prices', children = [
            ContinuousInput(
                'bauxite_price', 'Bauxite',
                conditionals=[conditionals.input_equal_to('route', 'Primary Aluminum')],
                unit='$/tonne',
                defaults=[Default(10)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='IBM',
                    source_link='https://ibm.gov.in/writereaddata/files/10012020172018Bauxite_2019_AR.pdf')
            ),
            ContinuousInput(
                'bauxite_price_change', '% change in bauxite price, 2020-2040',
                conditionals=[conditionals.input_equal_to('route', 'Primary Aluminum')],
                defaults=[Default(0)],
            ),
            ContinuousInput(
                'anode_price', 'Anode',
                conditionals=[conditionals.input_equal_to('route', 'Primary Aluminum')],
                unit='$/tonne',
                defaults=[Default(50)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='Springer',
                    source_link='https://link.springer.com/content/pdf/10.1007/s11837-001-0209-2.pdf')
            ),
            ContinuousInput(
                'anode_price_change', '% change in anode price, 2020-2040',
                conditionals=[conditionals.input_equal_to('route', 'Primary Aluminum')],
                defaults=[Default(0)],
            ),
            ContinuousInput(
                'naoh_price', 'NaOH',
                conditionals=[conditionals.input_equal_to('route', 'Primary Aluminum')],
                unit='$/tonne',
                defaults=[Default(2249)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='Bulk Apothecary',
                    source_link='https://www.bulkapothecary.com/raw-ingredients/other-ingredients-and-chemicals/sodium-hydroxide-lye/?sku=RAW%20BAY-chem-69')
            ),
            ContinuousInput(
                'naoh_price_change', '% change in NaOH price, 2020-2040',
                conditionals=[conditionals.input_equal_to('route', 'Primary Aluminum')],
                defaults=[Default(0)],
            ),
            ContinuousInput(
                'cao_price', 'CaO',
                conditionals=[conditionals.input_equal_to('route', 'Primary Aluminum')],
                unit='$/tonne',
                defaults=[Default(86)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='Indiamart',
                    source_link='https://dir.indiamart.com/impcat/calcium-oxide.html')
            ),
            ContinuousInput(
                'cao_price_change', '% change in CaO price, 2020-2040',
                conditionals=[conditionals.input_equal_to('route', 'Primary Aluminum')],
                defaults=[Default(0)],
            ),
            ContinuousInput(
                'alf3_price', 'AlF3',
                conditionals=[conditionals.input_equal_to('route', 'Primary Aluminum')],
                unit='$/tonne',
                defaults=[Default(945)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='Indiamart',
                    source_link='https://www.indiamart.com/proddetail/white-aluminium-fluoride-powder-24046876533.html')
            ),
            ContinuousInput(
                'alf3_price_change', '% change in AlF3 price, 2020-2040',
                conditionals=[conditionals.input_equal_to('route', 'Primary Aluminum')],
                defaults=[Default(0)],
            ),
            ContinuousInput(
                'scrap_price', 'Recycled Scrap',
                conditionals=[conditionals.input_equal_to('route', 'Recycle Aluminum')],
                unit='$/tonne',
                defaults=[Default(1543)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='Mid City Scrap',
                    source_link='https://midcityscrap.com/public-scrap-metal-prices/')
            ),
            ContinuousInput(
                'scrap_price_change', '% change in recycled scrap price, 2020-2040',
                conditionals=[conditionals.input_equal_to('route', 'Recycle Aluminum')],
                defaults=[Default(0)],
            ),
            ContinuousInput(
                'ingot_price', 'Recycled Ingot',
                conditionals=[conditionals.input_equal_to('route', 'Remelt Aluminum')],
                unit='$/tonne',
                defaults=[Default(2838)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='LME',
                    source_link='https://www.lme.com/en/Metals/Non-ferrous/LME-Aluminium#Trading+day+summary')
            ),
            ContinuousInput(
                'ingot_price_change', '% change in recycled ingot price, 2020-2040',
                conditionals=[conditionals.input_equal_to('route', 'Remelt Aluminum')],
                defaults=[Default(0)],
            ),
            ContinuousInput(
                'ingot_price', 'Recycled Ingot',
                conditionals=[conditionals.input_equal_to('route', 'Recycle Aluminum')],
                unit='$/tonne',
                defaults=[Default(2838)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='LME',
                    source_link='https://www.lme.com/en/Metals/Non-ferrous/LME-Aluminium#Trading+day+summary')
            ),
            ContinuousInput(
                'ingot_price_change', '% change in recycled ingot price, 2020-2040',
                conditionals=[conditionals.input_equal_to('route', 'Recycle Aluminum')],
                defaults=[Default(0)],
            ),
            ContinuousInput(
                'alloy_price', 'Alloy metal',
                conditionals=[conditionals.input_equal_to('route', 'Recycle Aluminum')],
                unit='$/tonne',
                defaults=[Default(5644)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='Statista',
                    source_link='https://www.statista.com/statistics/301564/us-silicon-price-by-type/#:~:text=In%202021%2C%20the%20average%20price,140%20U.S.%20cents%20per%20pound.')
            ),
            ContinuousInput(
                'alloy_price_change', '% change in alloy metal price, 2020-2040',
                conditionals=[conditionals.input_equal_to('route', 'Recycle Aluminum')],
                defaults=[Default(0)],
            ),
            ContinuousInput(
                'heavy_price', 'Heavy oil',
                conditionals=[conditionals.input_not_equal_to('route', 'Recycle Aluminum')],
                unit='$/tonne',
                defaults=[Default(1575)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='Bank Bazaar',
                    source_link='https://www.bankbazaar.com/fuel-price-india.html')
            ),
            ContinuousInput(
                'heavy_price_change', '% change in heavy oil price, 2020-2040',
                conditionals=[conditionals.input_not_equal_to('route', 'Recycle Aluminum')],
                defaults=[Default(0)],
            ),
            ContinuousInput(
                'diesel_price', 'Diesel oil',
                conditionals=[conditionals.input_not_equal_to('route', 'Recycle Aluminum')],
                unit='$/tonne',
                defaults=[Default(1486)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='Bank bazaar',
                    source_link='https://www.bankbazaar.com/fuel-price-india.html')
            ),
            ContinuousInput(
                'diesel_price_change', '% change in diesel oil price, 2020-2040',
                conditionals=[conditionals.input_not_equal_to('route', 'Recycle Aluminum')],
                defaults=[Default(0)],
            ),
            ContinuousInput(
                'vlso_price', 'VLSFO',
                conditionals=[conditionals.input_not_equal_to('route', 'Recycle Aluminum')],
                unit='$/tonne',
                defaults=[Default(334)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to  Asia in 2020. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='OPIS',
                    source_link='http://blog.opisnet.com/hubfs/OPIS-Global-Marine-Fuels-Report_20201001.pdf')
            ),
            ContinuousInput(
                'vlso_price_change', '% change in VLSFO price, 2020-2040',
                conditionals=[conditionals.input_not_equal_to('route', 'Recycle Aluminum')],
                defaults=[Default(0)],
            ),
             ContinuousInput(
                'ng_price', 'Natural gas',
                unit='$/GJ',
                defaults=[Default(4)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='Ministry of Petroleum & Natural Gas, Gov of India',
                    source_link='https://www.ppac.gov.in/WriteReadData/CMS/202009300542060502504GasPriceCeilingOct2020toMarch2021.pdf')
            ),
            ContinuousInput(
                'ng_price_change', '% change in natural gas price, 2020-2040',
                defaults=[Default(0)],
            ),
            ContinuousInput(
                'elec_price', 'Electricity',
                unit='$/GJ',
                defaults=[Default(11)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='India Stat',
                    source_link='https://www.indiastat.com/table/utility-wise-average-rates-of-electricity-supply-and-electricity-duty-tax/month-wise-average-price-volume-electricity-transa/1414631')
            ),
            ContinuousInput(
                'elec_price_change', '% change in electricity price, 2020-2040',
                defaults=[Default(0)],
            ),
            ContinuousInput(
                    'carbon_tax', 'Carbon tax',
                    unit = '$/tonne',
                    defaults=[Default(50)],
                    validators=[validators.numeric(), validators.gte(0)],
                ),

        ])
    ]

