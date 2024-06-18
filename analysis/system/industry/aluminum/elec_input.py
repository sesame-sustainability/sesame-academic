"""Electricity Input Table for Industries
Formal Separate File Began 2/4/22
sydney johnson
lingyan deng
Captive Power Source:https://cdm.unfccc.int/filestorage/Z/6/H/Z6HFW5FPPRA2BKAUK3CK5XN6EXB98F.1/Kalyani_PDD_28April2006.pdf?t=SWN8cjZ6cmNkfDBVoFiUaj0TOtJw92SytzFm """

import os
import pandas as pd
import numpy as np
from core.common import InputSource
import core.conditionals as conditionals
from core.inputs import OptionsInput, ContinuousInput, Default,Tooltip,InputGroup,ShareTableInput
import core.validators as validators
from analysis.system.industry.iron_steel.linear_elec_projection import linproj
from analysis.system.industry.iron_steel.power_plant import captive_power
from analysis.system.industry.iron_steel.power_plant import captive_power

PATH = os.getcwd() + '/analysis/system/industry/aluminum/'
# COUNTRIES = ['Global', 'EU-27']
ELECTRICITY_DATA = pd.read_csv(PATH + "electricity.csv", index_col = "Year")
base_year, projected_year = [2020, 2040]
SCENARIOS = ['IEA SDS', 'Static']

def electricity_value(country, year):
   return ELECTRICITY_DATA[country][year] * 3600 # UI unit in gCO2/kWh

def ci_defaults_base(COUNTRIES):
   return [
      Default(
         electricity_value(country, base_year),
         conditionals=[conditionals.input_equal_to('country', country)],
      )
      for country in COUNTRIES
   ]

def ci_defaults_projected(COUNTRIES):
   return [
      Default(
         electricity_value(country, projected_year),
         conditionals=[
            conditionals.input_equal_to('country', country),
            conditionals.input_equal_to('elec_source', 'IEA SDS',)
         ],
      )
      for country in COUNTRIES
   ] + [
      Default(
         electricity_value(country, base_year),
         conditionals=[
            conditionals.input_equal_to('country', country),
            conditionals.input_equal_to('elec_source', 'Static'),
         ],
      )
      for country in COUNTRIES
   ]


def user_inputs_ft_cap(cls,COUNTRIES): # if blast furnace, has access to captive power
   return [
      OptionsInput(
         'country', 'The Location of the Plant',
         options=COUNTRIES,  # ['India','China','World','EU-27','Gulf Cooperation Council region','Indonesia'],
         defaults=[Default(COUNTRIES[1])]
      ),

      OptionsInput(
         'elec_source', 'Electricity carbon intensity source',
         options=['IEA SDS', 'User', 'Static','Captive Power Plant'],
         defaults=[Default('IEA SDS')],
         tooltip=Tooltip(
            'IEA SDS = IEA Sustainable Development Scenario',
            source='IEA (2020)',
            source_link='https://www.iea.org/reports/tracking-power-2020',
         ),
      ),
      ShareTableInput(
         'elec_vals', 'Electricity Carbon Intensity (gCO2/kWh)',
         columns=[str(base_year), str(projected_year)],
         rows=[
            ShareTableInput.Row(
               'Enter Value:',
               tooltip=Tooltip(
                  source='IEA (2020)',
                  source_link='https://www.iea.org/reports/tracking-power-2020',
               ),
               cells=[
                  ShareTableInput.Cell(defaults=ci_defaults_base(COUNTRIES)),
                  ShareTableInput.Cell(defaults=ci_defaults_projected(COUNTRIES)),
               ],
            ),
         ],
         on_change_actions=[
            {
               'type': 'set_input_to',
               'target': 'elec_source',
               'value': 'User',
            }
         ],conditionals= [conditionals.input_not_equal_to('elec_source', 'Captive Power Plant')],
      ),
      OptionsInput(
         'cp_fuel', 'Fuel for Captive Plant',
         defaults=[Default('Coal')],
         options=['Coal','Natural Gas','Solar','Wind'],
         conditionals=[conditionals.input_equal_to('elec_source', 'Captive Power Plant')]
      ),
      ContinuousInput(
         'cp_eff', 'Captive Power Plant Efficiency',
         unit='%',
         defaults=[Default(32)],
         validators=[validators.numeric(), validators.gte(0)],
         conditionals=[conditionals.input_equal_to('elec_source', 'Captive Power Plant'),conditionals.input_not_equal_to('cp_fuel', 'Wind')],
      ),
   ]

def co2_int(route, years):
   elec_vals = route.elec_vals
   country = route.country
   elec_source = route.elec_source
   cp_eff = route.cp_eff
   eci_2020 = electricity_value(country, base_year)
   elec_co2 = []

   if elec_source == 'IEA SDS':
      for year in years:
         i_elec_co2 = ELECTRICITY_DATA[country][year] #elec['co2'][20:25]  # Electricity carbon intensity tonne CO2/GJ.
         elec_co2.append(i_elec_co2)
      i_elec_co2 = elec_co2
   elif elec_source == 'User':
      eci_2040 = elec_vals['2040'][0]
      i_elec_co2 = linproj(eci_2020, eci_2040, base_year, projected_year) / np.array(3600)
   elif elec_source == 'Static': # static
      i_elec_co2 = np.ones(len(years)) * eci_2020 / 3600  # calculate on backend in tCO2/GJ
   else: # power plant uses GREET LCA Values for emissions (GHG)
         cp_fuel = route.cp_fuel
         cp_eci = captive_power(cp_fuel,[],cp_eff,country)['cp_em']
         i_elec_co2 = np.ones(len(years))*cp_eci
   return i_elec_co2


    # ContinuousInput(
    #     'eci_2020', '2020 Carbon Intensity',
    #     unit='gCO2/kWh',
    #     defaults=[Default(707)],
    #     validators=[validators.numeric(), validators.gte(0)],
    #     conditionals=[conditionals.input_not_equal_to('elec_source', 'IEA SDS')],
    #     tooltip=Tooltip('Default Country: India', source='IEA (2020)',
    #                     source_link='https://www.iea.org/reports/tracking-power-2020')
    # ),
    # ContinuousInput(
    #     'eci_2040', '2040 Carbon Intensity ',
    #     unit='gCO2/kWh',
    #     defaults=[Default(108, conditionals=[conditionals.input_equal_to('elec_source', 'User')]),
    #               Default(707, conditionals=[conditionals.input_equal_to('elec_source', 'Static')])],
    #     validators=[validators.numeric(), validators.gte(0)],
    #     conditionals=[conditionals.input_not_equal_to('elec_source', 'IEA SDS')],
    #     tooltip=Tooltip('Default Country: India for IEA SDS', source='IEA (2020)')
    # )]


   # def captive_power_plant():
   #    f_oil = 129339/(1.64*10**6) #kL/yr divided by tonne hot metal production / yr
   #    oil_em_f = 3 # value
   #    emi = f_oil*oil_em_f
   #    cpp_data = {"emissions": emi}
   #    return cpp_data
