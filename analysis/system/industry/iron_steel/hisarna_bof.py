"""
Functional unit: 1 tonne of steel
HIsarna steelmaking route. source: 1. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019). page 39.
2.He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants." Energy Reports 3 (2017): 29-36.
3. Roussanaly, Simon, et al. "Techno-economic analysis of MEA CO2 capture from a cement kiln–impact of steam supply scenario." Energy Procedia 114 (2017): 6229-6239

"""
#BOF

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from core.common import InputSource
import core.conditionals as conditionals
from core.inputs import OptionsInput, ContinuousInput, PercentInput, Default,Tooltip,InputGroup
import core.validators as validators

from analysis.system.industry.iron_steel.m_input_hisarna_bof import m_input_hisarna_bof as mihb
from analysis.system.industry.iron_steel.steel_projectory import steel_route as sr
from analysis.system.industry.iron_steel.m_co2_hisarna_bof import m_co2_hisarna_bof as mchb
from analysis.system.industry.iron_steel.project_elec_co2 import elec_co2 as ec
from analysis.system.industry.iron_steel.m_input_hisarna import m_input_hisarna as mih
from analysis.system.industry.iron_steel.fuel_type import fuel_type as ft, options as fuel_type_options
from analysis.system.industry.iron_steel.m_co2_hisarna import m_co2_hisarna as mch
from analysis.system.industry.iron_steel.co2_asu import m_co2_asu as ca
from analysis.system.industry.iron_steel.capex import capex_add as capa
from analysis.system.industry.iron_steel.capex import capexs, capexes
from analysis.system.industry.iron_steel.cepci import cepci_v as cep
from analysis.system.industry.iron_steel.ppp import pppv
from analysis.system.industry.iron_steel.material_cost import c_materials as cm
from analysis.system.industry.iron_steel.exchange_rate import exchange_country as er
from analysis.system.industry.iron_steel.material_cost import water as cw
from analysis.system.industry.iron_steel.ccs import ccs, user_inputs as ccs_user_inputs
from analysis.system.industry.iron_steel.india_iron_steel_co2emission_prediction import co2_ub
from analysis.system.industry.cement.ccs_transport_storage import co2_transport, co2_storage, options_storage
from analysis.system.industry.iron_steel.linear_elec_projection import linproj
from analysis.system.industry.iron_steel.elec_input import user_inputs_ft_cap as elec_inputs
from analysis.system.industry.iron_steel.elec_input import co2_int

