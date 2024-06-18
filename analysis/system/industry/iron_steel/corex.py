"""
Functional unit: 1 tonne of hot metal.
model COREX
resources: 1. Song, Jiayuan, et al. "Comparison of energy consumption and CO2 emission for three steel production 
routes—Integrated steel plant equipped with blast furnace, oxygen blast furnace or COREX." Metals 9.3 (2019): 364.
Default values used in this model are from the above resources"""

import matplotlib.pyplot as plt
import numpy as np

from core.common import InputSource
import core.conditionals as conditionals
from core.inputs import OptionsInput, ContinuousInput, PercentInput, Default
import core.validators as validators

from analysis.system.industry.iron_steel.material_corex_bof import m_corex_bof as mcb 
from analysis.system.industry.iron_steel.m_corex_o2 import m_corex_o2 as mco
from analysis.system.industry.iron_steel.m_corex_coal import m_corex_coal as mccoal
from analysis.system.industry.iron_steel.m_corex_co2 import m_corex_co2 as mcco2
from analysis.system.industry.iron_steel.fuel_type import fuel_type as ft, options as fuel_type_options
from analysis.system.industry.iron_steel.linear_elec_projection import linproj
from analysis.system.industry.iron_steel.project_elec_co2 import elec_co2

class COREX(InputSource):

    @classmethod
    def user_inputs(cls):
        return [
            ContinuousInput(
                'hm', 'Amount of hot metal to be produced',
                defaults=[Default(1)],
                validators=[validators.numeric(), validators.gte(0)],
            ),
            OptionsInput(
                'fuel_type', 'Fuel type',
                options=fuel_type_options,
            ),
            # OptionsInput(
            #     'elec_source', 'Electricity Carbon Intensity Source',
            #     options=['IEA SDS', 'User', 'Static'],
            #     defaults=[Default('IEA SDS')]),
            # ContinuousInput(
            #     'eci_2020', '2020 Carbon Intensity',
            #     unit='gCO2/kWh',
            #     defaults=[Default(707)],
            #     validators=[validators.numeric(), validators.gte(0)],
            #     conditionals=[conditionals.input_equal_to('elec_source', 'User')],
            # ),
            # ContinuousInput(
            #     'eci_2040', '2040 Carbon Intensity ',
            #     unit='gCO2/kWh',
            #     defaults=[Default(108, conditionals=[conditionals.input_equal_to('elec_source', 'User')]),
            #               Default(707, conditionals=[conditionals.input_equal_to('elec_source', 'Static')])],
            #     validators=[validators.numeric(), validators.gte(0)],
            #     conditionals=[conditionals.input_equal_to('elec_source', 'User')],
            # ),
        ]

    def run(self):
        hm = self.hm
        f_dri = self.f_dri

        # elec = elec_co2()
        # country = elec['country']
        # years = elec['years'][20:25]  # years in database (2020,2040,5)
        # if self.elec_source == 'IEA SDS':
        #     c_elec = elec['co2'][20:25]  # Electricity carbon intensity tonne CO2/GJ.
        # elif self.elec_source == 'User':
        #     c_elec = linproj(self.eci_2020, self.eci_2040, 2020, 2040)
        # else:  # static
        #     c_elec = np.ones(5) * self.eci_2020 / 3600

        fuel = ft(self.fuel_type) #get fuel type
        hhv = fuel['hhv'] # HHV of fuel
        m_coal = mccoal(m_pellet,m_fore, f_dri,hhv) # tonne of coal needed

        c = fuel['c'] # c content of fuel
        co2_corex = mcco2(m_coal,c)
        # print(f"CO2 emisisons from COREX: {co2_corex}")

        return {
            'co2_corex': co2_corex,
        }

    def plot(self, results):
        #plot bar graph
        bloks = ('COREX','Total')
        x_pos = np.arange(len(bloks))
        emissions =[results['co2_corex'], results['co2_corex']]
        plt.bar(bloks,emissions, align='center', alpha=0.5) # plot bar graph
        plt.xticks(x_pos,bloks)
        plt.ylabel("CO2 emissions (tonne CO2)")
        plt.title("CO2 emission for COREX iron making route")
        plt.show()
