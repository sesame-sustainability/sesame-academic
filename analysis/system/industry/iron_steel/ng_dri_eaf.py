"""
Function unit: 1 tonne of steel
DRI - EAF (NG) steel making route.
Sources:
(1) Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019).
Based on ULCORED DRI Reactor
(2) Yang, F., J. C. Meerman, and A. P. C. Faaij. "Carbon capture and biomass in industry:
A techno-economic analysis and comparison of negative emission options." Renewable and Sustainable Energy Reviews 144 (2021): 111028.
(3)“Modeling MIDREX Based Process Configurations for Energy and Emission Analysis - Sarkar - 2018 - steel research international - Wiley Online Library.” https://onlinelibrary.wiley.com/doi/full/10.1002/srin.201700248 (accessed Mar. 14, 2022).
(4)O. Olayebi, “The Midrex Process and the Nigerian Steel Industry,” IJESRT, Nov. 2014, [Online]. Available: https://d1wqtxts1xzle7.cloudfront.net/36208578/58-libre.pdf?1420806474=&response-content-disposition=inline%3B+filename%3DThe_Midrex_Process_and_the_Nigerian_Stee.pdf&Expires=1647312827&Signature=Fz7m4NL0nz3-nPFuYE-HENK6MZ1vgq9KyoCMXxM7HbYNhcwCMsmfAjVYq1veFextt0vb~2UDNYMfSmtGToAF2rol3jH5~K2FhSo6imYp41y3NFA1CaCVstL6vsYyjOi7ioCkIZTRPpZ3b34wFwwr8cDDhx3LIwBOgMObmNNuHnJld3n0PafKyGZO-98s-ZQRK9TXS6WPJNiRUyPSvvCqEuGzNFNiVRwxCdJU1rUQYWgrEfyM9qiRlUIpNTR689YGWnIQjrNgDTOmHCxBFHOG2DprAlRupi4CRH6a6i8loYpESNLv8gAikpbkNcORvnEuyjmQRJsGA3tX13bOZeiCzg__&Key-Pair-Id=APKAJLOHF5GGSLRBV4ZA

1/22/2022
sydney johnson
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from core.common import InputSource
import core.conditionals as conditionals
from core.inputs import OptionsInput, ContinuousInput, PercentInput, Default,Tooltip,InputGroup
import core.validators as validators


from analysis.system.industry.iron_steel.india_iron_steel_co2emission_prediction import co2_ub
from analysis.system.industry.iron_steel.linear_elec_projection import linproj
from analysis.system.industry.iron_steel.m_hdri_eaf_input import m_fe_eaf
from analysis.system.industry.iron_steel.m_hdri_eaf_input import m_flux_eaf as mfe
from analysis.system.industry.iron_steel.m_hdri_eaf_input import m_c_eaf as mce
from analysis.system.industry.iron_steel.fuel_type import fuel_type as ft, options as fuel_type_options
from analysis.system.industry.iron_steel.m_hdri_eaf_input import m_water_eaf as mwe
from analysis.system.industry.iron_steel.m_hdri_eaf_input import q_elec_eaf as qea
from analysis.system.industry.iron_steel.m_ng_dri_input import m_pellet_dri as mpd
from analysis.system.industry.iron_steel.m_ng_dri_input import m_ng_dri as mnd
from analysis.system.industry.iron_steel.co2_asu import m_co2_asu
from analysis.system.industry.iron_steel.project_elec_co2 import elec_co2 as ec
from analysis.system.industry.iron_steel.m_ng_dri_pellet_input import m_iron_fines as mif
from analysis.system.industry.iron_steel.m_ng_dri_pellet_input import m_flux_pellet as mfp
from analysis.system.industry.iron_steel.m_ng_dri_pellet_input import m_c_pellet as mcp
from analysis.system.industry.iron_steel.m_ng_dri_pellet_input import q_elec_pellet as mep
from analysis.system.industry.iron_steel.m_co2_source import m_co2_source as mcs
from analysis.system.industry.iron_steel.capex import capexs, capexes
from analysis.system.industry.iron_steel.cepci import cepci_v as cep
from analysis.system.industry.iron_steel.ppp import pppv
from analysis.system.industry.iron_steel.material_cost import c_materials as cm, water as cw
from analysis.system.industry.iron_steel.exchange_rate import exchange_country as er
from analysis.system.industry.iron_steel.linear_elec_projection import linproj
from analysis.system.industry.iron_steel.elec_input import co2_int
from analysis.system.industry.iron_steel.elec_input import user_inputs_ft_cap as elec_inputs

class NG_DRI_EAF(InputSource):
    @classmethod
    def user_inputs(cls):
        cp_options = ['Coal', 'Solar', 'Natural Gas', 'Wind']
        return elec_inputs(cls, cp_options) + [
            OptionsInput(
                'ng_furn', 'Furnace Type',
                options=['MIDREX','ULCOS'],
                defaults=[Default('MIDREX')],
                tooltip=Tooltip('Type of reduction shaft furnace')
            ),

            ContinuousInput(
                'co2_tax', 'Carbon tax',
                unit = '$/tonne',
                defaults=[Default(50)],
                validators=[validators.numeric(), validators.gte(0)],
            ),
            ContinuousInput(
                'f_scrap', 'Fraction of iron from scrap',
                defaults=[Default(0)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(1)],
                tooltip=Tooltip('Fraction of iron bearing material coming from scrap in EAF')
            ),
            ContinuousInput(
                'f_ng_eaf', 'Fraction of carbon from NG in EAF',
                defaults=[Default(0.3962)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(1)],
                tooltip=Tooltip('Fraction of EAF carbon input coming from natural gas')
            ),
            OptionsInput(
                'fuel_type', 'Fuel Type',
                options=fuel_type_options,
                defaults=[Default('NG-DRI-EAF')],
                tooltip=Tooltip('Default coal for NG-DRI-EAF')
            ),
            ContinuousInput(
                'f_ng_pellet', 'Fraction of carbon from NG in pellet plant',
                defaults=[Default(0.590428)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(1)],
                tooltip=Tooltip('Fraction of pellet carbon input coming from natural gas')
            ),
               ] + [
            InputGroup('mat_prices', '2020 Fuel & Material Input Prices', children=[
            ContinuousInput(
                'scrap_price', 'Scrap',
                unit='$/tonne',
                defaults=[Default(385.11)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='MEPS',
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
                tooltip=Tooltip(
                    'Default prices  are with respect to Iron Ore Fines from India in 2020 . Due to fluctuation in pricing and location specific costs, user may input price',
                    source='Indian Bureau of Mines',
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
                tooltip=Tooltip(
                    'Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='Indian Bureau of Mines',
                    source_link='04272021170955ASPmineral_Dec20_(P)&(U)_Final.pdf (ibm.gov.in)'),
            ),
            ContinuousInput(
                'limestone_price_change', '% change in limestone price, 2020-2040',
                defaults=[Default(0)],
            ),
            ContinuousInput(
                'olive_price', 'Olivine',
                unit='$/tonne',
                defaults=[Default(86.32)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Flux; Default prices are with respect to  India in 2022. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='IndiaMart',
                    source_link='https://www.indiamart.com/proddetail/olivine-sand-22135716862.html')
            ),
            ContinuousInput(
                'olive_price_change', '% change in olive price, 2020-2040',
                defaults=[Default(0)],
            ),
            ContinuousInput(
                'coal_price', 'Coal',
                unit='$/tonne',
                defaults=[Default(120.03)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='Indian Ministry of Coal',
                    source_link='https://coal.nic.in/sites/default/files/2021-03/19-02-2021-nci.pdf')
            ),
            ContinuousInput(
                'coal_price_change', '% change in coal price, 2020-2040',
                defaults=[Default(0)],
            ),
            ContinuousInput(
                'ng_price', 'Natural gas',
                unit='$/GJ',
                defaults=[Default(1.697)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='Indian Ministry of Petroleum & Natural Gas',
                    source_link='https://www.ppac.gov.in/WriteReadData/CMS/202009300542060502504GasPriceCeilingOct2020toMarch2021.pdf')
            ),
            ContinuousInput(
                'ng_price_change', '% change in natural gas price, 2020-2040',
                defaults=[Default(0)],
            ),
            ContinuousInput(
                'electricity_price', 'Electricity',
                unit='$/GJ',
                defaults=[Default(10.6)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='IndiaStat',
                    source_link='https://www.indiastat.com/table/utility-wise-average-rates-of-electricity-supply-and-electricity-duty-tax/month-wise-average-price-volume-electricity-transa/1414631')
            ),
            ContinuousInput(
                'electricity_price_change', '% change in electricity price, 2020-2040',
                defaults=[Default(0)],
            ),
                ]
                       )

        ]
    def run(self):

        #EMISSIONS (Unit Operation Material Inputs, then CO2 Emissions)
        #################

        #CO2 Intensity from Elec
        elec = ec()  # get the electricity trajectory
        country = self.country
        years = elec['years'][20:25]
        co2_elec = co2_int(self, years)  # method for getting electricity CI
        #EAF
        # m_steel = sr('Commercial DRI')[0:5]*0.2
        m_crude_steel = pd.Series([1, 1, 1, 1, 1])
        f_scrap = self.f_scrap
        fe_dri = 0.861 #default composition ( see m_fe_eaf code for source)  https://www.metallics.org/dri.html
        ibm = m_fe_eaf(m_crude_steel,f_scrap,fe_dri)
        m_dri = ibm['dri']  # tonne dri input in EAF
        m_scrap = ibm['scrap']  # tonne scrap input in EAF
        m_carbon_steel = ibm['carbon steel']  # tonne carbon steel input in EAF

        m_flux_eaf = mfe(m_crude_steel)  # tonne limestone input in EAF
        f_ng_eaf = self.f_ng_eaf
        fuel = ft(fuel_type_options.index(self.fuel_type))  # get the fuel type
        c_coal = fuel['c']  # get the c content in fuel
        m_coal_eaf = mce(m_crude_steel, f_ng_eaf, c_coal)['coal']  # tonne of coal input in EAF
        m_ng_eaf = mce(m_crude_steel, f_ng_eaf, c_coal)['ng']  # tonne of ng input in EAF
        c_ng = 76.41  # C content in NG. default: 76.41. source 1. Assume HHV-ng = 49.5 MJ/kg
        m_water_eaf = mwe(m_crude_steel)  # tonne water needed in EAF
        hhv_coal = fuel['hhv']
        q_elec_eaf = qea(m_crude_steel, m_coal_eaf, m_ng_eaf, hhv_coal)
        eaf_o2 = 3.5*10**-2*m_crude_steel #Nm3

        co2_eaf_elec = np.array(co2_elec)*np.array(q_elec_eaf)
        co2_eaf_coal = mcs(m_coal_eaf,c_coal)
        co2_eaf_ng = mcs(m_ng_eaf,c_ng)
        co2_eaf_flux = m_flux_eaf*(44/100.09)  #flux eaf emissions for limestone
        # print(f"co2_eaf_elec: {co2_eaf_elec}, co2_eaf_coal:{co2_eaf_coal},co2_eaf_ng:{co2_eaf_ng}")
        co2_eaf = co2_eaf_elec + co2_eaf_coal + co2_eaf_ng + co2_eaf_flux

        # PELLET PLANT
        ng_furn = self.ng_furn
        m_pellet = mpd(m_dri,ng_furn)
        # Material/energy input in pellet plant
        m_iron_fine = mif(m_pellet)  # tonne of fine
        m_flux_pellet = mfp(m_pellet)  # tonne of flux needed
        m_olivine_pellet = 29.79 * 10 ** -6 * m_pellet / 1.13  # tonne olivine needed based on standard 32.62 ton per 1.4 Mton.

        f_ng_pellet = self.f_ng_pellet
        m_coal_pellet = mcp(m_pellet, f_ng_pellet, c_coal)['coal']  # tonne coal input in pellet plant
        m_ng_pellet = mcp(m_pellet, f_ng_pellet, c_coal)['ng']  # tonne ng input in ng plant
        q_elec_pellet = mep(m_pellet, m_coal_pellet, m_ng_pellet, hhv_coal)  # MJ of electricity input in pellet plant

        m_co2_coal_pellet = mcs(m_coal_pellet, c_coal)  # CO2 emission from coal input in pellet plant
        m_co2_ng_pellet = mcs(m_ng_pellet, c_ng)  # CO2 emission from NG input in pellet plant
        m_co2_elec_pellet = np.array(q_elec_pellet) * np.array(co2_elec)  # CO2 emission associated with electricity use in pellet plant
        co2_pellet = m_co2_elec_pellet + m_co2_ng_pellet + m_co2_coal_pellet  # total CO2 emission from pellet p

        # DRI

        dri_ng_amt = mnd(m_dri,ng_furn)  # natural gas in GJ/t DRI
        if ng_furn == 'ULCOS':
            dri_elec = 0.21*m_dri # GJ
            dri_o2 = 1.57*10**2*m_crude_steel #Nm3
        else: #MIDREX
            dri_elec = 95*0.0036*m_dri #source 4
            dri_o2 = 0
        co2_dri_ng = np.array(dri_ng_amt) * np.array(pd.Series(0.0566, index=[0, 1, 2, 3, 4]))  # source 1  0.0566 tCo2/GJ of natural gas
        co2_dri_elec = np.array(dri_elec) * np.array(co2_elec)
        # co2_dri_ng = np.array(dri_ng_amt)*np.array(pd.Series(0.0566,index=[0,1,2,3,4]))# source 1  tCo2/GJ
        # print(f"dri_ng = {co2_dri_ng}")
        co2_dri = co2_dri_elec + co2_dri_ng
        # print(co2_dri)

        #ASU
        t_o2 = dri_o2 + eaf_o2
        asu = m_co2_asu(t_o2,co2_elec)
        co2_asu = asu['co2']  # tonne CO2 in bof/ tonne steel
        m_asu_o2 = asu['o2']  # tonne of o2
        q_elec_asu = asu['elec']  # GJ of electricity


        #total emissions
        # print(f"co2_eaf:{co2_eaf} co2_pellet:{co2_pellet},co2_dri:{co2_dri},co2_asu:{co2_asu}")
        t_co2 = co2_eaf + co2_pellet + co2_dri + co2_asu
        indirect = co2_asu + co2_eaf_elec + co2_dri_elec + m_co2_elec_pellet
        direct = t_co2 - indirect

        #CO2 Emission by Source
        co2_coal = co2_eaf_coal + m_co2_coal_pellet
        co2_ng = co2_eaf_ng + co2_dri_ng + m_co2_ng_pellet

        # print(t_co2)
        # print(co2_coal+ co2_ng + indirect)
        #ub from IEA
        ub = co2_ub(m_crude_steel)

        # print(f"t_co2:{t_co2}. co2_indirect:{indirect}, co2_direct:{direct}")


        ##########################################################
        #Economic Analysis
        # carbon tax
        co2_tax = self.co2_tax * np.array(er(country)) #carbon tax $/tonne
        cost_carbon_tax = direct * co2_tax #  $ paid for carbon tax

        #CAPEX

        #needed values
        cepci1 = cep(2017)[0]  # get the base cost year. source: Techno-economic evaluation of innovative steel production technologies (wupperinst.org)
        cepci2 = cep(2020)[0]  # get the most up to date value available.
        ppp2 = pppv(country, 2020)  # get the ppp for the country of interest

        #DRI (not ULCORED)
        # DRI. Assume the cost is the same as common DRI, which might used syngas instead of H2 as reduction agent
        capacity2_dri = m_dri  # amount of dri produced
        capacity2_dri = capexes['Base Scale'][6]
        n_dri = m_dri / capacity2_dri  # number of eaf
        cost2_dri = n_dri * capexs(capacity2_dri, cepci1, cepci2, ppp2)['DRI']

        #Pellet Plant
         # Yang, F., J. C. Meerman, and A. P. C. Faaij. "Carbon capture and biomass in industry: A techno-economic analysis and comparison of negative emission options." Renewable and Sustainable Energy Reviews 144 (2021): 111028.
        capacity2_pellet = m_pellet  # t pellet needed/y
        capacity2_pellet = capexes['Base Scale'][2]
        n_pp = m_pellet / capacity2_pellet  # number of pellet plants
        cost2_pellet = n_pp * capexs(capacity2_pellet, cepci1, cepci2, ppp2)['Sintering plant']

        # EAF
        capacity2_eaf = m_crude_steel  # amount of steel produced
        capacity2_eaf = capexes['Base Scale'][8]  # Assume the capacity is the same as base scale.
        n_eaf = m_crude_steel / capacity2_eaf  # number of eaf
        # cost2_eaf_add = cap('EAF',capacity2_eaf,cepci1,cepci2,ppp2)['Additional']
        # cost2_eaf = cap('EAF',capacity2_eaf,cepci1,cepci2,ppp2)['Total']
        cost2_eaf = n_eaf * capexs(capacity2_eaf, cepci1, cepci2, ppp2)['EAF']  # local current unit. depends on ppp2

        # total capex
        # t_capex_add = np.array(cost2_eaf_add) + np.array(cost2_dri_add) + np.array(cost2_pellet_add)
        t_capex = np.array(cost2_eaf) + np.array(cost2_dri) + np.array(cost2_pellet)

        # Economic analysis
        # OPEX
        scrap_price = []
        iron_ore_price = []
        limestone_price = []
        olive_price = []
        coal_price = []
        electricity_price = []
        ng_price = []
        y_i = 2020 #initial/baseline year
        y_f = 2040 # final year

        for y in years:
            scrap_price_update = self.scrap_price + (y - y_i) * self.limestone_price * (self.scrap_price_change/100)/(y_f - y_i)
            scrap_price.append(scrap_price_update)
            iron_ore_price_update = self.iron_ore_price + (y - y_i) * self.iron_ore_price * (self.iron_ore_price_change/100)/(y_f - y_i)
            iron_ore_price.append(iron_ore_price_update)
            limestone_price_update = self.limestone_price +  (y - y_i) * self.limestone_price * (self.limestone_price_change/100)/(y_f - y_i)
            limestone_price.append(limestone_price_update)
            olive_price_update = self.olive_price +  (y - y_i) * self.olive_price * (self.olive_price_change/100)/(y_f - y_i)
            olive_price.append(olive_price_update)
            coal_price_update = self.coal_price + (y - y_i) * self.coal_price *  (self.coal_price_change/100)/(y_f - y_i)
            coal_price.append(coal_price_update)
            electricity_price_update = self.electricity_price + (y - y_i) * self.electricity_price * (self.electricity_price_change/100)/(y_f - y_i)
            electricity_price.append(electricity_price_update)
            ng_price_update = self.ng_price + (y - y_i) * self.ng_price * (self.ng_price_change/100)/(y_f - y_i)
            ng_price.append(ng_price_update)
        # print(f"scrap price: {scrap_price}")

        tc_onm = np.array(m_crude_steel) * 0.8 * np.array(er(country))  # assume steel operation and maintenance cost is $0.8/tonne. source 3.
        tc_ins_loc = np.array(t_capex) * 0.045  # maintenance and labor cost. source 3. Indian Rupee.
        tc_labor = 100 * 60000 / 1360000 * np.array(
            m_crude_steel)  # assume number of labor needed is linearly correlated to total amount of steel produced. source 3.
        tc_administrative = 0.3 * tc_onm  # administrative labor cost. Rupee. source 3.
        t_omt = tc_onm + tc_ins_loc + tc_labor + tc_administrative  # operation & management cost of bf-bof

        cost_coal =np.array(coal_price) * (m_coal_pellet + m_coal_eaf)  # coal price: usd/t. the total steel produced in is million ton scale
        cost_ng = np.array(ng_price) * ((m_ng_pellet + m_ng_eaf) * 49.5 + dri_ng_amt)  # price: usd/GJ
        cost_limestone = np.array(limestone_price) * (m_flux_eaf + m_flux_pellet) + np.array(olive_price) * m_olivine_pellet  # $
        cost_iron_ore = np.array(iron_ore_price) * m_iron_fine
        cost_scrap = np.array(scrap_price) * (m_scrap + m_carbon_steel)  # price: usd/t. cost of scrap. assume cost of scrap and carbon steel are the same
        cost_elec = np.array(electricity_price) * (q_elec_eaf + q_elec_pellet+dri_elec)  # cost of electrcity. without ccs. india's electricity price. unit: usd/GJ
        m_wateri = np.array(m_water_eaf)   # default fresh water consumption.

        # water cost
        tcost_water = []
        for i, water in enumerate(m_wateri):
            cost_water = cw(water)  # cost of water. ($)
            tcost_water.append(cost_water)  # $
        # print(f'tcost_water: {tcost_water}')
        tcost_fossil = (cost_ng + cost_coal) * np.array(er(country))
        tcost_elec = cost_elec * np.array(er(country))
        tcost_iron_ore = (cost_scrap + cost_iron_ore) * np.array(er(country))
        tcost_flux = cost_limestone * np.array(er(country))
        opex = t_omt + (np.array(cost_coal) + np.array(cost_ng) + np.array(cost_iron_ore) + np.array(cost_limestone) +
                        np.array(cost_scrap) + np.array(cost_elec) + tcost_water) * np.array(
            er(country))  # total operation cost. including material cost, utility cost.
        total_elc = q_elec_eaf + q_elec_pellet
        cc = cost_coal
        ce = cost_elec
        cf = cost_limestone
        co = opex / np.array(er(country))


        results = {
            'm_steel': m_crude_steel,
            'years': years,
            'country': country,
            'co2_asu': co2_asu,
            'co2_dri': co2_dri,
            'co2_eaf': co2_eaf,
            'co2_pellet': co2_pellet,
            't_co2_fossil': direct,
            't_co2_indirect':indirect,
            't_co2': t_co2,
            'co2_ng':co2_ng,
            'co2_coal':co2_coal,
            'co2_flux': co2_eaf_flux,
            'ub': ub,
            'tcost_water': tcost_water / np.array(er(country)),
            'tcost_flux': tcost_flux / np.array(er(country)),
            'tcost_elec': tcost_elec / np.array(er(country)),
            'tcost_fossil': tcost_fossil / np.array(er(country)),
            'tcost_iron_ore': tcost_iron_ore / np.array(er(country)),
            'opex': opex / np.array(er(country)),
            't_capex': t_capex / np.array(er(country)),
            'cost from carbon tax': cost_carbon_tax / np.array(er(country)),
            't_omt': t_omt / np.array(er(country)),
        }
        return results

    def figures(self, results):
        emissions_by_source = [
            {
                'label': 'Coal',
                'color': 'indigo_dark',
                'data': results['co2_coal'],
            },
            {
                'label': 'Natural Gas',
                'color': 'black',
                'data': results['co2_ng'],
            },
            {
                'label': 'Electricity',
                'color': 'blue',
                'data': results['t_co2_indirect'],
            },
            {
                'label': 'Flux',
                'color': 'gray',
                'data': results['co2_flux'],
            },

        ]
        return [
                        {
                'label': 'GHG Emissions by Source',
                'unit': 'tonne CO\u2082 / tonne steel',
                'axis': 0,
                'datasets': emissions_by_source,
            },
            {
                'label': 'GHG Emissions by Source',
                'unit': 'tonne CO\u2082 / tonne steel',
                'axis': 0,
                'datasets': emissions_by_source,
            },
            {
                'label': 'GHG Emissions by Stage',
                'unit': 'tonne CO\u2082  / tonne steel',
                'axis': 0,
                'datasets': [
                    {
                        'label': 'Pellet Plant',
                        'color': 'gray',
                        'data': results['co2_pellet'],
                    },
                    {
                        'label': 'ASU',
                        'color': 'blue',
                        'data': results['co2_asu'],
                    },
                    {
                        'label': 'DRI',
                        'color': 'orange',
                        'data': results['co2_dri'],
                    },
                    {
                        'label': 'EAF',
                        'color': 'indigo_dark',
                        'data': results['co2_eaf'],
                    },
                ],
            },
            {
                'label': 'Costs (broad)',
                'unit': 'USD / tonne steel',
                'axis': 0,
                'datasets': [
                    {
                        'label': 'Operating',
                        'color': 'teal_dark',
                        'data': results['opex'],
                    },
                    {
                        'label': 'Capital',
                        'color': 'teal_light',
                        'data': results['t_capex'],
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
                'unit': 'USD / tonne steel',
                'axis': 0,
                'datasets': [
                    {
                        'label': 'Water',
                        'color': 'blue',
                        'data': results['tcost_water'],
                    },
                    {
                        'label': 'Fluxes',
                        'color': 'green',
                        'data': results['tcost_flux'],
                    },
                    {
                        'label': 'Electricity',
                        'color': 'orange',
                        'data': results['tcost_elec'],
                    },
                    {
                        'label': 'Fossil Fuel',
                        'color': 'black',
                        'data': results['tcost_fossil'],
                    },
                    {
                        'label': 'Scrap',
                        'color': 'indigo_dark',
                        'data': results['tcost_iron_ore'],
                    },
                    {
                        'label': 'Operation & Management of NG-DRI-EAF',
                        'color': 'purple',
                        'data': results['t_omt'],
                    },
                    {
                        'label': 'Capital',
                        'color': 'yellow',
                        'data': results['t_capex'],
                    },
                    {
                        'label': 'Cost from Carbon Tax',
                        'color': 'teel',
                        'data': results['cost from carbon tax'],
                    },
                ],
            },
            {
                'label': 'Total GHG Emissions',
                'unit': 'tonne CO\u2082  / tonne steel',
                'axis': 1,
                'datasets': [
                    {
                        'label': 'Total CO2 Emissions',
                        'data': results['t_co2'],
                    },
                ],
            },
            {
                'label': 'Total Costs',
                'unit': 'USD',
                'axis': 1,
                'datasets': [
                    {
                        'label': 'Total Cost',
                        'data': results['opex'] + results['t_capex'] + results['cost from carbon tax'],
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
    def plot(self,results):
        # print(f"co2 fossil: {results['t_co2_fossil']}, cost from carbon tax: {results['cost from carbon tax']}")
        years = results['years']
        # print(f"CO2 emission:{results['t_co2']}") #;opex:{results['opex']}; capex:{results['t_capex']} ")
        # plot trajectory line graph
        plot1 = plt.figure(1)
        plt.plot(years, results['co2_pellet'], marker='x', label='Pellet plant', color='slategrey')
        plt.plot(years, results['co2_asu'], marker='p', label='ASU', color='blue')
        plt.plot(years, results['co2_dri'], label='DRI', marker='D', color='orange')
        plt.plot(years, results['co2_eaf'], label='EAF', marker='*', color='blueviolet')
        plt.plot(years, results['t_co2'], marker='s', label='Total', color='red')
        plt.plot(years, results['ub'], linestyle='dashed', label='Allowable CO2 emission upper bound:IEA-SDS',
                 color='forestgreen')
        # plt.vlines(2020, 0, 3000, label='Past/future', color='black', linestyles='dashed')  # plot vertical lines
        plt.xticks(np.arange(min(years), max(years) + 1, 5))
        plt.xlabel('Year')
        plt.ylabel("CO2 emissions (tonnes)")
        plt.title("CO2 emission for NG-DRI-EAF route")
        plt.legend()


        fig, ax = plt.subplots()
        ax.plot(years, results['tcost_water'], marker='s', label='Water', color='royalblue')
        ax.plot(years, results['tcost_flux'], marker='d', label='Fluxes', color='green')
        ax.plot(years, results['tcost_elec'], marker='x', label='Electricity', color='orange')
        ax.plot(years, results['tcost_fossil'], marker='p', label='Fossil Fuel', color='olive')
        ax.plot(years, results['tcost_iron_ore'], marker='+', label='Scrap', color='purple')
        ax.plot(years, results['opex'], marker='*', label='OPEX', color='red')
        ax.plot(years, results['cost from carbon tax'], marker='*', label='Cost from Carbon Tax', color='turquoise')
        ax2 = ax.twinx()  # add a second y axis
        ax2.plot(years, results['t_capex'], marker='o', label='CAPEX', color='navy')
        #        ax2.plot(years, results['t_capex_add'], marker='^', label='Additional CAPEX', color='slateblue')
        ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))  # use scientific tick-label for y axis.
        plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))  # use scientific tick-label for y axis.
        plt.title('OPEX/CAPEX for NG-DRI-EAF routes')
        plt.xticks(np.arange(min(years), max(years) + 1, 5))
        ax.set_xlabel('Year')
        ax.set_ylabel(f"OPEX ($/tonne steel)")
        ax2.set_ylabel(f"CAPEX ($/tonne steel)", color='navy')
        plt.legend()
        ax.legend()
        # plt.ylim([0, 4000000])  # make sure each route has the same y axis length and interval
        plt.show()
