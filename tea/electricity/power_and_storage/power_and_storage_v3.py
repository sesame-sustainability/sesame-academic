"""
Author: Seiji Engelkemier
Created: June 6, 2021

Purpose: Estimate LCOE of electricity supplied by intermittent renewable with storage
"""

import os
import pandas as pd

from core.tea import TeaBase
from core import conditionals, validators
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Option, InputSet
import numpy as np
import core.conditionals as conditionals
# from core.utils import load_class
from core.tea import TeaAnalysis, TeaBase, ComposedAnalysis
import analysis.tea as tea_analysis

from tea.electricity.LCOE import LCOE
from tea.electricity.wind_old.wind_tea import WindTEA
from tea.electricity.solar.solar_TEA_PS import SolarTEA
from tea.electricity.storage.Storage_v3 import StorageTEA


PATH = os.getcwd() + "/tea/electricity/power_and_storage"
PATH_storage = os.getcwd() + "/tea/electricity/storage/data/"

PATH_tes_data = os.path.join(PATH_storage,'TES_data_kW.csv')
PATH_caes_data = os.path.join(PATH_storage,'compressed_air_costs.csv')
PATH_lib_data = os.path.join(PATH_storage,'Li-ion_data_kW.csv')

# Redefine WindTEA class to set capacity factor from StorageCombination
class WindTEA_PS(WindTEA):
    def set_capacity_factor(self,cf):
        self.cf = cf
        return None

    def get_wind_lcoe(self):
        cap_fac = self.cf
        cap_reg_mult = self.get_cap_reg_mult()
        cost_values = self.get_other_costs()
        finance_values = self.get_finance_values()

        lifetime = 30
        grid_cost = 0
        fuel_cost = 0

        wind_lcoe = LCOE(cap_fac, cap_reg_mult, cost_values['OCC'], cost_values['FOM'], cost_values['VOM'], finance_values, lifetime, grid_cost, fuel_cost)
        return wind_lcoe, cap_fac

# For SolarTEA, modifications made in solar_TEA_PS.py