class HisarnaBOF(InputSource):

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
                'f_pig_iron', 'Fraction of iron from pig iron',
                defaults=[Default(0.83)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(1)],
                tooltip=Tooltip('Fraction of pig iron in iron bearing material input for BOF')
            ),
            ContinuousInput(
                'f_scrap', 'Fraction of iron from scrap in BOF',
                defaults=[Default(0.16)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(1)],
                tooltip=Tooltip('Fraction of scrap in iron bearing material input for BOF')
            ),
            OptionsInput(
                'fuel_type', 'Fuel type',
                options=fuel_type_options,
                defaults=[Default('Hisarna-BOF')],
                tooltip=Tooltip('Default coal for Hisarna-BOF')
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
               defaults=[Default(120.5)],
               validators=[validators.numeric(), validators.gte(0)],
               tooltip=Tooltip(source='Trading Economics',
                               source_link='https://tradingeconomics.com/commodity/iron-ore')
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
                'dolomite_price', 'Dolomite',
                unit='$/tonne',
                defaults=[Default(12.44)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to India in 2020 (assuming same as limestone). Due to fluctuation in pricing and location specific costs, user may input price',
                    source='Indian Bureau of Mines',
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
                'oxygen_price', 'Oxygen',
                unit='$/tonne',
                defaults=[Default(150.8)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='Reuters',
                    source_link='https://www.reuters.com/article/us-health-coronavirus-india-oxygen/india-caps-prices-of-medical-oxygen-amid-rising-covid-19-cases-idUSKBN26H0IO;http://www.airproducts.net.br/products/Gases/gas-facts/conversion-formulas/weight-and-volume-equivalents/oxygen.aspx'
                )
            ),
            ContinuousInput(
                'oxygen_price_change', '% change in oxygen price, 2020-2040',
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
                validators=[validators.numeric(), validators.gte(0), validators.lte(100000)],
                conditionals=[conditionals.input_equal_to('ccs', 'Yes')],
            ),
        ]

    def run(self):
        #m_steel = sr('Innovative_SR_BOF')[0:5] #amount of steel to be produced by chosen route. in the year (2020,2040,5). Assume this HIsarna-BOF is one of the Innovative BF-BOF
        m_steel = pd.Series([1,1,1,1,1]) #normalize to standard production for 1 tonne of steel
        #m_steel = float(input("Amount of steel to be produced tonne, default: 1:"))

        f_scrap = self.f_scrap
        f_pig_iron = 1- f_scrap
        fe_pig_iron = 0.965053 # Assume fixed value. source 2.
        fe_scrap = 0.99 # Assume fixed value. source 2.
        fe_pellet = 0.635 # Assume fixed value. source 2.


        bof_sources = mihb(m_steel,f_pig_iron,f_scrap,fe_pig_iron,fe_scrap,fe_pellet)
        m_pig_iron = bof_sources['pig iron'] # tonne pig iron needed
        m_scrap = bof_sources['scrap'] # tonne scrap needed
        m_pellet = bof_sources['pellet'] # tonne pellet needed
        m_lime_bof = bof_sources['limestone'] # tonne limestone needed
        m_dolomite_bof = bof_sources['dolomite'] # tonne dolomite needed
        q_steam_bof = bof_sources['steam produced'] # GJ of steam produced
        q_elec_bof = bof_sources['elec'] # GJ of elec needed
        v_o2_bof = bof_sources['oxygen'] # Nm3 of oxygen needed

        # CO2 emission in BOF.

        elec = ec() # get the electricity data, default in elec_co2 set to India
        years = elec['years'][20:25] # get the projectory years. x_axis in plot
        country = self.country #get the country name
        co2_elec = co2_int(self, years)
        co2_source_bof = mchb(m_pig_iron,q_elec_bof,fe_pig_iron,co2_elec)
        m_co2_pig_iron = co2_source_bof['pig iron']  # co2 emisison due to pig iron carbon content
        m_co2_elec_bof = co2_source_bof['elec']  # co2 emission due to electricity use in bof
        # print(m_co2_pig_iron)

        #HIsarna
        fuel = ft(fuel_type_options.index(self.fuel_type)) #get the fuel type
        c_coal = fuel['c']/100  # c content in coal
        hhv_coal = fuel['hhv'] #GJ/tonne coal
        # resources needed in Hisarna reactor
        hisarna_sources = mih(m_pig_iron,c_coal,hhv_coal)
        m_coal = hisarna_sources['coal'] # tonne coal needed
        m_iron_ore = hisarna_sources['iron ore'] # tonne iron ore needed
        q_elec_hisarna = hisarna_sources['elec'] #GJ elec
        v_o2_hisarna = hisarna_sources['oxygen'] # Nm3 oxygen

        #CO2 emission from HIsarna
        co2_source_hisarna = mch(m_coal,q_elec_hisarna,c_coal, co2_elec)
        m_coal_co2 = co2_source_hisarna['coal'] # tonne CO2/tonne pig iron emission due to coal used
        m_elec_hisarna_co2 = co2_source_hisarna['elec'] # tonne CO2/tonne pig iron emission due to electricity used

        #m_co2_asu: total co2 emission in air separation unit tonne CO2/1 ton steel
        v_o2 = v_o2_hisarna + v_o2_bof #total oxygen needed in hisarna-bof Nm3/tonne steel
        asu_elec = ca(v_o2,co2_elec) #get asu needed electricity and co2 emissions
        m_asu_co2 = asu_elec['co2'] # tonne CO2 in bof/ tonne steel
        m_asu_o2=asu_elec['o2'] #tonne of o2
        q_elec_asu = asu_elec['elec'] # GJ of electricity

        #m_co2_bof: total CO2 emission in bof
        m_co2_bof = m_co2_elec_bof + m_co2_pig_iron

        m_co2_hisarna_t = m_elec_hisarna_co2 + m_coal_co2
        co2_electricity = m_elec_hisarna_co2 + m_asu_co2 + m_co2_elec_bof
        t_co2 = m_co2_bof + m_co2_hisarna_t + m_asu_co2

        # print(f"CO2_hisarna: {m_co2_hisarna_t}  CO2_bof: {m_co2_bof} CO2_asu: {m_asu_co2} total: {t_co2}")
        # total_elec = q_elec_asu + q_elec_bof + q_elec_hisarna
        # m_co2_elec = total_elec*co2_elec
        # print(f"o2 = {co2_elec}")
