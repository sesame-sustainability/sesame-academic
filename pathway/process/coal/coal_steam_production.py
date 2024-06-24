from core.pathway import ActivitySource
from core.inputs import OptionsInput, Default, ContinuousInput, CategoricalInput, Tooltip, PercentInput, Input
from core import conditionals, validators
from analysis.lca import compute_input_flows, compute_emission_flows
import core.validators as validators
import sys
import pandas as pd
import os

class SteamProductionCoal(ActivitySource):

    default_eff = 84

    @classmethod
    def user_inputs(cls):
        return [ 
            CategoricalInput('coal_type', 'Coal type'),
            ContinuousInput('boiler_efficiency', 'Boiler Efficiency',
                            unit='%',
                            defaults=[Default(84)],
                            tooltip=Tooltip(
                                "Boiler efficiency is an aggregated representation of bolier model, insulation, pre-heating & heat recovery, pressure, temperature, etc. These sub-variations are not handled separately due to lack of data and necessity. Effecieicny = steam energy/feedstock energy, usually 75-90% coal boiler. Heating rate=1/boiler efficiency. This range is based on the DOE and IEA data, which seem to be using HHV as the energy content basis. GREET uses LHV. However, the difference is small because the efficiency is calculated as steam HHV/coal HHV or steam LHV/steam LHV, and the HHV & LHV both have ~ 10% difference. Thus, the difference is largly cancelled out by the division. So, we assume the range is LHV-based for consistency with other modules.",
                                source='IEA, DOE',
                                source_link='https://iea-etsap.org/E-TechDS/HIGHLIGHTS%20PDF/I01-ind_boilers-GS-AD-gct%201.pdf; https://www.energy.gov/sites/prod/files/2014/05/f16/steam15_benchmark.pdf',
                            ),
                            validators=[
                                validators.numeric(), validators.gte(0), validators.lte(100)])
        ]


    def get_inputs(self):
        flow_dict = compute_input_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )

        flow_dict['coal']['value'] = flow_dict['coal']['value'] * SteamProductionCoal.default_eff/self.boiler_efficiency

        return {
            'primary': flow_dict['coal'],
            'secondary': []
        }


    def get_emissions(self):
        emission_dict = compute_emission_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )

        for emission in emission_dict['aggregate']:
            emission_dict['aggregate'][emission]['value'] = \
                emission_dict['aggregate'][emission]['value'] * SteamProductionCoal.default_eff / self.boiler_efficiency

        return emission_dict

