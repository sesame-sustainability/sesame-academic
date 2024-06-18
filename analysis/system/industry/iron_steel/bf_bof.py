"""
Functional unit: 1 tonne of steel
Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
default value are calculated from the source
3. Roussanaly, Simon, et al. "Techno-economic analysis of MEA CO2 capture from a cement kiln–impact of steam supply scenario." Energy Procedia 114 (2017): 6229-6239
4. Captive Plant Info https://cdm.unfccc.int/filestorage/Z/6/H/Z6HFW5FPPRA2BKAUK3CK5XN6EXB98F.1/Kalyani_PDD_28April2006.pdf?t=RUZ8cjczbWN6fDDmawVzU0AbvAU_9mKt_uVl """

"""================================================================================================================"""

import json
import matplotlib.pyplot as plt
import numpy as np

from core.common import InputSource
import core.conditionals as conditionals
from core.inputs import OptionsInput, ContinuousInput, PercentInput, Default,Tooltip,InputGroup
import core.validators as validators
import pandas as pd

from analysis.system.industry.iron_steel.m_e_co2 import m_e_co2 as mc
from analysis.system.industry.iron_steel.m_fuel import m_fuel as mf
from analysis.system.industry.iron_steel.steel_projectory import steel_route
from analysis.system.industry.iron_steel.q_bof_elec import q_bof_elec as qbe
from analysis.system.industry.iron_steel.fe_bof_upstream import fe_bof_upstream as febof  # get Fe needed from hot iron and scrap kg
from analysis.system.industry.iron_steel.q_hot_iron import q_hot_iron as qhi
from analysis.system.industry.iron_steel.project_elec_co2 import elec_co2 as elecc
from analysis.system.industry.iron_steel.m_coke_coal import m_coke_coal as mcc
from analysis.system.industry.iron_steel.c_bf import c_bf as cbf
from analysis.system.industry.iron_steel.fe_bf_upstream import fe_bf_upstream as febf
from analysis.system.industry.iron_steel.fuel_type import fuel_type as ft, options as fuel_type_options
from analysis.system.industry.iron_steel.q_bf import q_bf as qbf
from analysis.system.industry.iron_steel.q_bf_elec import q_bf_elec as qbfe
from analysis.system.industry.iron_steel.m_sinter_ro import m_sinter_ro as msr
from analysis.system.industry.iron_steel.q_sinter import q_sinter as qs
from analysis.system.industry.iron_steel.q_sinter_elec import q_sinter_elec as qse
from analysis.system.industry.iron_steel.q_coking import q_coking as qc
from analysis.system.industry.iron_steel.q_coking_elec import q_coking_elec as qce
from analysis.system.industry.iron_steel.india_iron_steel_co2emission_prediction import co2_ub
from analysis.system.industry.iron_steel.capex import capexs, capexes
from analysis.system.industry.iron_steel.cepci import cepci_v as cep
from analysis.system.industry.iron_steel.exchange_rate import exchange_country as er
from analysis.system.industry.iron_steel.ppp import pppv
from analysis.system.industry.iron_steel.material_cost import c_materials as cm
from analysis.system.industry.iron_steel.material_cost import water as cw
from analysis.system.industry.iron_steel.material_cost import water as cw
from analysis.system.industry.iron_steel.ccs import ccs, user_inputs as ccs_user_inputs
from analysis.system.industry.iron_steel.ccs_transport_storage import co2_transport, co2_storage, options_storage
from analysis.system.industry.iron_steel.linear_elec_projection import linproj
from analysis.system.industry.iron_steel.elec_input import user_inputs_ft_cap as elec_inputs
from analysis.system.industry.iron_steel.elec_input import co2_int
from analysis.system.industry.iron_steel.power_plant import captive_power

