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
                'heavy_price', 'Heavy oil',
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
                defaults=[Default(0)],
            ),
            ContinuousInput(
                'diesel_price', 'Diesel oil',
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

