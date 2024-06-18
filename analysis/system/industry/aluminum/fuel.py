"""
Emission factos and hhv for fossil fuel. 
source:  https://european-aluminium.eu/media/3321/full-environmental-profile-report-2018.pdf
@author: Lingyan Deng
"""

from core.common import InputSource
import core.conditionals as conditionals
from core.inputs import OptionsInput, ContinuousInput, PercentInput, Default,Tooltip
import core.validators as validators

def fuel():
        return [
            ContinuousInput(
               'c_heavy_oil', 'Heavy oil emission factor',
               defaults=[Default(0.0851)],
               unit = 'kg CO2/MJ',
               validators=[validators.numeric(), validators.gte(0)],
               tooltip=Tooltip('Default Country: EU-27', source='EAI',
                               source_link='https://european-aluminium.eu/media/3321/full-environmental-profile-report-2018.pdf')
           ),
           ContinuousInput(
               'c_ng', 'Natural gas emission factor',
               defaults=[Default(0.0632)],
               unit = 'kg CO2/MJ',
               validators=[validators.numeric(), validators.gte(0)],
               tooltip=Tooltip('Default Country: EU-27', source='EAI',
                               source_link='https://european-aluminium.eu/media/3321/full-environmental-profile-report-2018.pdf')
           ),
           ContinuousInput(
               'c_diesel_oil', 'Diesel oil emission factor',
               defaults=[Default(0.0826)],
               unit = 'kg CO2/MJ',
               validators=[validators.numeric(), validators.gte(0)],
               tooltip=Tooltip('Default Country: EU-27', source='EAI',
                               source_link='https://european-aluminium.eu/media/3321/full-environmental-profile-report-2018.pdf')
           ),
           ContinuousInput(
               'hhv_diesel_oil', 'Diesel oil HHV',
               defaults=[Default(42.9)],
               unit = 'MJ/kg',
               validators=[validators.numeric(), validators.gte(0)],
               tooltip=Tooltip('Default Country: EU-27', source='University of Birmingham',
                               source_link='https://www.claverton-energy.com/wordpress/wp-content/uploads/2012/08/the_energy_and_fuel_data_sheet1.pdf')
           ),
            ContinuousInput(
                'hhv_ng', 'Natural gas HHV',
                defaults=[Default(49.5)],
                unit = 'MJ/kg',
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip('Default Country: EU-27', source='University of Birmingham',
                                source_link='https://www.claverton-energy.com/wordpress/wp-content/uploads/2012/08/the_energy_and_fuel_data_sheet1.pdf')
            ),
            ContinuousInput(
                'hhv_heavy_oil', 'Heavy oil HHV',
                defaults=[Default(43.05)],
                unit = 'MJ/kg',
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip('Default Country: EU-27', source='University of Birmingham',
                                source_link='https://www.claverton-energy.com/wordpress/wp-content/uploads/2012/08/the_energy_and_fuel_data_sheet1.pdf')
            ),
        ]