###############################################################################

        #Economic analysis
        #CAPEX
        cepci1 = cep(2017)[0] # get the base cost year. source: Techno-economic evaluation of innovative steel production technologies (wupperinst.org)
        cepci2 = cep(2020)[0] #get the most up to date value available.
        ppp2 = pppv(country,2020) # get the ppp for the country of interest

        #ASU source: Yang, F., J. C. Meerman, and A. P. C. Faaij. "Carbon capture and biomass in industry: A techno-economic analysis and comparison of negative emission options." Renewable and Sustainable Energy Reviews 144 (2021): 111028.
        #print(f'm_asu_o2: {m_asu_o2}')
        #capacity2_asu = m_asu_o2 #ton of o2 separated per ton of steel
        capacity2_asu = capexes['Base Scale'][2]
        n_asu = m_asu_o2/capacity2_asu
        #cost2_asu_add = capa('ASU',capacity2_asu,cepci1,cepci2,ppp2)['Additional']
        cost2_asu = n_asu*capexs(capacity2_asu,cepci1,cepci2,ppp2)['ASU'] #total cost for producting m_steel ton of steel in specific year

        #HIsarna
        #print(f'm_pig iron: {m_pig_iron}')
        # capacity2_hisarna = m_pig_iron #amount of pig iron produced
        # cost2_hisarna_add = capa('Hisarna',capacity2_hisarna,cepci1,cepci2,ppp2)['Additional']
        #cost2_hisarna = capa('Hisarna',capacity2_hisarna,cepci1,cepci2,ppp2)['Total']
        capacity2_hisarna = capexes['Base Scale'][5]  # Assume the capacity is the same as base scale.
        n_hisarna = m_pig_iron / capacity2_hisarna  # number of hisarna
        cost2_hisarna = n_hisarna * capexs(capacity2_hisarna, cepci1, cepci2, ppp2)['Hisarna']


        #BOF plant
        # capacity2_bof = m_steel # total amount steel produced. based on steel produciton prediction, this will automatically correlated with the amount of steel produced.
        # cost2_bof_add = capa('BOF',capacity2_bof,cepci1,cepci2,ppp2)['Additional']
        # cost2_bof= capa('BOF',capacity2_bof,cepci1,cepci2,ppp2)['Total'] #the LCU for BOF plant
        # #print(f'bof capex add: {cost2_bof_add}')
        capacity2_bof = capexes['Base Scale'][7]  # Assume the capacity is the same as base scale.
        n_bof = m_steel / capacity2_bof  # number of bof
        cost2_bof = n_bof * capexs(capacity2_bof, cepci1, cepci2, ppp2)['BOF']

        t_co2_fossil = m_coal_co2 #total CO2 emission from fossil fuel consumption in Hisarna
        #m_co2_hisarna: Total CO2 emission in Hisarna
        #Assume this HIsarna-BOF is one of the innovative BF-BOF, which this innovative technology includes the use of CCS

        # t_capex_add = np.array(cost2_asu_add) + np.array(cost2_hisarna_add) + np.array(cost2_bof_add)
        t_capex = np.array(cost2_asu) + np.array(cost2_hisarna) + np.array(cost2_bof)  #total capital investment


        #OPEX
        tc_onm = np.array(m_steel) * 0.8 * np.array(er(country)) #assume steel operation and maintenance cost is $0.8/tonne. source 3.(LCU)
        tc_ins_loc = np.array(t_capex) * 0.045 # maintenance and labor cost. source 3. Indian Rupee.
        tc_labor = 100*60000/1360000*np.array(m_steel)* np.array(er(country)) # assume number of labor needed is linearly correlated to total amount of steel produced. source 3. (LCU)
        tc_administrative = 0.3 * tc_onm # administrative labor cost. Rupee. source 3. (LCU)
        t_omt = tc_onm + tc_ins_loc + tc_labor + tc_administrative # operation & management cost of hisarna-bof (LCU)

        #OPEX material/energy price
        scrap_price = []
        iron_ore_price = []
        limestone_price = []
        dolomite_price = []
        coal_price = []
        electricity_price = []
        oxygen_price = []
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
            dolomite_price_update = self.dolomite_price +  (y - y_i) * self.dolomite_price * (self.dolomite_price_change/100)/(y_f - y_i)
            dolomite_price.append(dolomite_price_update)
            coal_price_update = self.coal_price + (y - y_i) * self.coal_price *  (self.coal_price_change/100)/(y_f - y_i)
            coal_price.append(coal_price_update)
            electricity_price_update = self.electricity_price + (y - y_i) * self.electricity_price * (self.electricity_price_change/100)/(y_f - y_i)
            electricity_price.append(electricity_price_update)
            oxygen_price_update = self.oxygen_price + (y - y_i) * self.oxygen_price * (self.oxygen_price_change/100)/(y_f - y_i)
            oxygen_price.append(oxygen_price_update)
            ng_price_update = self.ng_price + (y - y_i) * self.ng_price * (self.ng_price_change/100)/(y_f - y_i)
            ng_price.append(ng_price_update)
        # print(f"oxygen price: {oxygen_price}")
        #material cost
        cost_coal = np.array(coal_price) * (m_coal) #coal price: usd/t
        # print(f'coal : {cost_coal}')

        m_ng = 0 #default m_ng =0
        cost_ng = np.array(ng_price) * m_ng * 49.5/1000 * np.array(er(country)) #price: usd/GJ
        cost_limestone = np.array(limestone_price) * (m_lime_bof) * np.array(er(country)) #(LCU)
        cost_dolomite = np.array(dolomite_price) *m_dolomite_bof * np.array(er(country)) # (LCU)
        # print('-'*40)
        # print(f'lstone : {m_lime_bof}')
        # print(f'dmite : {cost_limestone}')
        cost_iron_ore = np.array(iron_ore_price) * (m_iron_ore + m_pellet) * np.array(er(country)) #(LCU)
        #print(f'iron ore : {cost_iron_ore}')
        cost_scrap = np.array(scrap_price) * (m_scrap) * np.array(er(country)) # price: usd/t. cost of scrap. assume cost of scrap and carbon steel are the same (LCU)
        #print(f'scrap : {cost_scrap}')
        total_elec= q_elec_asu+q_elec_bof+q_elec_hisarna
        cost_elec = np.array(electricity_price) * (q_elec_asu+q_elec_bof+q_elec_hisarna) * np.array(er(country)) #cost of electrcity. without ccs. india's electricity price. unit: usd/GJ (LCU)
        #print(f'elec: {cost_elec}')
        cost_oxygen = np.array(oxygen_price) * m_asu_o2 * np.array(er(country)) # (LCU)
        tcost_fossil = (cost_ng + cost_coal) #(LCU)
        tcost_elec = cost_elec  #(LCU)
        tcost_iron_ore = (cost_scrap + cost_iron_ore) #(LCU)
        tcost_flux = cost_limestone + cost_dolomite # (LCU)
        # print(f"cost of fossil{tcost_fossil},elec{tcost_elec},iron ore{t_iron_ore},flux{tcost_flux}")

        opex = tc_onm + tc_ins_loc + tc_labor + tc_administrative + tcost_fossil + tcost_elec + tcost_iron_ore + tcost_flux  #total operation cost. including material, O&M, labor, utility cost. (LCU)
        # print(f'opex : {opex/np.array(er(country))}')

        #gettheupperboundofco2emissionaccordingtoIEA-SDSscenario.
        ub=co2_ub(m_steel)#gettheIndiasteelindustryCO2emissionupperboundbysatisfyIEA-SDSscenario
        # print(f"upper bound of co2 emission {ub}")