class BFBOF(InputSource):

    @classmethod
    def user_inputs(cls):

        cp_options = ['Waste Gas','Coal', 'Solar','Natural Gas','Wind']
        return elec_inputs(cls,cp_options) + [
            ContinuousInput(
                'co2_tax', 'Carbon tax',
                unit = '$/tonne',
                defaults=[Default(50)],
                validators=[validators.numeric(), validators.gte(0)],
            ),
           # ContinuousInput(
           #     'f_scrap', 'Fraction of iron from scrap in BOF',
           #     defaults=[Default(0.16)],
           #     validators=[validators.numeric(), validators.gte(0), validators.lte(1)],
           #     tooltip=('Fraction of scrap in iron bearing material input for BOF')
           # ),
            ContinuousInput(
                'f_scrap', 'BOF: Fraction of iron from scrap',
                defaults=[Default(0.1313)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(1)],
                tooltip=Tooltip('Fraction of scrap in iron bearing material input for BOF. For India: 6.4-25%',source='Shakti Foundation (2019)',
                               source_link='https://shaktifoundation.in/wp-content/uploads/2020/03/Resource-efficiency-in-the-steel-and-paper-sectors.pdf')
            ),
            OptionsInput(
                'fuel_type', 'Fuel type',
                options=fuel_type_options,
                defaults=[Default('BF-BOF')],
                tooltip=Tooltip('Default coal for Blast Furnace')
            ),
            ContinuousInput(
                'f_coke', 'BF: Percent of carbon from coke (rest injected coal)',
                defaults=[Default(65)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                tooltip=Tooltip('Percent of carbon input that is from coke (vs. injected coal). Default is about 274 kg/tcs coke and 195 kg/tcs injected coal, assuming 80% carbon in coke and 60% carbon in coal ',source='He, 2017',source_link='https://shaktifoundation.in/wp-content/uploads/2020/03/Resource-efficiency-in-the-steel-and-paper-sectors.pdf' )
            ),
            # ContinuousInput(
            #     'f_pci', 'Pulverized Coal Injection (PCI) Coke Displacement',
            #     defaults=[Default(8)],
            #     units='%',
            #     validators=[validators.numeric(), validators.gte(0), validators.lte(1)],
            #     tooltip=Tooltip('Percent displacement of coke with PCI in blast furnace; for the default sytem coke consumption = . Default % based on Shakti Foundation.', source='Shakti Foundation',source_link='https://shaktifoundation.in/wp-content/uploads/2020/03/Resource-efficiency-in-the-steel-and-paper-sectors.pdf')
            # ),
            ContinuousInput(
                'f_sinter', 'BF: Fraction of iron from sinter (rest raw ore)',
                defaults=[Default(0.82772)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(1)],
                tooltip=Tooltip('Fraction of iron input that is from sinter (vs. raw ore)')
            ),

        ] +  [
           # OptionsInput(
           #     'elec_source', 'Electricity carbon intensity source',
           #     options=['IEA SDS', 'User', 'Static'],
           #     defaults=[Default('IEA SDS')],
           #     tooltip=Tooltip('IEA SDS = IEA Sustainable Development Scenario', source='IEA (2020)',
           #                     source_link='https://www.iea.org/reports/tracking-power-2020')
           # ),
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
           # ),
        ] + [
            InputGroup('mat_prices', '2020 Fuel & Material Input Prices', children=[
            ContinuousInput(
               'scrap_price', 'Scrap',
               unit='$/tonne',
               defaults=[Default(385.11)],
               validators=[validators.numeric(), validators.gte(0)],
               tooltip=Tooltip('Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',source='MEPS',
                               source_link='https://mepsinternational.com/gb/en/products/ferrous-scrap-prices')
            ),
            ContinuousInput(
                'scrap_price_change', '% change in scrap price, 2020-2040',
                defaults=[Default(0)],
            ),
            ContinuousInput(
             'iron_ore_price', 'Ore',
               unit='$/tonne',
               defaults=[Default(56.75)],
               validators=[validators.numeric(), validators.gte(0)],
               tooltip=Tooltip('Default prices  are with respect to Iron Ore Fines from India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',source='Indian Bureau of Mines',
                               source_link='04272021170955ASPmineral_Dec20_(P)&(U)_Final.pdf (ibm.gov.in)')
            ),
            ContinuousInput(
                'iron_ore_price_change', '% change in iron ore price, 2020-2040',
                defaults=[Default(0)],
            ),
            ContinuousInput(
            'limestone_price', 'Limestone',
               unit='$/tonne',
               defaults=[Default(12.44)],
               validators=[validators.numeric(), validators.gte(0)],
               tooltip=Tooltip('Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price', source='Indian Bureau of Mines',
                               source_link='04272021170955ASPmineral_Dec20_(P)&(U)_Final.pdf (ibm.gov.in)'),
            ),
            ContinuousInput(
                'limestone_price_change', '% change in limestone price, 2020-2040',
                defaults=[Default(0)],
            ),
            ContinuousInput(
              'dolomite_price', 'Dolomite',
               unit='$/tonne',
               defaults=[Default(12.44)],
               validators=[validators.numeric(), validators.gte(0)],
               tooltip=Tooltip('Default prices  are with respect to India in 2020 (assuming same as limestone). Due to fluctuation in pricing and location specific costs, user may input price', source='Indian Bureau of Mines',
                               source_link='04272021170955ASPmineral_Dec20_(P)&(U)_Final.pdf (ibm.gov.in)'),
            ),
            ContinuousInput(
                'dolomite_price_change', '% change in dolomite price, 2020-2040',
                defaults=[Default(0)],
            ),
            ContinuousInput(
             'coal_price', 'Coal',
               unit='$/tonne',
               defaults=[Default(120.03)],
               validators=[validators.numeric(), validators.gte(0)],
               tooltip=Tooltip('Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price', source='Indian Ministry of Coal',
                               source_link='https://coal.nic.in/sites/default/files/2021-03/19-02-2021-nci.pdf')
            ),
            ContinuousInput(
                'coal_price_change', '% change in coal price, 2020-2040',
                defaults=[Default(0)],
            ),
            ContinuousInput(
               'electricity_price', 'Electricity',
               unit='$/GJ',
               defaults=[Default(10.6)],
               validators=[validators.numeric(), validators.gte(0)],
               tooltip=Tooltip('Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price', source='IndiaStat',
                               source_link='https://www.indiastat.com/table/utility-wise-average-rates-of-electricity-supply-and-electricity-duty-tax/month-wise-average-price-volume-electricity-transa/1414631')
            ),
            ContinuousInput(
                'electricity_price_change', '% change in electricity price, 2020-2040',
                defaults=[Default(0)],
            ),
            ])

            ] + ccs_user_inputs()+[
            OptionsInput(
                'co2_storage', 'CO2 storage type',
                options = options_storage,
                defaults = [Default('Depleted oil, onshore')],
                conditionals=[conditionals.input_equal_to('ccs', 'Yes')],
            ),
            ContinuousInput(
                'co2_transportation_distance', 'CO2 transportation distance',
                unit='km',
                defaults=[Default(100)],
                conditionals=[conditionals.input_equal_to('ccs', 'Yes')],
                validators=[validators.numeric(), validators.gte(0),validators.lte(100000)],
            ),
        ]

    def run(self):
        m_steel = steel_route('BF-BOF')[
                  0:5]  # amount of steel to be produced by chosen route. in the year (2020,2040,5)



        # Dictionary to store carbon intensity of energy kg CO2/MJ:
        # i_co2 = {"coke": 0.103,"coal":0.083832,"elec":0.086275,
        #         "air":0.083908,"steam":0.088567,"fwater":0.122222,"hot_blast":0.083932}
        # i_*_co2: carbon intensity of certain energy kg CO2/MJ
        # assume internal use of COG, BFG has zero associated CO2 emissions. coking making allocate all co2 emission to coke produced.
        # air_CO2 emission in bof
        i_air_co2 = 0.083908  # heating air carbon intensity. (13.7+6.2)*44/12/(598.7+270.9) tonne CO2/GJ.
        cr_bof_air = 0.1037  # air consumption rate for hot steel production: (73+28.9+1.8)/1000 tonne air/tonne hot steel.
        e_bof_air = 8.385728  # air energy intensity GJ/tonne air = (598.7+270.9)/(73+28.9+1.8)
        m_bof_air = cr_bof_air * m_steel  # tonne of air input in bof
        q_bof_air = m_bof_air * e_bof_air  # air energy consumption/input GJ
        m_bof_air_co2 = q_bof_air * i_air_co2
        # print(f"CO2 emission from air_BOF: {m_bof_air_co2} kg")
        # Tested, correct

        # steam_CO2 emission in bof
        i_steam_co2 = 0.088567  # Steam carbon intensity tonne CO2/GJ =0.5*44/12/20.7
        e_steam = 3.7636364  # Steam energy intensity GJ/tonne steam=20.7/5.5. could be changed if steam energy intensity is higher.
        cr_steam = 0.0055  # Steam consumption rate tonne steam/tonne hot steel
        m_steam = cr_steam * m_steel  # tonne steam
        q_steam = m_steam * e_steam  # energy associated with steam GJ
        m_steam_co2 = q_steam * i_steam_co2  # amount of CO2 emission (tonne)
        # print(f"CO2 emission from steam_BOF: {m_steam_co2} tonne")
        # Tested, correct

        # cog_CO2 emission in bof
        cr_bof_cog = 0.0006  # tonne cog/tonne hot steel
        m_bof_cog = cr_bof_cog * m_steel  # tonne cog
        hhv_cog = 36.17  # COG LHV in GJ/tonne, default: 21.7/0.6=36.17
        q_bof_cog = m_bof_cog * hhv_cog  # GJ
        i_cog_co2 = 0  # tonne co2/GJ. assumed cog internal use has zero CO2 emission. internal energy
        m_bof_cog_co2 = q_bof_cog * i_cog_co2
        # print(f"CO2 emission from COG_BOF: {m_bof_cog_co2} tonne")

        # elec_CO2 emission in bof
        f_scrap = self.f_scrap
        fe_hi = 0.965  # Fe content in hot iron, default: 0.965
        fe_scrap = 0.99  # Fe content in scrap, default: 0.99
        t_fe_bof_upstream = febof(m_steel)  # amount of Fe from hot iron and scrap. tonne
        m_hi_fe = (1 - f_scrap) * t_fe_bof_upstream  # amount of Fe from hot iron(tonne)
        m_hi = m_hi_fe / fe_hi  # tonne of hot iron
        m_scrap_fe = f_scrap * t_fe_bof_upstream  # amount of Fe from scrap
        m_scrap = m_scrap_fe / fe_scrap  # scrap input in bof (tonne)
        q_hi = qhi(m_hi)  # total energy content of hot iron. (GJ)

        # freshwater in bof
        m_bof_fwater = 310 / 950 * m_hi  # tonne of fresh water needed in bof

        # projected electricity carbon intensity data
        elec = elecc()  # get the electricity data
        country = self.country
        years = elec['years'][20:25]  # get the projectory years. x_axis in plot
        # years in string from
        y = [str(i) for i in years]
        i_elec_co2 = co2_int(self, years) #method for getting electricity CI
        q_bof_elecs = qbe(t_fe_bof_upstream, q_hi, q_bof_air, q_bof_cog, q_steam)
        # electricity needed in bof
        m_bof_elec_co2 = np.array(q_bof_elecs) * np.array(
            i_elec_co2)  # mc(q_bof_elecs, i_elec_co2)  # bof_elec associated CO2 emission (tonne)
        # print(f"Electricity needed in BOF: {q_bof_elecs} GMJ")
        # print(f"elec CO2 : {i_elec_co2}")




        # BF process
        # calculate CO2 emission from bf
        # coke_CO2 emission in bf
        fuel = ft(fuel_type_options.index(self.fuel_type))  # get the fuel c% and hhv
        fe_hi0_upstream = febf(m_hi_fe)  # amount of Fe needed from upstream: raw ore and sinter.
        m_bf_carbon0 = cbf(fe_hi0_upstream)  # tonne of C needed in bf
        # a=m_coke_coal(293.762,0.6016,0.645,0.6021) # default values
        f_coke = self.f_coke/100  # Fraction of c from coke
        c_coke = 0.7987  # c content in coke, default:=269.4/337.3
        c_coal = fuel['c'] / 100  # c content in coal, default: =269.4/447.3=0.6021.
        m_bf_coke = mcc(m_bf_carbon0, f_coke, c_coke, c_coal)["coke"]  # tonne coke in bf
        # print(f"m_bf_coke:{m_bf_coke/m_steel}")
        # m_bf_coke = (1-self.f_pci/100)*m_bf_coke
        m_bf_coal = mcc(m_bf_carbon0, f_coke, c_coke, c_coal)["coal"]  # tonne coal in bf
        hhv_coke = 28.435  # default value GJ/tonne =7779.8/273.6  #this need to find papers to find correlations with coal
        q_bf_coke = m_bf_coke * hhv_coke
        m_bf_coke_co2 = m_bf_coke * c_coke * 44 / 12  # CO2 emisison due to coke
        # print(f"CO2 emission from coke in BF {m_bf_coke_co2} tonne")
        # coal_CO2 emission in bf
        hhv_coal = fuel['hhv']  # HHV of coal GJ/tonne, default: 26.33727
        q_bf_coal = m_bf_coal * hhv_coal  # GJ of coal input in bf
        m_bf_coal_co2 = m_bf_coal * c_coal * 44 / 12  # CO2 emission due to coal
        # print(f"CO2 emission from coal in BF {m_bf_coal_co2} tonne")

        # hblast_CO2 emission in bf
        # q_bf0,q_bf_coke,q_bf_coal,q_hblast; (15082,7779.8,5130.5,1795.5)     #default value
        cr_q_hblast = 1795.5 / 950  # hot blast consumption rate for hot iron production in bf GJ/tonne hot iron
        i_hblast_co2 = 41.1 * 44 / 12 / 1795.5  # hot blast carbon intensity. tonne CO2/GJ
        q_hblast = cr_q_hblast * m_hi  # GJ input in bf
        m_bf_hblast_co2 = q_hblast * i_hblast_co2  # tonne CO2 due to hot blast

        # elec_CO2 emission in bf
        f_sinter = self.f_sinter
        fe_sinter = 0.63  # assume fixed Fe content in sinter
        fe_ro = 0.64  # assume fixed Fe content in raw ore
        m_sinter = msr(fe_hi0_upstream, f_sinter, fe_sinter, fe_ro)["sinter"]
        m_ro = msr(fe_hi0_upstream, f_sinter, fe_sinter, fe_ro)["raw ore"]
        q_bf0 = qbf(m_sinter, m_ro)  # total energy needed in bf
        # print(f"coke:{q_bf_coke/m_steel}")
        # print(f"hblast:{q_hblast/m_steel}")
        # print(f"coal:{q_bf_coal/m_steel}")
        # print(f"hot iron :{m_hi / m_steel}")
        q_bf_elec = qbfe(m_hi, q_bf_coke, q_bf_coal, q_hblast)
        # print(q_bf_elec/m_steel)
        # print(f"m_hi: {m_hi/m_steel}, q_bf_coke: {q_bf_coke/m_steel}, q_bf_coal: {q_bf_coal/m_steel}, q_hblast: {q_hblast/m_steel}")
        # print(i_elec_co2)
        m_bf_elec_co2 = np.array(q_bf_elec) * np.array(i_elec_co2) # mc(q_bf_elec,i_elec_co2)
        # print(q_bf_elec/m_steel)
        # print(f"electricity needed in BF {q_bf_elec} GJ"
        # Sintering process
        # Calculate CO2 emission in sintering: cog, coke, fwater, steam,elec
        q_sinter0 = qs(m_sinter)  # Total energy needed for sintering GJ
        # (q_sinter0,q_sinter_cog,q_sinter_coke,q_sinter_fwater,q_sinter_steam)=(2065.3, 67.6, 1811.8, 0.3, 5.2)     #default value
        q_sinter_cog = 67.6 / 1248.5 * m_sinter  # GJ
        m_sinter_cog_co2 = q_sinter_cog * i_cog_co2  # tonne CO2
        q_sinter_coke = 1811.8 / 1248.5 * m_sinter  # GJ
        m_sinter_coke = q_sinter_coke / hhv_coke  # tonne
        m_sinter_coke_co2 = m_sinter_coke * c_coke  # tonne CO2
        q_sinter_fwater = 0.3 / 1248.5 * m_sinter  # GJ
        i_fwater_co2 = 0.01 * 44 / 12 / 0.3  # tonne CO2/GJ
        m_sinter_fwater = 108.6 / 1248.5 * m_sinter  # tonne of fresh water
        m_sinter_fwater_co2 = q_sinter_fwater * i_fwater_co2  # tonne CO2
        q_sinter_steam = 5.2 / 1248.5 * m_sinter  # GJ
        m_sinter_steam_co2 = q_sinter_steam * i_steam_co2
        q_sinter_elec0 = qse(q_sinter0, q_sinter_cog, q_sinter_coke, q_sinter_fwater, q_sinter_steam)
        m_sinter_elec_co2 = np.array(q_sinter_elec0) * np.array(i_elec_co2)
        m_flux = 175.6 / 1248.5 * m_sinter  # tonne of flux needed.
        m_bf_flux_co2 = m_flux*((44/(84.3139) + 44/(100.09))/2) # take average of dolomite and limestone emissions (assuming all carbon goes to co2)

        # print(f'electricity needed in sintering{q_sinter_elec0}')


        # coke making
        # calculate CO2 emission in coke making: elec
        # BFG was provided, suppose CO2 associated with BFG is zero.
        m_coke = m_bf_coke + m_sinter_coke  # total coke required in the bf-bof routes
        m_coking_coal = 447.3 / 337.3 * m_coke  # total coal input in coke making plant
        q_coking0 = qc(m_coke)  # total energy input in sintering
        q_bfg = 1368.2 / 337.3 * m_coke  # energy from bfg GJ
        q_coking_elecs = qce(q_coking0, q_bfg)  # electricity needed in sintering
        #energy of COG released ( minus what is used downstream based on source 1)
        cog_en = 2369.3/1000 #GJ/tcs
        #cog_co2  = 0.044*cog_en*np.ones(5)*m_steel
        m_coking_elec_co2 = np.array(q_coking_elecs) * np.array(i_elec_co2)
        m_coking_co2 = np.array(q_coking_elecs) * np.array(i_elec_co2) #+ cog_co2
        # print(f"electricity for coking {q_coking_elecs}")

        if self.elec_source == 'Captive Power Plant':
            cp_eff = self.cp_eff
            t_elec = (q_coking_elecs + q_sinter_elec0 + q_bf_elec + q_bof_elecs) / np.array(
                m_steel)  # sum all electricity
            # print(t_elec)
            if self.cp_fuel == 'Waste Gas':
                m_COG = (68.2/0.4473)*m_coking_coal/m_steel #amt of waste COG per tonne of coking coal
                if self.ccs == 'No': # if ccs is not used, all (reasonable) BF gas recovered
                    m_BFG = (556.8/0.2736)*m_bf_coke/m_steel #amt of waste BF per tonne of coke entering BF
                else: # if ccs in place & captive power plant chosen, all that is captured is no longer usable in CP*
                    m_BFG = (100-self.cap_r)/100*(556.8/0.2736)*m_bf_coke/m_steel
                m_BOFG = (52.5/0.950)*m_hi/m_steel# amt of waste BOF per tonne of hot metal
                wg_data = [m_COG,m_BFG,m_BOFG]
                # print(wg_data)
                cp_data = captive_power(self.cp_fuel, wg_data, cp_eff, country)
                cp_elec = cp_data['cp_elec']  # electricity from captive power plant
                cp_em = cp_data['cp_em']

                cp_em = np.array(cp_em)
                deficit_elec = (t_elec - cp_elec).tolist()
                # print(deficit_elec)
                # if the power plant covers all elec - get emissions from just power plant; else, use a weighted factor with IEA grid intensity. If excess, sell it back to the grid
                cp_portion = np.array(cp_elec / t_elec)
                for i in deficit_elec:
                    idx = deficit_elec.index(
                        i)  # https://stackoverflow.com/questions/18327624/find-elements-index-in-pandas-series
                    if i > 0:
                        i_elec = np.array(i_elec_co2) * (1 - cp_portion) + cp_portion * cp_em
                        # print(i_elec_co2)
                        # print('avg_i_elec')
                        avg_i_elec = (i_elec)
                    elif i < 0:
                        #capture the co2 intensity of the steel
                        #assume only amount of electricity need is factored into emissions
                        #possibly the remaining is sent to grid
                        #0.93 is to account for 7% auxiliary consumption
                        avg_i_elec = (cp_em/(cp_elec/0.93))*t_elec
                    else:
                        avg_i_elec = cp_em

            else:
                wg_data = []
                cp_eff =  self.cp_eff
                cp_elec = t_elec
                cp_data = captive_power(self.cp_fuel, wg_data,self.cp_eff,country)
                cp_em = cp_data['cp_em']*cp_elec
                # print(cp_em)
                avg_i_elec = cp_em #assume all electricity  produced was consumed in plant & satisfied plant demand
                deficit_elec = 0
            # avg_i_elec = np.array(avg_i_elec)
            # print(avg_i_elec)
            m_coking_elec_co2 = avg_i_elec * q_coking_elecs
            m_sinter_elec_co2 = avg_i_elec * q_sinter_elec0
            m_bf_elec_co2 = avg_i_elec * q_bf_elec
            m_bof_elec_co2 = avg_i_elec * q_bof_elecs
        # print(t_elec)
        # print(cp_em)
        # total CO2 emission in coke making
        co2_coking = m_coking_elec_co2# + cog_co2
        # print(f"coking:{co2_coking}")
        # total CO2 emission in sinteirng
        co2_sintering = m_sinter_coke_co2 + m_sinter_steam_co2 + m_sinter_fwater_co2 + m_sinter_elec_co2
        # print(f'sintering:{co2_sintering}')

        # total CO2 emission in bf
        co2_bf = m_bf_coke_co2 + m_bf_coal_co2 + m_bf_hblast_co2 + m_bf_elec_co2 + m_bf_flux_co2
        # print(f'bf:{co2_bf}')

        # total CO2 emission in bof
        co2_bof = m_bof_elec_co2 + m_bof_air_co2 + m_steam_co2
        # print(f'bof:{m_bof_elec_co2/m_steel}')

        t_co2 = co2_coking + co2_sintering + co2_bf + co2_bof
        t_co2_fossil = m_bf_coke_co2 + m_bf_coal_co2 + m_bf_hblast_co2 + m_sinter_coke_co2 + m_bf_flux_co2 #+ cog_co2#Direct co2 emissions tonne
        # old_t_co2_fossil = t_co2_fossil
        # t_co2_fossil = pd.concat([pd.Series(np.zeros(3)),t_co2_fossil[2:4]],ignore_index=True)
        # print(f'total:{t_co2_fossil/m_steel}')
        # print(f'total:{(t_co2-t_co2_fossil) / m_steel}')
        # print(f"CO2_coking: {co2_coking} CO2_sintering: {co2_sintering} CO2_bf: {co2_bf} CO2_bof: {co2_bof} total: {t_co2}")
        # print(f"bof air co2: {m_bof_air_co2}")
        # print(f"bf air co2: {m_bf_coke_co2 + m_bf_coal_co2 + m_bf_hblast_co2 }")
        # print(f"coke plant air co2: {m_bof_air_co2}")

        #CO2 emission by sources
        co2_by_product_gas = m_bof_air_co2 + m_sinter_steam_co2 + m_steam_co2 + m_bf_hblast_co2 + m_sinter_cog_co2 + m_sinter_fwater_co2 #+ cog_co2
        # print(f" coking:{m_coking_elec_co2}; m_sinter:{m_sinter_elec_co2}; m_bf_elec_co2:{m_bf_elec_co2}; m_bof: {m_bof_elec_co2}")
        m_co2_elec = m_coking_elec_co2 + m_sinter_elec_co2 + m_bf_elec_co2 + m_bof_elec_co2
        print(m_co2_elec/m_steel)
        co2_coke = m_sinter_coke_co2 + m_bf_coke_co2
        co2_coal = m_bf_coal_co2
        # gettheupperboundofco2emissionaccordingtoIEA-SDSscenario.
        ub = co2_ub(m_steel)  # gettheIndiasteelindustryCO2emissionupperboundbysatisfyIEA-SDSscenario
        # print(f"co2 elec coking: {q_coking_elecs/m_steel}; singter elec: {q_sinter_elec0/m_steel}, bf elec: {q_bf_elec/m_steel},bof elec {q_bof_elecs/m_steel}")



###########################################################################################################################################################
        #Economic analysis
        #CAPEX
        cepci1 = cep(2017)[0] # get the base cost year. source: Techno-economic evaluation of innovative steel production technologies (wupperinst.org)
        cepci2 = cep(2020)[0] #get the most up to date value available.
        cepci3 = cep(2006)[0] #for the power plant capex
        ppp2= pppv(country,2017) # get the ppp for the country of interest in 2017. the reference year is 2017 for the base case.

        #coking plant
        capacity2_coking = np.array(capexes['Base Scale'][0]) # Assume the capacity is the same as base scale.
        n_coking = m_coke/capacity2_coking # number of coking plant
        cost2_coking= np.array(n_coking) * np.array(capexs(capacity2_coking,cepci1,cepci2,ppp2)['Coke plant']) # total cost for producting m_steel tonne of steel in specific year. the LCU for coking plant

        #sintering plant
        capacity2_sintering = np.array(capexes['Base Scale'][1]) # #Assume the capacity is the same as base scale.
        n_sinter = m_sinter/capacity2_sintering # number of sinter plant
        cost2_sintering= np.array(n_sinter) * capexs(capacity2_sintering,cepci1,cepci2,ppp2)['Sintering plant'] #the LCU for sintering plant

        #BF plant
        capacity2_bf = np.array(capexes['Base Scale'][3]) # Assume the capacity is the same as base scale.
        n_bf = m_hi/capacity2_bf # total amount of hot iron needed for steel produced. based on steel produciton prediction, this will automatically correlated with the amount of steel produced.
        cost2_bf = np.array(n_bf) * capexs(capacity2_bf,cepci1,cepci2,ppp2)['BF'] #the LCU for BF plant

        #BOF plant
        capacity2_bof = np.array(capexes['Base Scale'][7]) # Assume the capacity is the same as base scale.
        n_bof = m_steel/capacity2_bof # number of BF
        cost2_bof= np.array(n_bof) * capexs(capacity2_bof,cepci1,cepci2,ppp2)['BOF'] #the LCU for BOF plant

        #Captive Power Plant

        if self.elec_source == 'Captive Power Plant':
            if self.cp_fuel == 'Waste Gas':
                cp_elec = t_elec #capacity based on deamnd atm
                processes = capexes['Equipments'][0:11]  # processes
                sf = capexes['shape factor'][0:11]  # shape (scaling) factors
                capacity1 = capexes['Base Scale'][0:11]  # base scale
                cost1 = capexes['Process_plant_cost'][0:11]  # process plant cost. euro.
                capacity2_cpp = capexes['Base Scale'][10]
                n_cpp = cp_elec / capacity2_cpp
                ppp1 = pppv("India",2006)  # the source base cost is based on 2006 Rupee
                ppp2 = pppv('United_States', 2020)  # convert to USD
                cost2 = [np.array(cost1) * (np.array(capacity2_cpp) / np.array(capacity1)) ** np.array(sf) * \
                         cepci2 / cepci3 * ppp2 / ppp1]  # to USD
                # print(cost2)
                process_capex = [dict(zip(processes, cost)) for cost in cost2][
                    0]  # assign the value in a list to keys in a list one by one
                # print(process_capex['CPP'])
                capex_cpp = n_cpp*process_capex['CPP'] #32000000*cep(2020)[0]/cep(2012)[0]
                # print(capex_cpp)
                ppp2 = pppv(country, 2017) # reset pp1 and ppp2
            elif self.cp_fuel == 'Coal':
                capex_cpp = cp_data['cp_capex']*t_elec #$/GJ*elec
            elif self.cp_fuel == 'Solar':
                capex_cpp = cp_data['cp_capex']*t_elec
        else:
            capex_cpp = 0
        # print(capex_cpp)
        # print(capex_cpp)
        # print(cepci2)
        # print(cepci3)
        # print(ppp1)
        # total capital investment
        t_capex = (np.array(cost2_coking) + np.array(cost2_sintering) + np.array(cost2_bf) + np.array(cost2_bof))/ m_steel / np.array(er(country)) + np.array(capex_cpp)
        # print(f"total capex:{t_capex}")
        #OPEX
        #OPEX material/energy price
        scrap_price = []
        iron_ore_price = []
        limestone_price = []
        dolomite_price = []
        coal_price = []
        electricity_price = []
        y_i = 2020 #initial/baseline year
        y_f = 2040 # final year
        for y in years:
            scrap_price_update = self.scrap_price + (y - y_i) * self.scrap_price * (self.scrap_price_change/100)/(y_f - y_i)
            scrap_price.append(scrap_price_update)
            iron_ore_price_update = self.iron_ore_price + (y - y_i) * self.iron_ore_price * (self.iron_ore_price_change/100)/(y_f - y_i)
            iron_ore_price.append(iron_ore_price_update)
            limestone_price_update = self.limestone_price +  (y - y_i) * self.limestone_price * (self.limestone_price_change/100)/(y_f - y_i)
            limestone_price.append(limestone_price_update)
            dolomite_price_update = self.dolomite_price +  (y - y_i) * self.dolomite_price * (self.dolomite_price_change/100)/(y_f - y_i)
            dolomite_price.append(dolomite_price_update)
            coal_price_update = self.coal_price + (y - y_i) * self.coal_price *  (self.coal_price_change/100)/(y_f - y_i)
            coal_price.append(coal_price_update)
            electricity_price_update = self.electricity_price + (y - y_i) * self.electricity_price * (self.electricity_price_change/100)/(y_f - y_i)
            electricity_price.append(electricity_price_update)
        # print(f"scrap price: {scrap_price}")

        tc_onm = np.array(m_steel) * 0.8 * np.array(er(country)) #assume steel operation and maintenance cost is $0.8/tonne. source 3.
        tc_ins_loc = np.array(t_capex) * 0.045 # maintenance and labor cost. source 3. Indian Rupee.
        tc_labor = 100*60000/1360000*np.array(m_steel) # assume number of labor needed is linearly correlated to total amount of steel produced. source 3.
        tc_administrative = 0.3 * tc_onm # administrative labor cost. Rupee. source 3.

        if self.elec_source == 'Captive Power Plant':
            if self.cp_fuel == 'Waste Gas':
                tc_onm += cp_data['maintenance']*t_elec * m_steel * np.array(er(country))
                tc_labor += cp_data['sal/admin']*t_elec * m_steel * np.array(er(country))
                cost_oil = cp_data['mat_cost']*t_elec*m_steel * np.array(er(country)) # furnace oil for waste gas captive plant (already in Rupees)
                cpp_opex = ((cp_data['maintenance'] + cp_data['sal/admin'] + cp_data['mat_cost']) * m_steel * np.array(er(country)) )*t_elec
                # print((cp_data['maintenance'] + cp_data['sal/admin'] + cp_data['mat_cost'])*t_elec)
            else:
                cost_oil = np.zeros(5)
                cpp_opex = (cp_data['maintenance']+ cp_data['mat_cost'])*t_elec* m_steel * np.array(er(country))
                tc_onm += cpp_opex # add fuel costs to maintenance for
                # print(cpp_opex)
        else:
            cost_oil = np.zeros(5)


        t_omt = tc_onm + tc_ins_loc + tc_labor + tc_administrative # operation & management cost of bf-bof

        cost_iron_ore = np.array(scrap_price) * m_sinter * np.array(er(country))#assume the price of sinter = price of iron ore. price: Rupee/ t. (Indian ruppe)
        cost_coal = np.array(coal_price) * (m_bf_coal + m_coking_coal )* np.array(er(country)) #coal price: Rupee/t. (Indian Rupee)
        cost_flux = (np.array(limestone_price)+ np.array(dolomite_price))/2 * m_flux * np.array(er(country))#suppose flux is a half half mixture of limestone and dolomite. (Indian Rupee)
        cost_scrap = np.array(scrap_price) * m_scrap * np.array(er(country)) # price: Rupee/t. cost of scrap. (Indian Rupee)

        if self.elec_source == 'Captive Power Plant': #assume cost back to grid is same from grid ( to be revised_
            if np.array(deficit_elec).sum() <= 0:
                # print(deficit_elec)
                cost_elec = np.zeros(5) #np.array(electricity_price)*deficit_elec
            else:
                cost_elec = np.array(electricity_price) * (q_bf_elec + q_coking_elecs + q_bof_elecs + q_sinter_elec0) * np.array(er(country))*(1-cp_portion)
            #need to factor in selling back to grid / capacity  change; np.array(electricity_price) * deficit_elec
        else:
            cost_elec = np.array(electricity_price) * (q_bf_elec + q_coking_elecs + q_bof_elecs + q_sinter_elec0) * np.array(er(country)) #cost of electrcity. india's electricity price. unit: Rupee/GJ. (Indian Rupee)
        m_water = m_sinter_fwater + np.array(m_bof_fwater) #total fresh water consumption. (tonne)
        # print(f"sinter tonne: {m_sinter}; cost of iron ore: {cost_iron_ore}")
        tcost_water = []
        opex = []
        for i, wateri in enumerate(m_water):
            cost_water = cw(wateri) * er(country)  # cost of water. $
            opexi = t_omt[i] + cost_iron_ore[i] + cost_coal[i] + cost_flux[i] + cost_scrap[i] + cost_elec[i] + cost_water + cost_oil[i] # total operation cost. including material cost, utility cost.
            tcost_water.append(cost_water[0])
            opex.append(opexi[0])
        # print(f'opex:{opex}')

        # CCS CAPEX
        ccs_regeneration_co2 = 0
        capex_ccs = 0
        opex_ccs_add = 0
        co2_ng =0
        ru = 0
        # # print(f"co2_bf:{co2_bf/m_steel} ")
        # print(t_co2_fossil/m_steel)
        ################################################################################################################
        #CCS


        # years in string from
        y = [str(i) for i in years]

        if self.ccs == 'Yes':
            cap_r = self.cap_r
            solvent = self.solvent
            regeneration_u = self.regeneration_u
            ccs_idx = y.index(self.ccs_start)
            # print(ccs_idx)
            ccs_vec = np.concatenate((np.zeros(ccs_idx),np.ones(len(years)-ccs_idx)))
            # When is CCS implemented? Multiply all additions from CCS w/ vector to indicate when ccs implemented
            
            cost_ccs = ccs(t_co2_fossil*ccs_vec, solvent, cap_r, regeneration_u, country)
            # print(t_co2/m_steel)
            #CO2 emissions
            ccs_regeneration_co2 = np.array(cost_ccs['CO2'])
            # old_co2_fossil = t_co2_fossil
            if regeneration_u == 'NG':
                co2_ng = ccs_regeneration_co2 # co2 emission due to NG used in ccs (tonne)
                # print(co2_ng/m_steel)
                #
                # print()
                # t_co2_fossil -= t_co2_fossil * (cap_r/100) * ccs_vec - ccs_regeneration_co2
            else:
                if self.elec_source == 'Captive Power Plant':
                    if deficit_elec < 0: # excess electrcitiy goes to ccs operation ( price not adjusted for electricity here)
                        ccs_regeneration_co2 = ccs_regeneration_co2/np.array(elecc(country)['co2'][20:25])*avg_i_elec
                        m_co2_elec += ccs_regeneration_co2
                        #t_co2_fossil -= t_co2_fossil * (cap_r / 100) * ccs_vec
                else:
                    m_co2_elec += ccs_regeneration_co2 # co2 emission from electricity source (tonne)
                # t_co2_fossil -= t_co2_fossil * ( cap_r / 100) * ccs_vec
                    # print(co2_sintering/m_steel)
            # print(co2_bf/m_steel)
            co2_sintering += - cap_r/100 * m_sinter_coke_co2*ccs_vec
            co2_bf += -cap_r/100*(m_bf_coke_co2 + m_bf_coal_co2 + m_bf_hblast_co2)*ccs_vec
            t_co2 = t_co2 -t_co2_fossil*( cap_r / 100) * ccs_vec + ccs_regeneration_co2   #minus amount of co2 captured, plus amount of co2 emitted in ccs
            # print(t_co2/m_steel)*
            # print(f"co2_bf:{co2_bf} ")
            # print(f"elec:{m_coking_elec_co2/i_elec_co2}")
            #CO2 emission by sources
            co2_by_product_gas +=  -cap_r/100*m_bf_hblast_co2*ccs_vec
            co2_coke += -cap_r/100*(m_sinter_coke_co2 + m_bf_coke_co2)*ccs_vec
            co2_coal += -cap_r/100*m_bf_coal_co2*ccs_vec

            # CCS transportation and storage cost
            co2_transportation_distance = float(
                self.co2_transportation_distance)  # co2 transport to storage location. (km)
            ccs_co2_transport = co2_transport(co2_transportation_distance)  # co2 transportation price ($_2020/tCO2)
            ccs_cost_transport = ccs_co2_transport *( t_co2_fossil * cap_r / 100 )# co2 transportation cost ($_2020)
            # print(f'ccs transport cost: {ccs_co2_transport}')

            ccs_co2_storage = co2_storage(options_storage.index(self.co2_storage))  # co2 storage price ($_2020/tCO2)
            ccs_cost_storage = ccs_co2_storage * t_co2_fossil * cap_r / 100  # co2 storage cost ($_2020)
            # print(f'ccs storage cost: {ccs_co2_storage}')

            capex_ccs = np.array(cost_ccs['tpc']) * cep(2020)[0] / cep(2008)[0] * np.array(er(country)) / np.array(er('EU_27')) +\
                        (ccs_cost_storage + ccs_cost_transport) * np.array(er(country)) # CAPEX of CCS. convert from 2005 euro to 2020 for country interested
            capex_ccs = capex_ccs /m_steel/np.array(er(country))
            t_capex = t_capex + np.array(capex_ccs)*ccs_vec
            # print(np.array(cost_ccs['tpc']))
            opex_ccs_add = (cost_ccs['operation_management'] + cost_ccs['raw material'] +cost_ccs['utility cost'] ) * np.array(er(country))
                  # material cost of mea

            opex = opex + opex_ccs_add*ccs_vec

            ru = cost_ccs['regeneration utility']*ccs_vec # GJ of utility used in ccs

        t_co2_fossil = t_co2 - m_co2_elec# Direct CO2 emission
        # t_co2 = t_co2_fossil + m_co2_elec
        # carbon tax
        # print(t_co2)

        co2_tax = self.co2_tax * np.array(er(country))  #carbon tax LCU/tonne
        cost_carbon_tax = t_co2_fossil * co2_tax #  LCU paid for carbon tax


        # print( -(m_bof_elec_co2 - m_bf_elec_co2 - m_sinter_elec_co2 -  m_coking_elec_co2)/m_steel)
        print(t_co2/m_steel)
        print(f"m_co2_elec:{( m_co2_elec)/m_steel}")
        print(t_co2_fossil/m_steel)

        return {
            'country': country,
            'years': years,
            'm_steel': m_steel,
            't_co2_fossil': t_co2_fossil / m_steel,
            't_co2': t_co2 / m_steel,
            'co2_coking': co2_coking / m_steel,
            'co2_sintering': co2_sintering / m_steel,
            'co2_bf': co2_bf / m_steel,
            'co2_bof': co2_bof / m_steel,
            'ccs_regeneration_co2': ccs_regeneration_co2 / m_steel,
            'co2_by_product_gas': co2_by_product_gas/m_steel,
            'm_co2_elec': m_co2_elec / m_steel,
            'co2_coke': co2_coke/m_steel,
            'co2_coal': co2_coal/m_steel,
            'co2_ng': co2_ng / m_steel,
            'ub': ub / m_steel,

            'tcost_water': np.array(tcost_water)/m_steel/np.array(er(country)),
            'cost_flux': np.array(cost_flux)/m_steel/np.array(er(country)),
            'cost_elec': np.array(cost_elec)/m_steel/np.array(er(country)),
            'cost_coal': np.array(cost_coal)/m_steel/np.array(er(country)),
            'cost_furnace_oil': np.array(cost_oil)/np.array(er(country)),
            'cost_iron_ore': np.array(cost_iron_ore)/m_steel/np.array(er(country)),
            'cost_scrap': np.array(cost_scrap)/m_steel/np.array(er(country)),
            'opex':np.array(opex)/m_steel/np.array(er(country)),
            'opex_ccs_add':np.array(opex_ccs_add)/m_steel/np.array(er(country)),
            't_capex': np.array(t_capex),
            'capex_ccs': np.array(capex_ccs) / m_steel / np.array(er(country)),
            'cost from carbon tax': cost_carbon_tax/ m_steel/ np.array(er(country)),
            'ru': ru/m_steel,
            't_omt': t_omt/m_steel/np.array(er(country)),
        }

    def figures(self, results):
        opex = results['opex']
        capex = results['t_capex']
        cost = opex + capex + results['cost from carbon tax']

        emissions_by_source = [
            {
                'label':'Coal',
                'color': 'indigo_dark',
                'data': results['co2_coal'],
            },
            {
                'label':'Coke',
                'color': 'black',
                'data': results['co2_coke'],
            },
            {
                'label':'Electricity',
                'color': 'blue',
                'data': results['m_co2_elec'],
            },
            {
                'label':'By_product_gases',
                'color': 'purple',
                'data': results['co2_by_product_gas'],
            },

        ]

        emissions_by_stage = [
            {
                'label': 'Coking',
                'color': 'indigo_dark',
                'data': results['co2_coking'],
            },
            {
                'label': 'Sintering',
                'color': 'indigo_light',
                'data': results['co2_sintering'],
            },
            {
                'label': 'BF',
                'color': 'orange',
                'data': results['co2_bf'],
            },
            {
                'label': 'BOF',
                'color': 'blue',
                'data': results['co2_bof'],
            },
        ]

        detailed_costs = [
            {
                'label': 'Water',
                'color': 'blue',
                'data': results['tcost_water'],
            },
            {
                'label': 'Fluxes',
                'color': 'green',
                'data': results['cost_flux'],
            },
            {
                'label': 'Electricity',
                'color': 'orange',
                'data': results['cost_elec'],
            },
            {
                'label': 'Fossil Fuel',
                'color': 'black',
                'data': results['cost_coal'],
            },
            {
                'label': 'Scrap + Iron Ore',
                'color': 'indigo_dark',
                'data': results['cost_scrap'] + results['cost_iron_ore'],
            },
            {
                'label': 'Operation & Management of BF-BOF',
                'color': 'purple',
                'data': results['t_omt'],
            },
            {
                'label': 'Capital',
                'color': 'yellow',
                'data': capex,
            },
            {
                'label': 'Cost from Carbon Tax',
                'color': 'teel',
                'data': results['cost from carbon tax'],
            },
        ]

        if self.ccs == 'Yes':
            if self.regeneration_u =='NG':
                emissions_by_source += [
                    {
                    'label':'NG',
                    'color': 'steelblue',
                    'data': results['co2_ng'],
                },]
            emissions_by_stage += [{
                'label': 'CCS',
                'color': 'yellow',
                'data': results['ccs_regeneration_co2'],
            }]
            detailed_costs += [{
                'label': 'Operation & Management of CCS',
                'color': 'teal',
                'data': results['opex_ccs_add'],
            },]


        return [
            {
                'label': 'GHG Emissions by Source',
                'unit': 'tonne CO\u2082 / tonne steel',
                'axis': 0,
                'datasets': emissions_by_source,
            },
            {
                'label': 'GHG Emissions by Stage',
                'unit': 'tonne CO\u2082 / tonne steel',
                'axis': 0,
                'datasets': emissions_by_stage,
            },
            {
                'label': 'Costs (broad)',
                'unit': 'USD $ / tonne steel',
                'axis': 0,
                'datasets': [
                    {
                        'label': 'Operating',
                        'color': 'teal_dark',
                        'data': opex,
                    },
                    {
                        'label': 'Capital',
                        'color': 'teal_light',
                        'data': capex,
                    },
                    {
                        'label': 'Cost from Carbon Tax',
                        'color': 'teel',
                        'data': results['cost from carbon tax'],
                    },
                ],
            },
            {
                'label': 'Costs (detailed)',
                'unit': 'USD $ / tonne steel',
                'axis': 0,

                'datasets':detailed_costs,
            },
            {
                'label': 'Total GHG Emissions',
                'unit': 'tonne CO\u2082 / tonne steel',
                'axis': 1,
                'datasets': [
                    {
                        'label': 'Total CO\u2082 Emissions',
                        'data': results['t_co2'],
                    },
                ],
            },
            {
                'label': 'Total Costs',
                'unit': 'USD $',
                'axis': 1,
                'datasets': [
                    {
                        'label': 'Total Cost',
                        'data': cost,
                    },
                ],
            },
            {
                'label': 'Production',
                'unit': 'tonnes',
                'axis': 1,
                'datasets': [
                    {
                        'label': 'Production',
                        'data': results['m_steel'],
                    },
                ],
            },
        ]

    def plot(self, results):
        # print(results['co2_bf'])
        # print(f"tco2: {results['t_co2']}") #, co2_stage: {results['co2_coking']+ results['co2_sintering']+ results['co2_bf'] + results['co2_bof'] }")
        # print(f"co2_source: {results['co2_coal']+ results['co2_coke']+ results['m_co2_elec'] + results['co2_by_product_gas']}")
        # print (f"co2_coal: {results['co2_coal']}, coke: {results['co2_coke']}, elec:{results['m_co2_elec']}, gases: {results['co2_by_product_gas']}")
        # print(f"results: {results}")
        # print(f"co2: {results['t_co2']}) cost from elec: {results['cost_elec']},opex:{results['opex']}; capex:{results['t_capex']}")
        years = results['years']
        # print (f"t_omt: {results['t_omt']}; co2 coking: {results['co2_coking']}, CO2 emission:{results['t_co2']};opex:{results['opex']}; capex:{results['t_capex']};opex_ccs:{results['opex_ccs_add']}; capex_ccs:{results['capex_ccs']};ru: {results['ru']} ")
        if self.ccs == 'Yes':
            #print(f"cost of coking:{results['cost2_coking']}; sintering: {results['cost2_sintering']}; bf: {results['cost2_bf']}; bof:{results['cost2_bof']}")

            #CO2 emission plots
            # plot trajectory line graph for CO2 emission
            plot1 = plt.figure(1)
            plt.plot(years, results['co2_coking'], marker='p', label='Coking', color='darkgoldenrod')
            plt.plot(years, results['co2_sintering'], marker='x', label='Sintering', color='slategrey')
            plt.plot(years, results['co2_bf'], marker='D', label='BF', color='orange')
            plt.plot(years, results['co2_bof'], marker='*', label='BOF', color='blueviolet')
            plt.plot(years, results['ccs_regeneration_co2'], marker='+',
                     label=f'CCS_{self.solvent.upper()}_{self.regeneration_u.upper()}', color='turquoise')
            plt.plot(years, results['t_co2'], marker='s', label='Total', color='red')
            plt.plot(years, results['ub'], linestyle='dashed', label='Allowable CO2 emission upper bound:IEA-SDS',
                     color='forestgreen')
            # plt.vlines(2020, 0, 1800, label='Past/future', color='black', linestyles='dashed')  # plot vertical lines
            plt.xticks(np.arange(min(years), max(years) + 1, 5))
            plt.title(f'CO\u2082 emission for BF-BOF routes:{self.solvent.upper()}_CCS')
            plt.xlabel('Year')
            plt.ylabel('CO\u2082 emissions (tonnes CO\u2082 / tonne steel)')
            plt.legend()

            # capex, opex
            fig, ax = plt.subplots()
            ax.plot(years, results['tcost_water'], marker='s', label='Water', color='royalblue')
            ax.plot(years, results['cost_flux'], marker='d', label='Fluxes', color='green')
            ax.plot(years, results['cost_elec'], marker='x', label='Electricity', color='orange')
            ax.plot(years, results['cost_coal'], marker='p', label='Fossil Fuel', color='olive')
            ax.plot(years, results['cost_iron_ore'] + results['cost_scrap'], marker='+', label='Scrap+Iron Ore',
                    color='purple')
            ax.plot(years, results['cost from carbon tax'], marker='*', label='Cost from Carbon Tax', color='turquoise')
            ax.set_xlabel('Year')
            plt.xticks(np.arange(min(years), max(years) + 1, 5))
            ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))  # use scientific tick-label for y axis.
            plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))  # use scientific tick-label for y axis.
            plt.title(f'OPEX/CAPEX for BF-BOF routes:{self.solvent.upper()}_CCS')
            ax2 = ax.twinx()  # add a second y axis
            ax.plot(years, results['opex'], marker='*', label="Total OPEX", color='red')
            ax.set_ylabel(f"OPEX (USD $/tonne steel", color='black')
            ax2.plot(years, results['t_capex'], marker='o', label="Total CAPEX", color='navy')  # total capex with ccs
            ax2.plot(years, results['capex_ccs'], marker='d',
                     label=f'CAPEX_CCS_{self.solvent.upper()}_{self.regeneration_u.upper()}',
                     color='cornflowerblue')  # additional capex with ccs
            ax2.set_ylabel(f"CAPEX (USD $/tonne steel)", color='navy')
            ax.legend()
            plt.legend()
            # plt.ylim([0, 4000000])  # make sure each route has the same y axis length and interval
            plt.show()

        else:
            # print(
            #     f"cost of coking:{results['cost2_coking']}; sintering: {results['cost2_sintering']}; bf: {results['cost2_bf']}; bof:{results['cost2_bof']};opex:{results['opex']}; capex:{results['t_capex']} ")
            # co2 emission plots
            plot1 = plt.figure(1)
            plt.plot(years, results['t_co2'], marker='s', label='Total', color='red')
            plt.plot(years, results['co2_coking'], marker='p', label='Coking', color='darkgoldenrod')
            plt.plot(years, results['co2_sintering'], marker='x', label='Sintering', color='slategrey')
            plt.plot(years, results['co2_bf'], marker='D', label='BF', color='orange')
            plt.plot(years, results['co2_bof'], marker='*', label='BOF', color='blueviolet')
            plt.plot(years, results['ub'], linestyle='dashed', label='Allowable CO2 emission upper bound:IEA-SDS',
                     color='forestgreen')
            # plt.vlines(2020, 0, 1800, label='Past/future', color='black', linestyles='dashed')  # plot vertical lines
            plt.xticks(np.arange(min(years), max(years) + 1, 5))
            plt.title('CO\u2082 emission for BF-BOF routes: without CCS')
            plt.xlabel('Year')
            plt.ylabel('CO\u2082 emissions (tonnes CO\u2082 / tonne steel)')
            plt.legend()

            # capex, opex plots
            fig, ax = plt.subplots()
            ax.plot(years, results['tcost_water'], marker='s', label='Water', color='royalblue')
            ax.plot(years, results['cost_flux'], marker='d', label='Fluxes', color='green')
            ax.plot(years, results['cost_elec'], marker='x', label='Electricity', color='orange')
            ax.plot(years, results['cost_coal'], marker='p', label='Fossil Fuel', color='olive')
            ax.plot(years, results['cost_iron_ore'] + results['cost_scrap'], marker='+', label='Scrap+Iron Ore',
                    color='purple')
            ax.plot(years, results['opex'], marker='*', label=f'Total OPEX', color='red')
            ax.plot(years, results['cost from carbon tax'], marker='*', label='Cost from Carbon Tax', color='turquoise')
            ax.set_xlabel('Year')
            plt.xticks(np.arange(min(years), max(years) + 1, 5))
            ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))  # use scientific tick-label for y axis.
            plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))  # use scientific tick-label for y axis.
            plt.title('OPEX/CAPEX for BF-BOF routes:without CCS')
            ax2 = ax.twinx()  # add a second y axis
            ax2.plot(years, results['t_capex'], marker='o', label=f'Total CAPEX', color='navy')
            ax.set_ylabel(f"OPEX (USD $/tonne steel)", color='black')
            ax2.set_ylabel(f"CAPEX (USD $/tonne steel)", color='navy')
            ax.legend()
            plt.legend()
            plt.show()

        # plot bar graph
        """import numpy as np
        bloks = ("Coking","Sintering","BF","BOF",'Total')
        x_pos = np.arange(len(bloks))
        emissions =[co2_coking,co2_sintering,co2_bf, co2_bof,t_co2]
        plt.bar(bloks,emissions, align='center', alpha=0.5) # plot bar graph
        plt.xticks(x_pos,bloks)
        plt.ylabel("CO2 emissions (kg CO2/tonne of steel)")
        plt.title("CO2 emission for BF-BOF route")
        plt.show()"""
