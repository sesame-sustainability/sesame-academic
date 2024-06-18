"""Electricity Input Table for Industries
Formal Separate File Began 2/4/22
sydney johnson

Captive Power Source:https://cdm.unfccc.int/filestorage/Z/6/H/Z6HFW5FPPRA2BKAUK3CK5XN6EXB98F.1/Kalyani_PDD_28April2006.pdf?t=SWN8cjZ6cmNkfDBVoFiUaj0TOtJw92SytzFm """

import os
import pandas as pd
import numpy as np
from core.common import InputSource
import core.conditionals as conditionals
from core.inputs import OptionsInput, ContinuousInput, Default,Tooltip,InputGroup,ShareTableInput
import core.validators as validators
from analysis.system.industry.cement.linear_elec_projection import linproj
from analysis.system.industry.iron_steel.power_plant import captive_power

PATH = os.getcwd() + '/analysis/system/industry/cement/'
# COUNTRIES = ['India', 'China', 'United_States', 'EU_27']

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
         'country', 'Location of plant',
         defaults=[Default(COUNTRIES[0])],
         options=COUNTRIES
      ),
      InputGroup('elec_options', 'Electricity Inputs', children=[
         OptionsInput(
            'elec_source', 'Electricity carbon intensity source',
            options=['IEA SDS', 'User', 'Static','Captive Power Plant','Mix (Captive + Grid)'],
            defaults=[Default('IEA SDS')],
            tooltip=Tooltip(
               'IEA SDS = IEA Sustainable Development Scenario Grid Intensity for Main Grid, User = define grid intensity for 2040, Static = constant grid intensity, Captive Power Plant = Onsite Source of Electricity, Mix = combination of grid and onsite electricity',
               source='IEA (2020)',
               source_link='https://www.iea.org/reports/tracking-power-2020',
            ),
         ),
         OptionsInput(
            'grid_source', 'Grid Electricity Source',
            options=['IEA SDS', 'User', 'Static'],
            defaults=[Default('IEA SDS')],
            tooltip=Tooltip(
               'IEA SDS = IEA Sustainable Development Scenario Grid Intensity for Main Grid, User = define grid intensity for 2040, Static = constant grid intensity',
               source='IEA (2020)',
               source_link='https://www.iea.org/reports/tracking-power-2020',
            ),
            conditionals=[conditionals.input_equal_to('elec_source', 'Mix (Captive + Grid)')],
         ),
         ContinuousInput(
            'elec_split', 'Percent Electricity from Grid',
            unit='%',
            defaults=[Default(50)],# arbitrary
            validators=[validators.numeric(), validators.gte(0),validators.lte(100)],
            conditionals=[conditionals.input_equal_to('elec_source', 'Mix (Captive + Grid)')],
            tooltip=Tooltip(
               'Percent of electricity from main grid versus onsite production'
            ),
         ),
         ShareTableInput( # for if the choice is not captive power
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
            ],conditionals= [conditionals.input_not_equal_to('elec_source', 'Captive Power Plant'),conditionals.input_not_equal_to('elec_source', 'Mix (Captive + Grid)')],
         ),
         ShareTableInput( # for if the choice is mix
            'elec_vals_mix', 'Electricity Carbon Intensity (gCO2/kWh)',
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
                  'target': 'grid_source',
                  'value': 'User',
               }
            ], conditionals=[conditionals.input_equal_to('elec_source', 'Mix (Captive + Grid)')],
         ),
         OptionsInput(
            'cp_fuel', 'Fuel for Captive Plant',
            defaults=[Default('Coal')],
            options=['Coal', 'Natural Gas', 'Solar', 'Wind'],
            conditionals=[conditionals.input_not_equal_to('elec_source', 'IEA SDS'),conditionals.input_not_equal_to('elec_source', 'User'),conditionals.input_not_equal_to('elec_source', 'Static')],
         ),
         ContinuousInput(
            'cp_eff', 'Captive Power Plant Efficiency',
            unit='%',
            defaults=[
               Default(35, conditionals=[conditionals.input_equal_to('cp_fuel', 'Coal')]), # https://www.nsenergybusiness.com/features/coal-power-india-emissions/
               Default(50, conditionals=[conditionals.input_equal_to('cp_fuel', 'Natural Gas')]), #SESAME
               Default(20,conditionals=[conditionals.input_equal_to('cp_fuel','Solar')]), #SESAME
               ],
            validators=[validators.numeric(), validators.gte(0)],
            conditionals=[conditionals.input_not_equal_to('elec_source', 'IEA SDS'),
                          conditionals.input_not_equal_to('elec_source', 'User'),
                          conditionals.input_not_equal_to('elec_source', 'Static')],
         ),
      ]
   )
   ]




def co2_int(route, years):

   elec_vals = route.elec_vals
   country = route.country
   elec_source = route.elec_source
   cp_fuel = route.cp_fuel
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
      i_elec_co2 = np.ones(5) * eci_2020 / 3600  # calculate on backend in tCO2/GJ

   elif elec_source == 'Captive Power Plant':
      cp_eci = captive_power(cp_fuel, [], cp_eff, country)['cp_em']
      i_elec_co2 = np.ones(len(years)) * cp_eci

   elif elec_source == 'Mix (Captive + Grid)':
      grid_source = route.grid_source
      if grid_source == 'IEA SDS':
         for year in years:
            iea_elec_co2 = ELECTRICITY_DATA[country][year]  # elec['co2'][20:25]  # Electricity carbon intensity tonne CO2/GJ.
            elec_co2.append(iea_elec_co2)
         grid_elec_co2 = elec_co2
      elif grid_source == 'User':
         eci_2040 = elec_vals['2040'][0]
         grid_elec_co2 = linproj(eci_2020, eci_2040, base_year, projected_year) / np.array(3600)
      elif grid_source == 'Static':
         grid_elec_co2 = np.ones(5) * eci_2020 / 3600  # calculate on backend in tCO2/GJ

      #Grid Elec
      grid_perc = route.elec_split/100
      print(grid_elec_co2)

      #Captive Power
      cp_eci = captive_power(cp_fuel, [], cp_eff, country)['cp_em']
      cp_elec_co2 = np.ones(len(years)) * cp_eci
      print(cp_elec_co2)


      i_elec_co2 = cp_elec_co2*np.array((1-grid_perc)) + grid_elec_co2*np.array(grid_perc)
      print(i_elec_co2)

   else: #  uses IEA by default
      for year in years:
         i_elec_co2 = ELECTRICITY_DATA[country][year]  # elec['co2'][20:25]  # Electricity carbon intensity tonne CO2/GJ.
         elec_co2.append(i_elec_co2)
   return i_elec_co2

