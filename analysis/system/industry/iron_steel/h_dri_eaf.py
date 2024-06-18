"""H-DRI-EAF system. source: 1. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019).
2. He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants." Energy Reports 3 (2017): 29-36. page 41
3. https://www.tandfonline.com/doi/pdf/10.1179/174328108X301679?needAccess=true
4. https://www.metallics.org/dri.html
5. (internal communication) Sergey Paltsev et al. Economic Analysis of the hard-to-abate sectors in India
Projection according to both steel production (Shell internal communication) and electricity carbon intensity prediction from IEA SDS"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
from core.common import InputSource
import core.conditionals as conditionals
from core.inputs import OptionsInput, ContinuousInput, PercentInput, Default,Tooltip,InputGroup
import core.validators as validators

from analysis.system.industry.iron_steel.m_hdri_eaf_input import m_fe_eaf
from analysis.system.industry.iron_steel.steel_projectory import steel_route as sr
from analysis.system.industry.iron_steel.m_hdri_eaf_input import m_flux_eaf as mfe
from analysis.system.industry.iron_steel.m_hdri_eaf_input import m_c_eaf as mce
from analysis.system.industry.iron_steel.fuel_type import fuel_type as ft, options as fuel_type_options
from analysis.system.industry.iron_steel.m_hdri_eaf_input import m_water_eaf as mwe
from analysis.system.industry.iron_steel.m_hdri_eaf_input import q_elec_eaf as qea
from analysis.system.industry.iron_steel.m_hdri_input import m_pellet_dri as mpd
from analysis.system.industry.iron_steel.m_hdri_input import m_h2_dri as mhd
from analysis.system.industry.iron_steel.m_hdri_pellet_input import m_iron_fines as mif
from analysis.system.industry.iron_steel.m_hdri_pellet_input import m_flux_pellet as mfp
from analysis.system.industry.iron_steel.m_hdri_pellet_input import m_c_pellet as mcp
from analysis.system.industry.iron_steel.m_hdri_pellet_input import q_elec_pellet as mep
from analysis.system.industry.iron_steel.m_hdri_electrolysis import m_water as mw
from analysis.system.industry.iron_steel.m_hdri_electrolysis import q_elec_water as qew
from analysis.system.industry.iron_steel.m_co2_source import m_co2_source as mcs
from analysis.system.industry.iron_steel.m_e_co2 import m_e_co2 as mec
from analysis.system.industry.iron_steel.project_elec_co2 import elec_co2 as ec
from analysis.system.industry.iron_steel.india_iron_steel_co2emission_prediction import co2_ub
from analysis.system.industry.iron_steel.capex import capex_add as cap
from analysis.system.industry.iron_steel.capex import capexs, capexes
from analysis.system.industry.iron_steel.cepci import cepci_v as cep
from analysis.system.industry.iron_steel.ppp import pppv
from analysis.system.industry.iron_steel.material_cost import c_materials as cm
from analysis.system.industry.iron_steel.material_cost import water as cw
from analysis.system.industry.iron_steel.exchange_rate import exchange_country as er
from analysis.system.industry.iron_steel.linear_elec_projection import linproj
from analysis.system.industry.iron_steel.elec_input import co2_int
from analysis.system.industry.iron_steel.elec_input import user_inputs_ft_cap as elec_inputs

class HDRIEAF(InputSource):

    @classmethod
    def user_inputs(cls):
        cp_options = ['Coal', 'Solar', 'Natural Gas', 'Wind']
        return elec_inputs(cls, cp_options) + [
            ContinuousInput(
                'co2_tax', 'Carbon tax',
                unit = '$/tonne',
                defaults=[Default(50)],
                validators=[validators.numeric(), validators.gte(0)],
            ),
            ContinuousInput(
                'f_scrap', 'Fraction of iron from scrap',
                defaults=[Default(0.26094)],
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
                'fuel_type', 'Fuel type',
                options=fuel_type_options,
                defaults=[Default('H-DRI-EAF')],
                tooltip=Tooltip('Default coal for EAF (reduction agent)')
            ),
            ContinuousInput(
                'f_ng_pellet', 'Fraction of carbon from NG in pellet plant',
                defaults=[Default(0.590428)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(1)],
                tooltip=Tooltip('Fraction of pellet carbon input coming from natural gas')
            ),

            ] +  [
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
                tooltip=Tooltip('Flux; Default prices are with respect to  India in 2022. Due to fluctuation in pricing and location specific costs, user may input price',source='IndiaMart',
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
            ]),
        ]

    def run(self):

        #m_crude_steel = sr('H_DRI_EAF')[0:5] #amount of steel to be produced by chosen route. in the year (2020,2040,5)
        m_crude_steel = pd.Series([1, 1, 1, 1, 1])
        f_scrap = self.f_scrap
        fe_dri = 0.861  # Default DRI Fe content. source 4.
        m_dri = m_fe_eaf(m_crude_steel,f_scrap,fe_dri)['dri'] # tonne dri input in EAF
        m_scrap = m_fe_eaf(m_crude_steel,f_scrap,fe_dri)['scrap'] # tonne scrap input in EAF
        m_carbon_steel = m_fe_eaf(m_crude_steel,f_scrap,fe_dri)['carbon steel'] #tonne carbon steel input in EAF

        m_flux_eaf = mfe(m_crude_steel) # tonne limestone input in EAF
        # print(m_flux_eaf)
        f_ng_eaf = self.f_ng_eaf
        fuel = ft(fuel_type_options.index(self.fuel_type)) # get the fuel type
        c_coal = fuel['c']  # get the c content in fuel
        m_coal_eaf = mce(m_crude_steel,f_ng_eaf,c_coal)['coal'] #tonne of coal input in EAF
        m_ng_eaf = mce(m_crude_steel,f_ng_eaf,c_coal)['ng'] #tonne of ng input in EAF


        m_water_eaf = mwe(m_crude_steel) # tonne water needed in EAF
        # print(m_water_eaf)

        hhv_coal = fuel['hhv']
        q_elec_eaf = qea(m_crude_steel,m_coal_eaf,m_ng_eaf,hhv_coal)
        # print(q_elec_eaf)

        #PELLET PLANT

        # Material/energy input in DRI
        m_pellet = mpd(m_dri) # tonne pellet input in DRI
        # print(m_pellet)

        m_h2 = mhd(m_dri) # tonne H2 input in DRI
        # print(m_h2)

        # Material/energy input in pellet plant
        m_iron_fine = mif(m_pellet) # tonne of fines
        # print(m_iron_fine)

        m_flux_pellet = mfp(m_pellet) # tonne of flux needed
        m_olivine_pellet = 32.62*10**-6* m_pellet /1.40  #tonne olivine needed based on standard 32.62 ton per 1.4 Mton.
        # print(m_flux_pellet)

        f_ng_pellet = self.f_ng_pellet
        m_coal_pellet = mcp(m_pellet,f_ng_pellet,c_coal)['coal'] # tonne coal input in pellet plant
        m_ng_pellet = mcp(m_pellet,f_ng_pellet,c_coal)['ng'] # tonne ng input in ng plant
        q_elec_pellet = mep(m_pellet,m_coal_pellet,m_ng_pellet,hhv_coal) # MJ of electricity input in pellet plant
        # print(q_elec_pellet)

        #Material/Energy input in water electrolyser
        m_water_electrolyser = mw(m_h2) # tonne water input in electrolyser
        # print(m_water_electrolyser)

        q_elec_electrolyser = qew(m_h2) #GJ input in electrolyser.
        # print(q_elec_electrolyser)

        #CO2 emissions
        #EAF
        m_co2_coal_eaf = mcs(m_coal_eaf,c_coal) #CO2 emission from coal input in EAF
        c_ng = 76.41 #C content in NG. default: 76.41. source 1. Assume HHV-ng = 49.5 MJ/kg
        m_co2_ng_eaf = mcs(m_ng_eaf,c_ng) #CO2 emission from ng input in EAF
        elec = ec() # get the electricity trajectory
        country= self.country
        years = elec['years'][20:25]
        c_elec = co2_int(self, years) #method for getting electricity CI
        m_co2_elec_eaf= np.array(q_elec_eaf) * np.array(c_elec) # CO2 emission associated with electricity use in EAF
        m_co2_flux_eaf =  m_flux_eaf*(100.09/44) #flux eaf emissions for limestone
        co2_eaf = m_co2_ng_eaf + m_co2_elec_eaf + m_co2_coal_eaf + m_co2_flux_eaf # total co2 emission from eaf

        #DRI
        co2_dri = np.zeros_like(years) # total co2 emission from dri

        #Pellet plant
        m_co2_coal_pellet = mcs(m_coal_pellet, c_coal) #CO2 emission from coal input in pellet plant
        m_co2_ng_pellet = mcs(m_ng_pellet,c_ng) #CO2 emission from NG input in pellet plant
        m_co2_elec_pellet = np.array(q_elec_pellet) * np.array(c_elec) #CO2 emission associated with electricity use in pellet plant
        m_co2_pellet_flux = m_flux_pellet*(44/100.09)  #flux eaf emissions for limestone
        co2_pellet = m_co2_elec_pellet + m_co2_ng_pellet + m_co2_coal_pellet + m_co2_pellet_flux # total CO2 emission from pellet plant

        #Electrolyser
        m_co2_elec_electrolyser = np.array(q_elec_electrolyser) * np.array(c_elec) #CO2 emission associated with electricity use in electrolyser
        co2_electrolyser = m_co2_elec_electrolyser

        # CO2 emission by source
        co2_coal =  m_co2_coal_eaf + m_co2_coal_pellet
        co2_ng = m_co2_ng_eaf + m_co2_ng_pellet
        co2_electricity = m_co2_elec_eaf + m_co2_elec_pellet + m_co2_elec_electrolyser
        co2_flux = m_co2_flux_eaf + m_co2_pellet_flux
        t_co2 = co2_eaf + co2_dri + co2_pellet + co2_electrolyser
        t_co2_fossil = m_co2_ng_pellet + m_co2_coal_pellet + m_co2_ng_eaf + m_co2_coal_eaf +  m_co2_flux_eaf + m_co2_pellet_flux#more like direct emissions

        #print(f"Pellet plant:{co2_pellet}, Electrolyser: {co2_electrolyser}, H-DRI: {co2_dri},EAF:{co2_eaf},Total: {co2_t}")

        #gettheupperboundofco2emissionaccordingtoIEA-SDSscenario.
        ub=co2_ub(m_crude_steel)#gettheIndiasteelindustryCO2emissionupperboundbysatisfyIEA-SDSscenario
        # print(f"upper bound of co2 emission {ub}")

        #Economic analysis
        # carbon tax
        co2_tax = self.co2_tax * np.array(er(country))  #carbon tax $/tonne
        cost_carbon_tax = t_co2_fossil * co2_tax #  $ paid for carbon tax

        #CAPEX
        cepci1 = cep(2017)[0] # get the base cost year. source: Techno-economic evaluation of innovative steel production technologies (wupperinst.org)
        cepci2 = cep(2020)[0] #get the most up to date value available.
        ppp2 = pppv(country,2020) # get the ppp for the country of interest


        #Pellet plant. Yang, F., J. C. Meerman, and A. P. C. Faaij. "Carbon capture and biomass in industry: A techno-economic analysis and comparison of negative emission options." Renewable and Sustainable Energy Reviews 144 (2021): 111028.
        capacity2_pellet = m_pellet # t pellet needed/y
        capacity2_pellet = capexes['Base Scale'][2]
        n_pp = m_pellet / capacity2_pellet  # number of pellet plants
        cost2_pellet = n_pp * capexs(capacity2_pellet, cepci1, cepci2, ppp2)['Sintering plant']
        # cost2_pellet_add = cap('Sintering plant',capacity2_pellet,cepci1,cepci2,ppp2)['Additional']
        # cost2_pellet = cap('Sintering plant',capacity2_pellet,cepci1,cepci2,ppp2)['Total'] #total cost for producting m_steel ton of steel in specific year


        #Electrolyser plant.
        cost1_electrolyser = 0 # Data absent

        # DRI. Assume the cost is the same as common DRI, which might used syngas instead of H2 as reduction agent
        capacity2_dri = m_dri # amount of dri produced
        capacity2_dri = capexes['Base Scale'][6]
        n_dri = m_dri/ capacity2_dri # number of eaf
        cost2_dri = n_dri * capexs(capacity2_dri, cepci1, cepci2, ppp2)['DRI']
        # cost2_dri_add = cap('DRI',capacity2_dri,cepci1,cepci2,ppp2)['Additional']
        # cost2_dri = cap('DRI',capacity2_dri,cepci1,cepci2,ppp2)['Total']
        #print(f'dri capex {cost2_dri/np.array(er(country))}')

        #EAF
        capacity2_eaf = m_crude_steel # amount of steel produced
        capacity2_eaf = capexes['Base Scale'][8]  # Assume the capacity is the same as base scale.
        n_eaf = m_crude_steel / capacity2_eaf  # number of eaf
        # cost2_eaf_add = cap('EAF',capacity2_eaf,cepci1,cepci2,ppp2)['Additional']
        # cost2_eaf = cap('EAF',capacity2_eaf,cepci1,cepci2,ppp2)['Total']
        cost2_eaf = n_eaf * capexs(capacity2_eaf,cepci1,cepci2,ppp2)['EAF'] # local current unit. depends on ppp2


        #total capex
        #t_capex_add = np.array(cost2_eaf_add) + np.array(cost2_dri_add) + np.array(cost2_pellet_add)
        t_capex = np.array(cost2_eaf) + np.array(cost2_dri) + np.array(cost2_pellet)
        #print(f'total capex:{t_capex/np.array(er(country))}')

        #Economic analysis
        #OPEX
        tc_onm = np.array(m_crude_steel) * 0.8 * np.array(er(country)) #assume steel operation and maintenance cost is $0.8/tonne. source 3.
        tc_ins_loc = np.array(t_capex) * 0.045 # maintenance and labor cost. source 3. Indian Rupee.
        tc_labor = 100*60000/1360000*np.array(m_crude_steel) # assume number of labor needed is linearly correlated to total amount of steel produced. source 3.
        tc_administrative = 0.3 * tc_onm # administrative labor cost. Rupee. source 3.
        t_omt = tc_onm + tc_ins_loc + tc_labor + tc_administrative # operation & management cost of bf-bof

        #OPEX material/energy price

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
            scrap_price_update = self.scrap_price + (y - y_i) * self.scrap_price * (self.scrap_price_change/100)/(y_f - y_i)
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
        #
        # print(f"scrap price: {scrap_price}")

        cost_coal = np.array(coal_price) * (m_coal_pellet + m_coal_eaf) # $
        cost_ng = np.array(ng_price) * (m_ng_pellet + m_ng_eaf)*49.5  #price: usd/GJ
        cost_limestone = np.array(limestone_price) * (m_flux_eaf + m_flux_pellet) + np.array(olive_price) * m_olivine_pellet #$
        cost_iron_ore = np.array(iron_ore_price) * m_iron_fine
        cost_scrap = np.array(scrap_price)* (m_scrap + m_carbon_steel)  # price: usd/t. cost of scrap. assume cost of scrap and carbon steel are the same
        cost_elec = np.array(electricity_price) * (q_elec_eaf + q_elec_electrolyser + q_elec_pellet) #cost of electrcity. without ccs. india's electricity price. unit: usd/GJ
        m_wateri = np.array(m_water_eaf) + np.array(m_water_electrolyser) #default fresh water consumption.
        # print(m_wateri)

        #water cost
        tcost_water = []
        for i, water in enumerate(m_wateri):
            cost_water = cw(water)  #cost of water. ($)
            tcost_water.append(cost_water)  # $
        # print(f'tcost_water: {tcost_water}')
        tcost_fossil = (cost_ng + cost_coal) * np.array(er(country))
        tcost_elec = cost_elec * np.array(er(country))
        tcost_iron_ore = (cost_scrap + cost_iron_ore) * np.array(er(country))
        tcost_flux = cost_limestone * np.array(er(country))
        opex = t_omt + (np.array(cost_coal) + np.array(cost_ng) + np.array(cost_iron_ore) + np.array(cost_limestone) +
                np.array(cost_scrap) + np.array(cost_elec) + tcost_water)*np.array(er(country)) # total operation cost. including material cost, utility cost.
        total_elc  =q_elec_eaf + q_elec_electrolyser + q_elec_pellet
        cc = cost_coal
        ce = cost_elec
        cf= cost_limestone
        co =opex/np.array(er(country))
        # print(tcost_water)

        return {
            'years': years,
            'country': country,

            'm_steel': m_crude_steel,
            'co2_pellet': co2_pellet,
            'co2_electrolyser': co2_electrolyser,
            'co2_dri': co2_dri,
            'co2_eaf': co2_eaf,
            't_co2_fossil': t_co2_fossil,
            'co2_coal': co2_coal,
            'co2_ng': co2_ng,
            'co2_electricity': co2_electricity,
            'co2_flux': co2_flux,
            't_co2': t_co2,
            'ub': ub,
            'tcost_water': tcost_water,
            'tcost_flux': tcost_flux/np.array(er(country)),
            'tcost_elec': tcost_elec/np.array(er(country)),
            'tcost_fossil': tcost_fossil/np.array(er(country)),
            'tcost_iron_ore': tcost_iron_ore/np.array(er(country)),
            'opex': opex/np.array(er(country)),
            't_capex': t_capex/np.array(er(country)),
            'cost from carbon tax': cost_carbon_tax/np.array(er(country)),
            't_omt': t_omt/np.array(er(country)),
            #'t_capex_add': t_capex_add,
        }

    def figures(self, results):
        return [
            {
                'label': 'GHG Emissions by Source',
                'unit': 'tonne CO\u2082 / tonne steel',
                'axis': 0,
                'datasets': [
                    {
                        'label': 'Coal',
                        'color': 'indigo_dark',
                        'data': results['co2_coal'],
                    },
                    {
                        'label':'Natural Gas',
                        'color': 'black',
                        'data': results['co2_ng'],
                    },
                    {
                        'label':'Electricity',
                        'color': 'blue',
                        'data': results['co2_electricity'],
                    },
                    {
                        'label': 'Flux',
                        'color': 'gray',
                        'data': results['co2_flux'],
                    },
                ]

            },
            {
                'label': 'GHG Emissions by Stage',
                'unit': 'tonne CO2 / tonne steel',
                'axis': 0,
                'datasets': [
                    {
                        'label': 'Pellet Plant',
                        'color': 'gray',
                        'data': results['co2_pellet'],
                    },
                    {
                        'label': 'Electrolysis',
                        'color': 'blue',
                        'data': results['co2_electrolyser'],
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
                        'color': 'teal',
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
                        'label': 'Scrap + Ore',
                        'color': 'indigo_dark',
                        'data': results['tcost_iron_ore'],
                    },
                    {
                        'label': 'Operation & Management of H-DRI-EAF',
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
                        'color': 'teal',
                        'data': results['cost from carbon tax'],
                    },
                ],
            },
            {
                'label': 'Total GHG Emissions',
                'unit': 'tonne CO2 / tonne steel',
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

    def plot(self, results):
        # print(f"co2 fossil: {results['t_co2_fossil']}, cost from carbon tax: {results['cost from carbon tax']}")
        years = results['years']
        # print(f" detailed: {results['tcost_water']+ results['t_omt'] +results['t_capex'] + results['tcost_iron_ore'] + results['tcost_fossil'] + results['tcost_elec'] + results['tcost_flux']  } ; total broad:{results['opex'] + results['t_capex']}")
        # print(f"CO2 emission:{results['t_co2']};opex:{results['opex']}; capex:{results['t_capex']} ; total:{results['opex']+results['t_capex']}")
        # print(f"water: {results['tcost_water']}")
        #plot trajectory line graph
        plot1 = plt.figure(1)
        plt.plot(years, results['co2_pellet'], marker='x', label='Pellet plant', color='slategrey')
        plt.plot(years, results['co2_electrolyser'], marker='p', label='Electrolysis', color='blue')
        plt.plot(years, results['co2_dri'], label='DRI', marker='D', color='orange')
        plt.plot(years, results['co2_eaf'], label='EAF', marker='*', color='blueviolet')
        plt.plot(years, results['t_co2'], marker='s', label='Total', color='red')
        plt.plot(years, results['ub'], linestyle='dashed', label='Allowable CO2 emission upper bound:IEA-SDS', color='forestgreen')
        #plt.vlines(2020, 0, 3000, label='Past/future', color='black', linestyles='dashed')  # plot vertical lines
        plt.xticks(np.arange(min(years), max(years)+1, 5))
        plt.xlabel('Year')
        plt.ylabel("CO2 emissions (tonnes)")
        plt.title("CO2 emission for H-DRI-EAF route")
        plt.legend()
        #plt.ylim([0, 650])  # make sure each route has the same y axis length and interval

        # plot trajectory line graph for operation/capital cost
        fig, ax = plt.subplots()
        ax.plot(years, results['tcost_water'], marker='s', label='Water', color='royalblue')
        ax.plot(years, results['tcost_flux'], marker='d', label='Fluxes', color='green')
        ax.plot(years, results['tcost_elec'], marker='x', label='Electricity', color='orange')
        ax.plot(years, results['tcost_fossil'], marker='p', label='Fossil Fuel', color='olive')
        ax.plot(years, results['tcost_iron_ore'], marker='+', label='Scrap', color='purple')
        ax.plot(years, results['opex'], marker='*', label='OPEX', color='red')
        ax.plot(years, results['cost from carbon tax'], marker='*', label='Cost from Carbon Tax', color='turquoise')
        ax2 = ax.twinx() #add a second y axis
        ax2.plot(years, results['t_capex'], marker='o', label='CAPEX', color='navy')
#        ax2.plot(years, results['t_capex_add'], marker='^', label='Additional CAPEX', color='slateblue')
        ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0)) #use scientific tick-label for y axis.
        plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0)) #use scientific tick-label for y axis.
        plt.title('OPEX/CAPEX for H-DRI-EAF routes')
        plt.xticks(np.arange(min(years), max(years) + 1, 5))
        ax.set_xlabel('Year')
        ax.set_ylabel(f"OPEX ($/tonne steel)")
        ax2.set_ylabel(f"CAPEX ($/tonne steel)", color='navy')
        plt.legend()
        ax.legend()
        #plt.ylim([0, 4000000])  # make sure each route has the same y axis length and interval
        plt.show()

        #plot bar graph
        """import numpy as np
        bloks = ("Pellet plant","Electrolyser","H-DRI","EAF",'Total')
        x_pos = np.arange(len(bloks))
        emissions =[co2_pellet,co2_electrolyser,co2_dri, co2_eaf,t_co2]
        plt.bar(bloks,emissions, align='center', alpha=0.5) # plot bar graph
        plt.xticks(x_pos,bloks)"""
