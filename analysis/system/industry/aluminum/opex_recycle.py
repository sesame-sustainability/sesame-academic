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
                'scrap_price', 'Recycled Scrap',
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
                defaults=[Default(0)],
            ),
        
            ContinuousInput(
                'ingot_price', 'Recycled Ingot',
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
                defaults=[Default(0)],
            ),
            ContinuousInput(
                'alloy_price', 'Alloy metal',
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