class StorageCombination(TeaBase):
    unit = '$/MWh'

    @classmethod
    def user_inputs(cls):
        return [
            OptionsInput(
                'generation_type','Generator',
                defaults=[Default('wind')],
                options=['wind', 'solar'],
            ),
            OptionsInput(
                'generation_option', 'Generator location',
                defaults=[
                    Default('TX_onshore', conditionals=[conditionals.input_equal_to('generation_type', 'wind')]),
                    Default('Tuscon', conditionals=[conditionals.input_equal_to('generation_type', 'solar')]),
                ],
                options=[
                    Option('MA_offshore', conditionals=[conditionals.input_equal_to('generation_type', 'wind')]),
                    Option('TX_onshore', conditionals=[conditionals.input_equal_to('generation_type', 'wind')]),
                    Option('Tuscon', conditionals=[conditionals.input_equal_to('generation_type', 'solar')]),
                    Option('Boston', conditionals=[conditionals.input_equal_to('generation_type', 'solar')]),
                ],
            ),
            OptionsInput(
                'storage_type', 'Storage',
                defaults=[Default('Li-ion battery')],
                options=['Li-ion battery', 'Thermal', 'Compressed Air'],
            ),

            OptionsInput(
                'cost_source_ss', 'Select Data Source for Technology Costs',
                defaults=[
                    Default('MIT - 2020 estimate', conditionals=[conditionals.input_equal_to('storage_type', 'Li-ion battery')]),
                    Default('MIT - 2050 estimate', conditionals=[conditionals.input_equal_to('storage_type', 'Thermal')]),
                    Default('MIT estimate', conditionals=[conditionals.input_equal_to('storage_type', 'Compressed Air')]),
                ],
                options=[
                    Option('MIT - 2020 estimate', conditionals=[conditionals.input_equal_to('storage_type', 'Li-ion battery')]),
                    Option('MIT - 2050 estimate', conditionals=[conditionals.input_equal_to('storage_type', 'Thermal')]),
                    Option('MIT estimate', conditionals=[conditionals.input_equal_to('storage_type', 'Compressed Air')]),
                ],
            ),
            OptionsInput(
                'cost_scenario', 'Select Cost Scenario',
                defaults=[
                    Default('Today', conditionals=[conditionals.input_equal_to('storage_type', 'Li-ion battery')]),
                    Default('Moderate', conditionals=[conditionals.input_equal_to('storage_type', 'Thermal')]),
                    Default(2020, conditionals=[conditionals.input_equal_to('storage_type', 'Compressed Air')]),
                ],
                options=[
                    Option('Today', conditionals=[conditionals.input_equal_to('storage_type', 'Li-ion battery')]),
                    Option('High', conditionals=[conditionals.input_equal_to('storage_type', 'Thermal')]),
                    Option('Moderate', conditionals=[conditionals.input_equal_to('storage_type', 'Thermal')]),
                    Option('Low', conditionals=[conditionals.input_equal_to('storage_type', 'Thermal')]),
                    Option(2020, conditionals=[conditionals.input_equal_to('storage_type', 'Compressed Air')]),
                    Option(2050, conditionals=[conditionals.input_equal_to('storage_type', 'Compressed Air')]),
                ],
            ),
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.psm_df = pd.read_csv(os.path.join(PATH, "compiled_results.csv"))

        self.wind = WindTEA_PS()
        self.solar = SolarTEA()
        self.storage_obj = StorageTEA()
        # self.generator_obj is set later because it's dependent on user input

    # Read from csv file for specific storage technology
    def read_storage_data(self, df, scenario, var):
        col_vars = 'Variable'
        col_scenario = 'Cost Scenario'
        col_value = 'Value'
        val = df.loc[(df[col_vars] == var) & (df[col_scenario] == scenario)][col_value].item()
        return val

    # Read from compiled_results.csv
    def read_psm_data(self, list_cols, df=None):
        """
        return value of each var_name (str) in list_cols
        """
        # If user passes in single string instead of list
        list_cols = list(list_cols) if isinstance(list_cols, str) else list_cols

        gen = self.generation_type
        gen_opt = self.generation_option
        sto = self.storage_type
        sto_opt = str(self.cost_scenario)
        if df is None:
            df = self.psm_df
        idx = df.index[(df['Gen']==gen) & (df['Gen_opt']==gen_opt) & (df['Storage']==sto) & (df['Storage_opt']==sto_opt)]

        values = []
        for col_name in list_cols:
            values.append(df.loc[df.index[idx],col_name].item())
        values = values[0] if len(values) == 1 else values
        return values

    # Use data from PSM outputs and storage data
    def generate_TEA_inputs(self,df=None):
        """
        Returns dicts that can be used set values for user inputs of generator or storage TEA

        Reads from table of power system outputs
        Reads from storage TEA's csv file
        """
        if df is None:
            df = self.psm_df

        # Find index corresponding to case
        gen = self.generation_type
        # gen_opt = self.generation_option
        sto = self.storage_type
        sto_opt = self.cost_scenario
        # If sto_opt is an int, convert to string. Required because of how the sto_opt gets treated in the csv file vs. elsewhere in SESAME
        # sto_opt_temp = sto_opt if type(sto_opt)!=int else str(sto_opt)
        # idx = df.index[(df['Gen']==gen) & (df['Gen_opt']==gen_opt) & (df['Storage']==sto) & (df['Storage_opt']==sto_opt_temp)]

        # Get values
        col_names = ['Stor_EndEnergyCap','Stor_EndChargeCap','Stor_EndCap','Sto_cycles']
        E_capacity, P_c, P_d, cycles = self.read_psm_data(col_names)

        # Select storage cost file
        if sto == 'Thermal':
            path_storage_data = PATH_tes_data
        elif sto == 'Li-ion battery':
            path_storage_data = PATH_lib_data
        elif sto == 'Compressed Air':
            path_storage_data = PATH_caes_data
        sto_cost_df = pd.read_csv(path_storage_data)

        eta_c = self.read_storage_data(sto_cost_df, sto_opt, 'Efficiency up')
        eta_d = self.read_storage_data(sto_cost_df, sto_opt, 'Efficiency down')
        sto_lifetime = self.read_storage_data(sto_cost_df, sto_opt, 'Capital Recovery Period')

        # Do calculations
        # For storage types where GenX assumes P_c = P_d
        if P_c == 0:
            P_c = P_d
        # E has units of electricity. Convert to units of thermal, chemical, etc.
        t_c = (E_capacity/eta_d)/(P_c*eta_c)
        t_d = E_capacity/P_d

        # Save results to dicts
        # key = user input's variable name
        # value = user input's value
        # power_dict gets passed to generator TEA
        generator_inputs = {}
        generator_inputs['capacity_factor'] = self.read_psm_data(['Gen_CF'])
        if gen == 'wind':
            generator_inputs['group_by'] = 'State'
            if self.generation_option == 'MA_offshore':
                generator_inputs['install_type'] = 'offshore'
                generator_inputs['region'] = 'Massachusetts'
            elif self.generation_option == 'TX_onshore':
                generator_inputs['install_type'] = 'onshore'
                generator_inputs['region'] = 'Texas'
            generator_inputs['cost_source'] = 'NREL'
            generator_inputs['finance_source'] = 'EIA'
            generator_inputs['tax_credit'] = 0
        elif gen == 'solar':
            generator_inputs['finance_source'] = 'EIA'
            # city dict matches name of city in compiled_results.csv to solar_TEA.py
            city = {'Boston':'US NE (Boston)','Tuscon':'US SW (Tucson)'}
            generator_inputs['cell'] = 'multi crystal Si'
            generator_inputs['location'] = 'Utility'
            generator_inputs['size'] = 10
            generator_inputs['tilt'] = '1-axis'
            generator_inputs['city'] = city[self.generation_option]
            generator_inputs['shading'] = 2.5
            generator_inputs['lifetime'] = 30
            generator_inputs['efficiency'] = 18
            generator_inputs['degradation'] = 0.8
            generator_inputs['ILR'] = 1.3

        # storage_dict gets passed to storage TEA
        storage_dict = {}
        storage_dict['storage_tech'] = sto
        storage_dict['duration_charge'] = t_c
        storage_dict['duration_discharge'] = t_d
        storage_dict['cycles'] = cycles
        storage_dict['lifetime_ss'] = sto_lifetime
        storage_dict['user_defined'] = 'Literature'
        storage_dict['cost_source_ss'] = self.cost_source_ss
        storage_dict['cost_scenario'] = self.cost_scenario
        storage_dict['finance_source_ss'] = 'EIA' # 'ATB'

        return generator_inputs, storage_dict

    def get_cost_breakdown(self):
        # Dictionary of user inputs
        gen_dict, storage_dict = self.generate_TEA_inputs()

        # Set user inputs for generator object
        if self.generation_type == 'wind':
            self.wind.prepare(InputSet(WindTEA.user_inputs(), gen_dict))
            self.wind.set_capacity_factor(gen_dict['capacity_factor'])
            self.generator_obj = self.wind
        elif self.generation_type == 'solar':
            self.solar.prepare(InputSet(SolarTEA.user_inputs(), gen_dict))
            self.solar.set_capacity_factor(gen_dict['capacity_factor'])
            self.generator_obj = self.solar

        # Set user inputs for storage object
        self.storage_obj.prepare(InputSet(StorageTEA.user_inputs(power_storage=True), storage_dict))

        # Get cost breakdown
        cost_breakdown_gen = self.generator_obj.get_cost_breakdown()
        cost_breakdown_storage = self.storage_obj.get_cost_breakdown()

        # Some TEA's like WindTEA have component-level breakdown of capital and fixed costs
        # Compute sum of component costs
        if type(cost_breakdown_gen["Capital and Fixed"]) is dict:
            # Replace nan values with 0
            cost_breakdown_gen["Capital and Fixed"] = {k: v if not np.isnan(v) else 0 for k, v in
                                                        cost_breakdown_gen["Capital and Fixed"].items()}
            cost_breakdown_gen["Capital and Fixed"] = sum(cost_breakdown_gen["Capital and Fixed"].values())

        # Weightings to apply to LCOE and LCOS
        kWh_re, kWh_sto = self.read_psm_data(['E_supplied_gen','E_supplied_sto'])

        cost_breakdown_joint = {}
        cost_breakdown_joint["Capital and Fixed"] = {
            'Generation': kWh_re * cost_breakdown_gen["Capital and Fixed"],
            'Storage': kWh_sto * cost_breakdown_storage["Capital and Fixed"]
        }
        cost_breakdown_joint["Operational"] = {
            'Generation': kWh_re * cost_breakdown_gen["Operational"],
            'Storage': kWh_sto *cost_breakdown_storage["Operational"]
        }
        cost_breakdown_joint["Maintenance"] = {
            'Generation': kWh_re * cost_breakdown_gen["Maintenance"],
            'Storage': kWh_sto *cost_breakdown_storage["Maintenance"]
        }

        return cost_breakdown_joint

    def get_table(self):
        col_names = ['Gen_EndCap','Stor_EndEnergyCap','Stor_EndChargeCap','Stor_EndCap','E_supplied_gen','E_supplied_sto','Curtailment_pct']
        P_gen, E_sto_capacity, P_c, P_d, kWh_re, kWh_sto, Curtailment_pct = self.read_psm_data(col_names)


        # ( Some of this repeats code in generate_TEA_inputs() )
        # For storage technologies where P_c = P_d, but GenX records P_c = 0
        if P_c == 0:
            P_c = P_d

        # Adjust by efficiencies
        eta_c, eta_d = self.storage_obj.get_eta()
        t_c = (E_sto_capacity / eta_d)/(P_c * eta_c)
        t_d = E_sto_capacity/P_d

        # Formatting
        n_digits = 2

        # Each tuple: (item name, units, value)
        table = [
            ('Output', 'Unit', 'Value'), # first row is the table header
            ('Storage - discharge duration',    'hr',   round(t_d, 1)),
            ('Storage - charge duration',       'hr',   round(t_c, 1)),
            ('(storage power capacity, charge) / (generator capacity)',         '-',    round(P_c/P_gen, n_digits)),
            ('(storage power capacity, discharge) / (generator capacity)',      '-',    round(P_d/P_gen, n_digits)),
            ('(Total generation from renewable) / (Electricity consumed)',      '-',    round(kWh_re,n_digits)),
            ('(Electricity from storage to load) / (Electricity consumed)',     '-',    round(kWh_sto, n_digits)),
            ('Curtailment','%', round(Curtailment_pct*100,1))
        ]
        return table
