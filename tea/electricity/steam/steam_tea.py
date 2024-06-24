import os
import pandas as pd
from core.inputs import OptionsInput, Default, ContinuousInput, CategoricalInput, Tooltip, PercentInput, Input
from core.tea import TeaBase
from core import validators, conditionals
from tea.electricity.ccs.pointsources.ccs_tea import CcsTea


class SteamTEA(TeaBase):
    """
    @classmethod

    def user_inputs(cls):
        return [
        ]

    @classmethod
    def user_inputs(cls):
        return [
            OptionsInput(
                'feed', 'Feedstock',
                defaults = [Default('Natural Gas')],
                options = ['Natural Gas', 'Coal'],
                tooltip = Tooltip(
                    "Energy feedstock used to generate steam",
                    source='',
                    source_link='',
                ),
            ),
            ContinuousInput('boiler_efficiency_ng', 'Boiler Efficiency',
                            unit='%',
                            defaults=[Default(80)],
                            tooltip=Tooltip(
                                "Boiler efficiency is an aggregated representation of bolier model, insulation, pre-heating & heat recovery, pressure, temperature, etc. These sub-variations are not handled separately due to lack of data and necessity. Effecieicny = steam energy/feedstock energy, usually 70-86% for natural gas boiler. Heating rate=1/boiler efficiency. This range is based on the DOE and IEA data, which seem to be using HHV as the energy content basis. GREET uses LHV. However, the difference is small because the efficiency is calculated as steam HHV/NG HHV or steam LHV/steam LHV, and the HHV & LHV both have ~ 10% difference. Thus, the difference is largly cancelled out by the division. So, we assume the 70%-86% range is LHV-based for consistency with other modules.",
                                source='GREET, IEA, DOE',
                                source_link='https://greet.es.anl.gov/; https://iea-etsap.org/E-TechDS/HIGHLIGHTS%20PDF/I01-ind_boilers-GS-AD-gct%201.pdf; https://www.energy.gov/sites/prod/files/2014/05/f16/steam15_benchmark.pdf',
                            ),
                            validators=[
                                validators.numeric(), validators.gte(0), validators.lte(100)],
                            conditionals=[conditionals.input_equal_to('feed', 'Natural Gas')]),

            ContinuousInput('ng_price', 'Natural Gas Price',
                            unit='$/thousand ft3',
                            defaults=[Default(3.32)],
                            tooltip=Tooltip(
                                "Natural gas industrial price. Default = 2020 US average; range 2.04 (North Dakota)-20.5 (Hawaii), 2nd largest is 10.8 (Delaware)",
                                source='EIA 2020',
                                source_link='https://www.eia.gov/dnav/ng/ng_pri_sum_a_EPG0_PIN_DMcf_a.htm',
                            ),
                            validators=[
                                validators.numeric(), validators.gte(0), validators.lte(50)],
                            conditionals=[conditionals.input_equal_to('feed', 'Natural Gas')]),

            ContinuousInput('boiler_efficiency_coal', 'Boiler Efficiency',
                            unit='%',
                            defaults=[Default(84)],
                            tooltip=Tooltip(
                                "Boiler efficiency is an aggregated representation of bolier model, insulation, pre-heating & heat recovery, pressure, temperature, etc. These sub-variations are not handled separately due to lack of data and necessity. Effecieicny = steam energy/feedstock energy, usually 75-90% coal boiler. Heating rate=1/boiler efficiency. This range is based on the DOE and IEA data, which seem to be using HHV as the energy content basis. GREET uses LHV. However, the difference is small because the efficiency is calculated as steam HHV/coal HHV or steam LHV/steam LHV, and the HHV & LHV both have ~ 10% difference. Thus, the difference is largly cancelled out by the division. So, we assume the range is LHV-based for consistency with other modules.",
                                source='IEA, DOE',
                                source_link='https://iea-etsap.org/E-TechDS/HIGHLIGHTS%20PDF/I01-ind_boilers-GS-AD-gct%201.pdf; https://www.energy.gov/sites/prod/files/2014/05/f16/steam15_benchmark.pdf',
                            ),
                            validators=[
                                validators.numeric(), validators.gte(0), validators.lte(100)],
                            conditionals=[conditionals.input_equal_to('feed', 'Coal')]),

            ContinuousInput('coal_price', 'Coal Price',
                            unit='$/ton',
                            defaults=[Default(57.18)],
                            tooltip=Tooltip(
                                "Coal industrial price. Default = 2020 US average; range 24 (Nebraska)-116 (Oklahoma)",
                                source='EIA 2020',
                                source_link='https://www.eia.gov/coal/annual/pdf/table34.pdf',
                            ),
                            validators=[
                                validators.numeric(), validators.gte(0), validators.lte(200)],
                            conditionals=[conditionals.input_equal_to('feed', 'Coal')]),

            ContinuousInput('CF', 'Capacity Factor',
                            unit='%',
                            defaults=[Default(90)],
                            tooltip=Tooltip(
                                "Percent of the facility design capacity is used to produce product, e.g., mathematically the number of hours in a year the facility runs, divided by 24*365 hours. No credible public data has been found specifically for average steam generators. For the default 90%, it is assumed that steam is generated on purpose and thus has a relatively large capacity factor compared to power generation",
                            ),
                            validators=[
                                validators.numeric(), validators.gte(0), validators.lte(100)]),

            ContinuousInput('CRF', 'Capacity Recovery Factor',
                            unit='%',
                            defaults=[Default(4.9)],
                            tooltip=Tooltip(
                                "Amortized capital cost per year = crf (capital recovery factor) * total capital cost",
                                source='NREL ATB 2020',
                                source_link='https://atb.nrel.gov/',
                            ),
                            validators=[
                                validators.numeric(), validators.gte(0), validators.lte(100)]),

        ]

    def __init__(self, lca_pathway=None):
        self.lca_pathway = lca_pathway
        self.cost_par = pd.read_csv(PATH + "steam_costpar.csv")
        super().__init__()

"""
    def get_cost(self):
        capital = 0
        fuel_cost =0
        OM=0
        cost_breakdown = {"Capital": capital,
                          "O&M": OM,
                          }

        return cost_breakdown
