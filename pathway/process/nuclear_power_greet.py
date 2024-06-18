from core.pathway import ActivitySource
from core.inputs import CategoricalInput, ContinuousInput, OptionsInput, Default, Tooltip
from core import conditionals, validators
from analysis.lca import compute_input_flows, compute_emission_flows
import core.validators as validators
import sys
import pandas as pd
import os


class NuclearPowerGREET(ActivitySource):

    #@classmethod
    def get_emissions(self):

        return compute_emission_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )

    def get_inputs(self):
        flow_dict = compute_input_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )
        return {
            'primary': flow_dict['uranium'],
            #            'secondary': [flow_dict[key] for key in flow_dict if key != 'natural gas']
            'secondary': []
        }


class LWRNuclearPowerGREET(NuclearPowerGREET):

    filters = [
        ('Generator Type', 'LWR (Light Water Reactor)')
    ]
    @classmethod
    def user_inputs(cls):
        return [
            CategoricalInput('lwr_sub_type', 'LWR Sub-Type',
                             # conditionals=[conditionals.input_equal_to('generator_type', 'LWR (Light Water
                             # Reactor)')],
                             defaults=[Default('Mix (100% PWR_Pressurized Water Reactor)')],
                             tooltip=Tooltip(
                                 'LWR=Light Water Reactor; HTGR= High-Temperature Gas-Cooled Reactor; most US nuclear reactors are LWR. PWR=Pressurized Water Reactor; BRW=Boiling Water Reactor; according to GREET assumption, all US LWR are PWR. Caveat: GREET 2019 model is used here, but it only includes emissions related to uranium extraction/processing/transportation and power plant infrastructure. Other contributors such as plant decomissioning are not included.',
                                 source='GREET2019',
                                 source_link='https://greet.es.anl.gov/'),
                             ),
            CategoricalInput('infrastructure_emission_inclusion', 'Count Emissions from Building Plant Infrastructure',
                             defaults=[Default('yes')],
                             tooltip=Tooltip(
                                 'Emissions related to producing the iron/steel, concrete/cement, … to build the facility, amortized over the lifetime of the facility. For traditional energy product production methods, this contribution is usually very small and thus often ignored by many studies.',
                                 source='GREET2019',
                                 source_link='https://greet.es.anl.gov/'),
                             )
        ]

class HTGRNuclearPowerGREET(NuclearPowerGREET):
    filters = [
        ('Generator Type', 'HTGR')
    ]
    @classmethod
    def user_inputs(cls):
        return [
            CategoricalInput('infrastructure_emission_inclusion', 'Count Emissions from Building Plant Infrastructure',
                             defaults=[Default('yes')],
                             tooltip=Tooltip(
                                 'HTGR= High-Temperature Gas-Cooled Reactor; most US nuclear reactors are not HTGR but LWR (Light Water Reactor). Caveat: GREET 2019 model is used here, but it only includes emissions related to uranium extraction/processing/transportation and power plant infrastructure. Other contributors such as plant decomissioning are not included. Emissions related to producing the iron/steel, concrete/cement, … to build the facility, amortized over the lifetime of the facility. For traditional energy product production methods, this contribution is usually very small and thus often ignored by many studies.',
                                 source='GREET2019',
                                 source_link='https://greet.es.anl.gov/'),
                             )
        ]