###############################################################################



        ccs_regeneration_co2 = 0
        capex_ccs = 0
        ru = 0
        opex_ccs = 0
        cost2_ccs = 0
        co2_ccs = 0
        co2_ng = 0
        y = [str(i) for i in years]

        # CCS
        if self.ccs == 'Yes':
            cap_r = self.cap_r
            solvent = self.solvent
            regeneration_u = self.regeneration_u
            ccs_idx = y.index(self.ccs_start)
            # print(ccs_idx)
            ccs_vec = np.concatenate((np.zeros(ccs_idx), np.ones(len(years) - ccs_idx)))
            # print(type(ccs_vec))
            cost_ccs = ccs(t_co2_fossil*ccs_vec, solvent, cap_r, regeneration_u, country)
            #Emissions
            co2_ccs = cost_ccs['CO2']
            t_co2 = t_co2 - t_co2_fossil * (cap_r / 100)*ccs_vec + co2_ccs  # minus amount of co2 captured, plus amount of co2 emitted in ccs
            ccs_regeneration_co2 = co2_ccs
            if regeneration_u == 'NG':
                co2_ng = ccs_regeneration_co2 # co2 emission due to NG used in ccs (tonne)
                #t_co2_fossil = t_co2_fossil - t_co2_fossil * cap_r / 100 + co2_ccs + m_co2_pig_iron # assuming ng as regen fuel
                m_co2_hisarna_t += -(cap_r / 100)*m_coal_co2*ccs_vec
                m_coal_co2 += -(cap_r / 100)*m_coal_co2*ccs_vec
            else:
                co2_electricity += ccs_regeneration_co2 # co2 emission from electricity source (tonne)

            #capex_ccs = np.array(cost_ccs['tpc']) * cep(2020)[0] / cep(2008)[0] * np.array(er(country)) / np.array(er('Euro Zone'))  # CAPEX of CCS. convert from 2005 euro to 2020 for country intereste


            #CCS transportation and storage cost
            co2_transportation_distance = float(self.co2_transportation_distance)  #co2 transport to storage location. (km)
            ccs_co2_transport = co2_transport(co2_transportation_distance) #co2 transportation price ($_2020/tCO2)
            ccs_cost_transport = (ccs_co2_transport * t_co2_fossil * cap_r/100)# co2 transportation cost ($_2020)
            # print(f'ccs transport cost: {ccs_co2_transport}')

            ccs_co2_storage = co2_storage(options_storage.index(self.co2_storage)) #co2 storage price ($_2020/tCO2)
            ccs_cost_storage = ccs_co2_storage * t_co2_fossil * cap_r/100 # co2 storage cost ($_2020)
            # print(f'ccs storage cost: {ccs_co2_storage}')

            capex_ccs = np.array(cost_ccs['tpc']) * cep(2020)[0] / cep(2008)[0] * np.array(er(country)) / np.array(er('EU_27')) +\
                        (ccs_cost_storage + ccs_cost_transport) * np.array(er(country)) # CAPEX of CCS. (Rupee)
            t_capex = t_capex + np.array(capex_ccs)*ccs_vec

            #chose solvent
            opex_ccs = (cost_ccs['operation_management'] + cost_ccs['raw material'] +cost_ccs['utility cost'] ) * np.array(er(country))
            opex = np.array(opex) + np.array(opex_ccs)*ccs_vec

            ru = cost_ccs['regeneration utility']*ccs_vec # GJ of utility used in ccs

            #Modify based on when ccs is implemented

        t_co2_fossil = t_co2- co2_electricity
        # carbon tax
        co2_tax = self.co2_tax * np.array(er(country))  #carbon tax $/tonne
        cost_carbon_tax = t_co2_fossil * co2_tax #  $ paid for carbon tax

        # print(f"t_co2_fossil:{t_co2_fossil}")
        # print(f"coal his:{m_coal_co2}")
        return {
            # ccs costs already in USD
            'years': years,
            'country': country,
            'm_asu_co2': m_asu_co2,
            'm_co2_hisarna_t': m_co2_hisarna_t,
            'm_co2_bof': m_co2_bof,
            'co2_ccs': co2_ccs,
            # 'cost_ccs_CO2': cost_ccs['CO2'],
            't_co2_fossil': t_co2_fossil,
            'co2_coal': m_coal_co2 + m_co2_pig_iron,
            'co2_ng': co2_ng,
            'co2_electricity': co2_electricity,
            't_co2': t_co2,
            'ub': ub/m_steel,
            'tcost_flux': tcost_flux/ np.array(er(country)),
            'tcost_elec': tcost_elec/ np.array(er(country)),
            'tcost_fossil': tcost_fossil/ np.array(er(country)),
            'tcost_iron_ore': tcost_iron_ore/ np.array(er(country)),
            'capex_ccs': np.array(capex_ccs) / np.array(er(country)),
            'opex_ccs': opex_ccs/ np.array(er(country)),
            'opex': opex/np.array(er(country)),
            't_capex': t_capex/ np.array(er(country)),
            'cost from carbon tax': cost_carbon_tax / np.array(er(country)),
            'ru': ru,
            't_omt': t_omt/ np.array(er(country)),
            #'t_capex_add': t_capex_add/ np.array(er(country)),
            'm_steel': m_steel,
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
                'label':'Electricity',
                'color': 'blue',
                'data': results['co2_electricity'],
            },

        ]
        emissions_by_stage = [
            {
                'label': 'Air separation unit',
                'color': 'indigo_dark',
                'data': results['m_asu_co2'],
            },
            {
                'label': 'Hisarna',
                'color': 'indigo_light',
                'data': results['m_co2_hisarna_t'],
            },
            {
                'label': 'BOF',
                'color': 'blue',
                'data': results['m_co2_bof'],
            },
        ]
        detailed_costs = [
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
                'label': 'Operation & Management of Hisarna-BOF',
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
            },]

        if self.ccs == 'Yes':
            if self.regeneration_u == 'NG':
                emissions_by_source += [
                    {
                    'label':'NG',
                    'color': 'steelblue',
                    'data': results['co2_ng'],
                },]
            emissions_by_stage += [{
                'label': 'CCS',
                'color': 'yellow',
                'data': results['co2_ccs'],
            }]
            detailed_costs += [{
                'label': 'Operation & Management of CCS',
                'color': 'teal',
                'data': results['opex_ccs'],
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
                'datasets': detailed_costs,
            },
            {
                'label': 'Total Emissions',
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
        # print(f"co2 fossil: {results['t_co2_fossil']}, cost from carbon tax: {results['cost from carbon tax']}")
        years = results['years']

        print(f"co2 emissions: {results['t_co2']},co2_elec:{results['co2_electricity']} , co2_fossil_fuel:{results['t_co2_fossil'] }")

        #t_opex: {results['opex']}; capex: {results['t_capex']};capex_ccs: {results['capex_ccs']}")
        # print(f"opex: {results['opex']};opex_ccs: {results['opex_ccs']};ru: {results['ru']}")
        # print('-' * 26)


        if self.ccs == 'Yes':
            plot1 = plt.figure(1)
            plt.plot(years, results['m_asu_co2'], marker='o', label='Air separation unit',color='royalblue')
            plt.plot(years, results['m_co2_hisarna_t'], marker='D', label='HIsarna',color='orange')
            plt.plot(years, results['m_co2_bof'], marker ='*', label='BOF',color='blueviolet')
#            plt.plot(years, results['cost_ccs_CO2'],marker = '+', label=f'CCS_{self.solvent.upper()}_{self.regeneration_u.upper()}',color='turquoise')
            plt.plot(years, results['t_co2'], marker = 's', label='Total',color='red')
            plt.plot(years, results['ub'], linestyle='dashed', label='Allowable CO2 emission upper bound:IEA-SDS', color='forestgreen')
            #plt.vlines(2020,0,500,label='Past/future',color='black',linestyles='dashed') #plot vertical lines
            plt.xticks(np.arange(min(years), max(years) + 1, 5))
            plt.title(f'CO2 emission for HIsarna-BOF/Innovative SR-BOF routes: {self.solvent.upper()}_CCS')
            plt.xlabel('Year')
            plt.ylabel('CO2 emissions (million tonnes)')
            plt.legend()
            plt.ylim([0,5]) # make sure each route has the same y axis length and interval

            # plot trajectory line graph for operation cost
            fig, ax = plt.subplots()
            #plt.plot(years, tcost_water, marker='s', label='Water', color='blue')
            ax.plot(years, results['tcost_flux'], marker='d', label='Fluxes', color='green')
            ax.plot(years, results['tcost_fossil'], marker='p', label='Fossil Fuel', color='olive')
            ax.plot(years, results['tcost_iron_ore'], marker='+', label='Scrap', color='purple')
            ax2 = ax.twinx() #add a second y axis
            ax2.plot(years, results['t_capex'], marker='o',label="Total CAPEX", color='navy')
            ax.plot(years, results['opex_ccs'], marker='d', label=f'OPEX_CCS_{self.solvent.upper()}_{self.regeneration_u.upper()}', color='turquoise')
            ax.plot(years, results['opex'], marker='*', label="Total OPEX", color='red')
            ax.plot(years, results['cost from carbon tax'], marker='*', label='Cost from Carbon Tax', color='turquoise')
            plt.xticks(np.arange(min(years), max(years) + 1, 5))
            plt.title(f'OPEX/CAPEX for HIsarna-BOF/Innovative SR-BOF routes: {self.solvent.upper()}_CCS')
            ax.set_xlabel('Year')
            ax.set_ylabel(f"OPEX ($/tonne steel)" , color='black')#{results['country'].title()}'s currency million LCU", color='black')
            ax2.set_ylabel(f"CAPEX ($/tonne steel)" , color='navy')#{results['country'].title()}'s currency million LCU", color='navy')
            ax2.plot(years, results['capex_ccs'], marker='d', label=f'CAPEX_CCS_{self.solvent.upper()}_{self.regeneration_u.upper()}', color='cornflowerblue') #additional capex with ccs
            #ax2.plot(years, results['t_capex_add_ccs'], marker='^', label='Additional CAPEX', color='slateblue')
            ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))  # use scientific tick-label for y axis.
            plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))  # use scientific tick-label for y axis.
            ax.legend()
            plt.legend()
            #plt.ylim([0, 4000000])  # make sure each route has the same y axis length and interval
            plt.show()

        else:
            plot1 = plt.figure(1)
            plt.plot(years, results['m_asu_co2'], marker='o', label='Air separation unit', color='blue')
            plt.plot(years, results['m_co2_hisarna_t'], marker='D', label='HIsarna', color='orange')
            plt.plot(years, results['m_co2_bof'], marker='*', label='BOF', color='blueviolet')
            plt.plot(years, results['t_co2'], marker = 's', label='Total',color='red')
            plt.plot(years, results['ub'], linestyle='dashed', label='Allowable CO2 emission upper bound:IEA-SDS', color='forestgreen')
            #plt.vlines(2020, 0, 1700, label='Past/future', color='black', linestyles='dashed')  # plot vertical lines
            plt.xticks(np.arange(min(years), max(years) + 1, 5))
            plt.title('CO2 emission for HIsarna-BOF/Innovative SR-BOF routes: without CCS')
            plt.xlabel('Year')
            plt.ylabel('CO2 emissions (tonne CO2/tonne of steel)')
            plt.legend()
            plt.ylim([0, 5])  # make sure each route has the same y axis length and interval

            # plot trajectory line graph for operation cost
            fig, ax = plt.subplots()
            #plt.plot(years, tcost_water, marker='s', label='Water', color='blue')
            ax.plot(years, results['tcost_flux'], marker='d', label='Fluxes', color='green')
            ax.plot(years, results['tcost_elec'], marker='x', label='Electricity', color='orange')
            ax.plot(years, results['tcost_fossil'], marker='p', label='Fossil Fuel', color='olive')
            ax.plot(years, results['tcost_iron_ore'], marker='+', label='Scrap', color='purple')
            ax.plot(years, results['opex'], marker='*', label='OPEX', color='red')
            ax2 = ax.twinx()  # add a second y axis
            ax2.plot(years, results['t_capex'], marker='o', label='CAPEX', color='navy')
            ax.set_xlabel('Year')
            ax.set_ylabel(f"OPEX ($/tonne steel)" , color='black') # {results['country'].title()}'s currency million LCU", color='black')
            ax2.set_ylabel(f"CAPEX ($/tonne steel)" , color='navy')#{results['country'].title()}'s currency million LCU", color='navy')
            #ax2.plot(years, results['t_capex_add'], marker='^', label='Additional CAPEX', color='slateblue')
            plt.xticks(np.arange(min(years), max(years) + 1, 5))
            ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))  # use scientific tick-label for y axis.
            plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))  # use scientific tick-label for y axis.
            plt.title('OPEX/CAPEX for HIsarna-BOF/Innovative SR-BOF routes: without CCS')
            ax.legend()
            plt.legend()
            #plt.ylim([0, 4000000])  # make sure each route has the same y axis length and interval
            plt.show()

        #plot bar graph
        """bloks = ("Hisarna","BOF",'Total')
        x_pos = np.arange(len(bloks))
        emissions =[m_co2_hisarna,m_co2_bof,t_co2]
        plt.bar(bloks,emissions, align='center', alpha=0.5) # plot bar graph
        plt.xticks(x_pos,bloks)
        plt.ylabel("CO2 emissions (kg CO2)")
        plt.title("CO2 emission from Hisarna-BOF route")
        plt.show()"""
