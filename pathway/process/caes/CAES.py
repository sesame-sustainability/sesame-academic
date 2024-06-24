"""
Created on Wed Mar 24 14:07:00 2021

@author: brendanwagner
"""
from core.pathway import ActivitySource
from core.inputs import CategoricalInput, ContinuousInput, OptionsInput, Default
from analysis.lca import compute_input_flows, compute_emission_flows
from core import conditionals, validators
import pandas as pd
import os


PATH = os.getcwd() + "/pathway/process/caes/"
scaling_factor = 0.6    

class CAES(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
            ContinuousInput('efficiency','Efficiency (typically between .4 and .65)', defaults=[Default(0.5)], validators=[validators.numeric(), validators.gt(0), validators.lte(1)]),
            ContinuousInput('cycling_frequency','Cycling Frequency (How many times it is cycled per day)', defaults=[Default(1)], validators=[validators.numeric(), validators.integer(), validators.gt(0)]),
            ContinuousInput('p_capacity','Power Capacity (in MW)', defaults=[Default(60)], validators=[validators.numeric(), validators.integer(), validators.gt(0)]),
            ContinuousInput('e_capacity','Energy Capacity (in MWh)', defaults=[Default(720)], validators=[validators.numeric(), validators.integer(), validators.gt(0)]),
            ContinuousInput('lifetime','Lifetime (in years)', defaults=[Default(30)], validators=[validators.numeric(), validators.integer(), validators.gt(0)]),
        ]

    def get_inputs(self):

        flow_dict = {'electricity': {'name': 'electricity', 'unit': 'kWh', 'value': 1/self.efficiency},}

        return {
            'primary': flow_dict['electricity'],
            'secondary':None
        }

        
    def storage_emission(self):
        df = pd.read_csv(PATH + "CAES_Data.csv")
        ref_p_emissions = df.loc[df['Emissions Source'] == 'Total_Power']['Value'].item()
        ref_e_emissions = df.loc[df['Emissions Source'] == 'Total_Energy']['Value'].item()
        ref_p_capacity = 60 
        ref_e_capacity = 60*12 
        fixed_emissions_power = ref_p_emissions*(self.p_capacity/ref_p_capacity)**scaling_factor
        fixed_emissions_energy = ref_e_emissions*(self.e_capacity/ref_e_capacity)**scaling_factor
        lifetime_storage = (self.e_capacity * 1000) * self.cycling_frequency * 365 * self.lifetime
        emiss = (fixed_emissions_power + fixed_emissions_energy)/lifetime_storage
        return emiss

    def get_emissions(self):
        emiss = self.storage_emission()
        return {'aggregate': {'co2': {'name': 'co2', 'unit': 'kg', 'value': emiss}}}

