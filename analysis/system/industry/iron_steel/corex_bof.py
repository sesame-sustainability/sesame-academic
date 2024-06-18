"""
Functional unit: 1 tonne of hot metal.
model COREX
resources: 1. Song, Jiayuan, et al. "Comparison of energy consumption and CO2 emission for three steel production
routes—Integrated steel plant equipped with blast furnace, oxygen blast furnace or COREX." Metals 9.3 (2019): 364.
2. Techno-economic evaluation of innovative steel production technologies (wupperinst.org)
3. Yang, F., J. C. Meerman, and A. P. C. Faaij. "Carbon capture and biomass in industry: A techno-economic analysis and comparison of negative emission options." Renewable and Sustainable Energy Reviews 144 (2021): 111028.
4. Roussanaly, Simon, et al. "Techno-economic analysis of MEA CO2 capture from a cement kiln–impact of steam supply scenario." Energy Procedia 114 (2017): 6229-6239

Default values used in this model are from the above resources"""

import matplotlib.pyplot as plt
import numpy as np
import json
import pandas as pd
from core.common import InputSource
import core.conditionals as conditionals
from core.inputs import OptionsInput, ContinuousInput, PercentInput, Default,Tooltip,InputGroup
import core.validators as validators

from analysis.system.industry.iron_steel.steel_projectory import steel_route
from analysis.system.industry.iron_steel.material_corex_bof import m_corex_bof as mcb
from analysis.system.industry.iron_steel.fuel_type import fuel_type as ft, options as fuel_type_options
from analysis.system.industry.iron_steel.project_elec_co2 import elec_co2 as ec
from analysis.system.industry.iron_steel.linear_elec_projection import linproj
from analysis.system.industry.iron_steel.capex import capexs, capexes
from analysis.system.industry.iron_steel.cepci import cepci_v as cep
from analysis.system.industry.iron_steel.ppp import pppv
from analysis.system.industry.iron_steel.ccs import ccs, user_inputs as ccs_user_inputs
from analysis.system.industry.iron_steel.exchange_rate import exchange_country as er
from analysis.system.industry.iron_steel.ccs_transport_storage import co2_transport, co2_storage, options_storage
from analysis.system.industry.iron_steel.elec_input import user_inputs_ft_cap as elec_inputs
from analysis.system.industry.iron_steel.elec_input import co2_int

class COREXBOF(InputSource):

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
                'f_scrap', 'BOF: Fraction of iron from scrap',
                defaults=[Default(0.137)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(1)],
                tooltip=Tooltip('Fraction of scrap in iron bearing material input for BOF. For India (BF/BOF): 6.4-25%',
                source='Shakti Foundation (2019)',
                source_link='https://shaktifoundation.in/wp-content/uploads/2020/03/Resource-efficiency-in-the-steel-and-paper-sectors.pdf')

            ),
            ContinuousInput(
                'fe_scrap', 'Iron content in scrap',
                defaults=[Default(0.99)],
                validators=[validators.numeric(), validators.gte(0.25), validators.lte(1)],
                tooltip=Tooltip('Range: 0.97-0.99')
            ),
            ContinuousInput(
                'fe_hm', 'Iron content in hot metal',
                defaults=[Default(0.9485)],
                validators=[validators.numeric(), validators.gte(0.5), validators.lte(1)],
                tooltip=Tooltip('Range: 0.95-0.97')
            ),
            ContinuousInput(
                'fe_ore', 'Iron content in iron ore',
                defaults=[Default(0.6186)],
                validators=[validators.numeric(), validators.gte(0.4), validators.lte(1)],
                tooltip=Tooltip('Range: 0.55 - 0.635')
            ),
            ContinuousInput(
                'fc_coke', 'COREX: Fraction of carbon from coke',
                defaults=[Default(0.0046)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(0.5)],
                tooltip=Tooltip('Of total carbon, reducing ore, the fraction from coke. Range: 0-0.05')
            ),
            OptionsInput(
                'fuel_type', 'Fuel type',
                defaults=[Default('COREX-BOF')],
                options=fuel_type_options,
                tooltip=Tooltip('Default coal for Corex')

            ),
            ContinuousInput(
                'f_energy_corex', 'COREX: Allocation of energy used in COREX (/off-gas by products) [Range: 0.4-0.52]',
                defaults=[Default(0.4945)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(1)],
                tooltip=Tooltip('Assuming of the gases released from COREX, what fraction is repurposed for offsite electricity generation or other industry consumption')
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
                'coke_price', 'Coke',
                unit='$/tonne',
                defaults=[Default(120.03)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Default prices  are with respect to  India in 2020, assuming coal price. Due to fluctuation in pricing and location specific costs, user may input price',
                    source='Indian Ministry of Coal',
                    source_link='https://coal.nic.in/sites/default/files/2021-03/19-02-2021-nci.pdf')
            ),
            ContinuousInput(
                'coke_price_change', '% change in coke price, 2020-2040',
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
                'oxygen_price', 'Oxygen',
                unit='$/tonne',
                defaults=[Default(150.8)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip('Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price',source='Reuters', source_link='https://www.reuters.com/article/us-health-coronavirus-india-oxygen/india-caps-prices-of-medical-oxygen-amid-rising-covid-19-cases-idUSKBN26H0IO;http://www.airproducts.net.br/products/Gases/gas-facts/conversion-formulas/weight-and-volume-equivalents/oxygen.aspx'
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
        ] + ccs_user_inputs() + [
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
                validators=[validators.numeric(), validators.gte(0), validators.lte(100000)],
            ),
        ]

    def run(self):
       # m_steel = steel_route('Innovative_SR_BOF')[0:5] #amount of steel to be produced by chosen route. in the year (2020,2040,5)
        m_steel = pd.Series([1, 1, 1, 1, 1])
        f_scrap = self.f_scrap
        fe_hm = self.fe_hm
        fe_ore = self.fe_ore
        fe_scrap = self.fe_scrap
        fc_coke = self.fc_coke
        f_energy_corex = self.f_energy_corex

        fuel = ft(fuel_type_options.index(self.fuel_type)) #get fuel type
        c_coal = np.array(fuel['c'])/100 # c content of fuel
        hhv_coal = np.array(fuel['hhv']) # HHV of fuel

        # material, energy flow
        material_energy = mcb(m_steel,f_scrap, fe_hm,fe_ore, fe_scrap, fc_coke, c_coal, hhv_coal,f_energy_corex)
        m_scrap = material_energy['m_scrap'] #tonne of scrap
        m_ore = material_energy['m_ore'] #tonne of ore
        m_hot_metal = material_energy['m_hot_metal'] #tonne of hot metal

        m_lim_corex = material_energy['m_lim_corex'] #tonne of lime used in corex
        m_lim_bof = material_energy['m_lim_bof'] #tonne of lime used in bof

        m_coke = material_energy['m_coke'] #tonne of coke
        m_coal = material_energy['m_coal'] #tonne of coal

        m_coke_corex = material_energy['m_coke_corex'] #tonne of coke used in corex
        m_coal_corex = material_energy['m_coal_corex'] #tonne of coal used in bof

        m_o2_corex = material_energy['m_o2_corex'] #tonne of oxygen used in corex
        m_o2_bof = material_energy['m_o2_bof'] #tonne of oxygen used in bof

        elec_corex = material_energy['elec_corex'] # GJ of electricity for corex
        elec_bof = material_energy['elec_bof'] #GJ of electricity for bof
        elec_lim_corex = material_energy['elec_lim_corex'] #GJ of electricity for limemaking in corex
        elec_lim_bof = material_energy['elec_lim_bof'] #GJ of electricity for climemaking in bof
        elec_oxygen_corex = material_energy['elec_oxygen_corex']#GJ of electricity for oxygen production for corex
        elec_oxygen_bof = material_energy['elec_oxygen_bof']#GJ of electricity for oxygen production for bof
        # print(f"scrap:{m_scrap},ore:{m_ore}, hot metal: {m_hot_metal}, lim corex:{m_lim_corex}, lim bof:{m_lim_bof}")
        # print(f"coke: {m_coke}, coal:{m_coal}, coke corex:{m_coke_corex}, coal corex:{m_coal_corex},elec corex:{elec_corex}")
        # print(f"elec bof:{elec_bof},elec lim corex:{elec_lim_corex},elec lim bof: {elec_lim_bof},elec o2 corex:{elec_oxygen_corex},elec o2 bof:{elec_oxygen_bof}")

        #CO2 emissions
        c_coke = 0.8655 # carbon content of coke
        m_co2_coke_corex = m_coke_corex * np.array(c_coke)*44/12 #tonne CO2 emission from coke allocated to corex
        m_co2_coal_corex = m_coal_corex * np.array(c_coal)*44/12 #tonne CO2 emission from coal allocated to corex

        elec = ec() # get the electricity data, default in project_elec_co2 set to India
        years = elec['years'][20:25] # get the projectory years. x_axis in plot
        country = self.country #get the country name
        co2_elec = co2_int(self, years)

        m_co2_elec_corex = elec_corex * np.array(co2_elec) # tonne of CO2 emission due to elec use in COREX.
        m_co2_elec_bof = elec_bof * np.array(co2_elec) # tonne of CO2 emission due to elec use in bof.
        m_co2_elec_lim_corex = elec_lim_corex * np.array(co2_elec) # tonne of CO2 emission due to elec use in limemaking for corex.
        m_co2_elec_lim_bof = elec_lim_bof * np.array(co2_elec) # tonne of CO2 emission due to elec use in limemaking for bof.
        m_co2_elec_oxygen_corex = elec_oxygen_corex * np.array(co2_elec) # tonne of CO2 emission due to elec use in oxygen production for corex.
        m_co2_elec_oxygen_bof = elec_oxygen_bof * np.array(co2_elec) # tonne of CO2 emission due to elec use in oxygen production for bof.
        m_co2_elec = m_co2_elec_corex + m_co2_elec_bof + m_co2_elec_lim_corex + m_co2_elec_lim_bof + m_co2_elec_oxygen_corex + m_co2_elec_oxygen_bof # tonne of CO2 emission from electricity use

        #emission by stage
        t_asu = np.array(m_co2_elec_oxygen_corex) + np.array(m_co2_elec_oxygen_bof)
        t_corex = np.array(m_co2_coke_corex) + np.array(m_co2_coal_corex) + np.array(m_co2_elec_corex) + np.array(m_co2_elec_lim_corex)  # total CO2 emission from corex (tonne)
        t_bof = np.array(m_co2_elec_bof) + np.array(m_co2_elec_lim_bof)  # total CO2 emission from bof (tonne)
        t_co2 = np.array(t_asu) + np.array(t_corex) + np.array(t_bof) # total CO2 emission for corex-bof (tonne)
        t_co2_direct_capture = np.array(m_co2_coke_corex) + np.array(m_co2_coal_corex) # total amount of CO2 considered for CCS (tonne)

        # emission by source
        co2_coal = m_co2_coal_corex #tonne co2
        co2_coke = m_co2_coke_corex #tonne co2
        co2_electricity =  m_co2_elec # tonne co2

        ############################################################################################################################################
        #Economic analysis
        #CAPEX
        cepci1 = cep(2017)[0] # get the base cost year. source: 2
        cepci2 = cep(2020)[0] #get the most up to date value available.
        ppp2 = pppv(country,2020) # get the ppp for the country of interest

        #ASU source: 3
        capacity2_asu = capexes['Base Scale'][2] # Assume the capacity is the same as base scale.
        n_asu = (m_o2_corex + m_o2_bof)/capacity2_asu
        cost2_asu = n_asu*capexs(capacity2_asu,cepci1,cepci2,ppp2)['ASU'] #total cost for asu (Indian Rupee)

        #COREX plant. source 3.
        capacity2_corex = capexes['Base Scale'][4] # Assume the capacity is the same as base scale.
        n_corex = m_hot_metal/np.array(capacity2_corex)
        cost2_corex = n_corex*capexs(capacity2_asu,cepci1,cepci2,ppp2)['COREX'] #total cost for COREX (Indian Rupee)

        #BOF plant. source 3.
        capacity2_bof = capexes['Base Scale'][7]  # Assume the capacity is the same as base scale.
        n_bof = m_steel / capacity2_bof  # number of bof
        cost2_bof = n_bof * capexs(capacity2_bof, cepci1, cepci2, ppp2)['BOF'] #total cost for BOF (Indian Rupee)

        t_capex = np.array(cost2_asu) + np.array(cost2_corex) + np.array(cost2_bof)  #total capital investment (Indian Rupee)

        #OPEX material/energy price
        scrap_price = []
        iron_ore_price = []
        limestone_price = []
        coke_price = []
        coal_price = []
        electricity_price = []
        oxygen_price = []
        y_i = 2020 #initial/baseline year
        y_f = 2040 # final year
        for y in years:
            scrap_price_update = self.scrap_price + (y - y_i) * self.scrap_price * (self.scrap_price_change/100)/(y_f - y_i)
            scrap_price.append(scrap_price_update)
            iron_ore_price_update = self.iron_ore_price + (y - y_i) * self.iron_ore_price * (self.iron_ore_price_change/100)/(y_f - y_i)
            iron_ore_price.append(iron_ore_price_update)
            limestone_price_update = self.limestone_price +  (y - y_i) * self.limestone_price * (self.limestone_price_change/100)/(y_f - y_i)
            limestone_price.append(limestone_price_update)
            coke_price_update = self.coke_price +  (y - y_i) * self.coke_price * (self.coke_price_change/100)/(y_f - y_i)
            coke_price.append(coke_price_update)
            coal_price_update = self.coal_price + (y - y_i) * self.coal_price *  (self.coal_price_change/100)/(y_f - y_i)
            coal_price.append(coal_price_update)
            electricity_price_update = self.electricity_price + (y - y_i) * self.electricity_price * (self.electricity_price_change/100)/(y_f - y_i)
            electricity_price.append(electricity_price_update)
            oxygen_price_update = self.oxygen_price + (y - y_i) * self.oxygen_price * (self.oxygen_price_change/100)/(y_f - y_i)
            oxygen_price.append(oxygen_price_update)
        # print(f"oxygen price: {oxygen_price}")


        #OPEX material cost for each process unit
        c_scrap = m_scrap * np.array(scrap_price) * np.array(er(country)) # scrap cost (Indian Rupee)
        c_iron_ore = m_ore * np.array(iron_ore_price) * np.array(er(country))  # iron ore cost (Indian Rupee)
        c_lim_corex = m_lim_corex* np.array(limestone_price) * np.array(er(country)) # cost of limestone used in COREX (Indian Rupee)
        c_lim_bof = m_lim_bof * np.array(limestone_price) * np.array(er(country)) # cost of limestone used in BOF (Indian Rupee)
        c_coke_corex = m_coke_corex * np.array(coke_price) * np.array(er(country)) # cost of coke used in COREX (Indian Rupee)
        c_coal_corex = m_coal_corex * np.array(coal_price) * np.array(er(country)) # cost of coal used in COREX (Indian Rupee)
        c_oxygen_corex = m_o2_corex * oxygen_price * np.array(er(country)) # cost of oxygen used in COREX (Indian Rupee)
        c_oxygen_bof = m_o2_bof * oxygen_price * np.array(er(country)) # cost of oxygen used in BOF (Indian Rupee)
        c_material = c_scrap + c_iron_ore + c_lim_corex + c_lim_bof + c_coke_corex + c_coal_corex + c_oxygen_corex + c_oxygen_bof #material cost (indian Rupee)

        c_elec_corex = elec_corex * np.array(electricity_price) * np.array(er(country)) # cost of electricity used in COREX (Indian Rupee)
        c_elec_bof = elec_bof * np.array(electricity_price) * np.array(er(country)) # cost of electricity used in BOF (Indian Rupee)
        c_elec_lim_corex = elec_lim_corex * np.array(electricity_price) * np.array(er(country)) # cost of electricity used for limestone in COREX (Indian Rupee)
        c_elec_lim_bof = elec_lim_bof * np.array(electricity_price) * np.array(er(country)) # cost of electricity used for limstone in BOF (Indian Rupee)
        c_elec_oxygen_corex = elec_oxygen_corex * np.array(electricity_price) * np.array(er(country)) # cost of electricity used for oxygen in COREX (Indian Rupee)
        c_elec_oxygen_bof = elec_oxygen_bof * np.array(electricity_price) * np.array(er(country)) # cost of electricity used for oxygen in BOF (Indian Rupee)
        c_energy = c_elec_corex + c_elec_bof + c_elec_lim_corex + c_elec_lim_bof + c_elec_oxygen_corex + c_elec_oxygen_bof #energy cost except coal/coke (Indian Rupee)

        #OPEX operation & maintenance cost
        tc_onm = np.array(m_steel) * 0.8 * np.array(er(country)) #assume steel operation and maintenance cost is $0.8/tonne. source 4.
        tc_ins_loc = np.array(t_capex) * 0.045 # maintenance and labor cost. source 4. Indian Rupee.
        tc_labor = 100*60000/1360000*np.array(m_steel) # assume number of labor needed is linearly correlated to total amount of steel produced. source 3.
        tc_administrative = 0.3 * tc_onm # administrative labor cost. Rupee. source 4.
        t_omt = tc_onm + tc_ins_loc + tc_labor + tc_administrative # operation & management cost of hisarna-bof

        # total OPEX
        opex = t_omt + c_material + c_energy # (Indian Rupee)

        ############################################################################################################################################
        #CCS
        ccs_regeneration_co2 = 0
        opex_ccs = 0
        capex_ccs = 0
        co2_ng = 0 #co2 emission coming from NG (tonne)
        y = [str(i) for i in years]

        if self.ccs == 'Yes':
            cap_r = self.cap_r
            solvent = self.solvent
            regeneration_u = self.regeneration_u
            ccs_idx = y.index(self.ccs_start)
            ccs_vec = np.concatenate((np.zeros(ccs_idx), np.ones(len(years) - ccs_idx))) #Add vector for the
            # print(ccs_vec)

            ccs_outputs = ccs(t_co2_direct_capture*ccs_vec, solvent, cap_r, regeneration_u, country) #capex, opex, co2 emission due to regeneration utility

            #CO2 emissions
            ccs_regeneration_co2 = ccs_outputs['CO2'] # co2 emitted due to ccs regeneration utility (tonne)
            if regeneration_u == 'NG':
                co2_ng = ccs_regeneration_co2 # co2 emission due to NG used in ccs (tonne)
            else:
                m_co2_elec += ccs_regeneration_co2 # co2 emission from electricity source (tonne)

            #Modify emissions based on year of ccs implementation
            [m_co2_coal_corex,m_co2_coke_corex] = [m_co2_coal_corex * (1 - ccs_vec*cap_r/100),m_co2_coke_corex * (1 - ccs_vec*cap_r/100) ]# amount of direct CO2 emitt from coal in COREX (tonne)


            t_corex = np.array(m_co2_coke_corex) + np.array(m_co2_coal_corex) + np.array(m_co2_elec_corex) + np.array(m_co2_elec_lim_corex) # amount of  CO2 emitt from COREX (tonne)
            t_co2 = np.array(t_asu) + np.array(t_corex) + np.array(t_bof) + ccs_regeneration_co2 # total CO2 emission including ccs regeneration (tonne)
            t_co2_direct_capture += co2_ng

            # emission by source
            co2_coal = m_co2_coal_corex #tonne co2
            co2_coke = m_co2_coke_corex #tonne co2
            co2_electricity = m_co2_elec # tonne co2
            #Economic analysis


            # CCS transportation and storage cost
            co2_transportation_distance = float(self.co2_transportation_distance)  # co2 transport to storage location. (km)
            ccs_co2_transport = co2_transport(co2_transportation_distance)  # co2 transportation price ($_2020/tCO2)
            ccs_cost_transport = ccs_co2_transport * t_co2_direct_capture * cap_r / 100 * np.array(er(country)) # co2 transportation cost (LCU_2020)
            # print(f'ccs transport cost: {ccs_co2_transport}')
            ccs_co2_storage = co2_storage(options_storage.index(self.co2_storage))  # co2 storage price ($_2020/tCO2)
            ccs_cost_storage = ccs_co2_storage * t_co2_direct_capture * cap_r / 100 * np.array(er(country))  # co2 storage cost (LCU_2020)
            # print(f'ccs storage cost: {ccs_co2_storage}')

            # CAPEX, OPEX
            capex_ccs = np.array(ccs_outputs['tpc']) * cep(2020)[0] / cep(2008)[0] * np.array(er(country)) / np.array(er('EU_27')) +\
                        (ccs_cost_storage + ccs_cost_transport)  # CAPEX of CCS. convert from 2005 euro to 2020 for country interested


            opex_ccs = (ccs_outputs['operation_management'] + ccs_outputs['raw material'] ) * np.array(er(country)) +ccs_outputs['utility cost']# material, operation and management cost of ccs

            #Modify cost based on year of implementation
            [capex_ccs,opex_ccs] = [capex_ccs,opex_ccs]*ccs_vec

            t_capex = t_capex + np.array(capex_ccs)

            opex = opex + opex_ccs

        # direct emissions
        t_co2_direct = t_co2 - co2_electricity

        # carbon tax
        co2_tax = self.co2_tax * np.array(er(country))  #carbon tax $/tonne
        cost_carbon_tax = t_co2_direct * co2_tax #  $ paid for carbon tax



        print(t_co2_direct/m_steel)

        return {
            'years': years,
            'co2_coal':co2_coal/m_steel,
            'co2_coke': co2_coke/m_steel,
            'co2_ng': co2_ng/m_steel,
            'co2_electricity': co2_electricity/m_steel,
            'co2_asu': t_asu/m_steel,
            'co2_corex': t_corex/m_steel,
            'co2_bof': t_bof/m_steel,
            'ccs': ccs_regeneration_co2/m_steel,
            't_co2_direct_capture': t_co2_direct_capture/m_steel,
            't_co2':t_co2/m_steel,
            't_co2_fossil': t_co2_direct / m_steel,
            'scrap_cost':c_scrap/m_steel/np.array(er(country)),
            'iron_ore_cost':c_iron_ore/m_steel/np.array(er(country)),
            'limestone_cost': (c_lim_corex + c_lim_bof)/m_steel/np.array(er(country)),
            'coke_cost': c_coke_corex/m_steel/np.array(er(country)),
            'coal_cost': c_coal_corex/m_steel/np.array(er(country)),
            'oxygen_cost': (c_oxygen_corex + c_oxygen_bof)/m_steel/np.array(er(country)),
            'electricity_cost': c_energy/m_steel/np.array(er(country)),
            'operation_management_corex_bof': t_omt/m_steel/np.array(er(country)),
            'capex_ccs': capex_ccs/m_steel/np.array(er(country)),
            'opex_ccs': opex_ccs/m_steel/np.array(er(country)),
            'opex': opex/m_steel/np.array(er(country)),
            't_capex': t_capex/m_steel/np.array(er(country)),
            'cost from carbon tax': cost_carbon_tax / m_steel/ np.array(er(country)),

        }
    def figures(self, results):
        opex = results['opex']
        t_capex = results['t_capex']
        cost = opex + t_capex + results['cost from carbon tax']

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
                'data': results['co2_electricity'],
            },

        ]
        emissions_by_stage = [
            {
                'label': 'ASU',
                'color': 'indigo_dark',
                'data': results['co2_asu'],
            },
            {
                'label': 'COREX',
                'color': 'orange',
                'data': results['co2_corex'],
            },
            {
                'label': 'BOF',
                'color': 'blue',
                'data': results['co2_bof'],
            },
        ]
        detailed_costs = [
            {
                'label': 'Limestone',
                'color': 'green',
                'data': results['limestone_cost'],
            },
            {
                'label': 'Electricity',
                'color': 'orange',
                'data': results['electricity_cost'],
            },
            {
                'label': 'Fossil Fuel',
                'color': 'black',
                'data': results['coal_cost'] + results['coke_cost'],
            },
            {
                'label': 'Scrap + Iron Ore',
                'color': 'indigo_dark',
                'data': results['iron_ore_cost'] + results['scrap_cost'],
            },
            {
                'label': 'Oxygen',
                'color': 'green',
                'data': results['oxygen_cost'],
            },
            {
                'label': 'Operation & Management of COREX-BOF',
                'color': 'purple',
                'data': results['operation_management_corex_bof'],
            },
            {
                'label': 'Capital',
                'color': 'yellow',
                'data': t_capex,
            },
            {
                'label': 'Cost from Carbon Tax',
                'color': 'teel',
                'data': results['cost from carbon tax'],
            },
        ]

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
                'data': results['ccs'],
            }]
            detailed_costs += [{
                'label': 'Operation & Management of CCS',
                'color': 'teal',
                'data': results['opex_ccs'],
            },]

        return [
            {
                'label': 'GHG Emissions by Source',
                'unit': 'tonne CO2 / tonne steel',
                'axis': 0,
                'datasets': emissions_by_source,
            },
            {
                'label': 'GHG Emissions by Stage',
                'unit': 'tonne CO2 / tonne steel',
                'axis': 0,
                'datasets': emissions_by_stage,
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
                        'data': t_capex,
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

            # {
            #     'label': 'Total Costs',
            #     'unit': 'Rupees',
            #     'axis': 1,
            #     'datasets': [
            #         {
            #             'label': 'Total Cost',
            #             'data': results['opex'] + results['t_capex'],
            #         },
            #     ],
            # },
            # {
            #     'label': 'Production',
            #     'unit': 'tonnes',
            #     'axis': 1,
            #     'datasets': [
            #         {
            #             'label': 'Production',
            #             'data': results['m_steel'],
            #         },
            #     ],
            # },
        ]

    def plot(self, results):
        print(f"co2 fossil: {results['t_co2_fossil']}, co2 electricity: {results['co2_electricity']}, total co2 {results['t_co2']}" )
        # print(f"results: {results}")
        plot1 = plt.figure(1)
        years = results['years']
        plt.plot(years, results['co2_asu'], marker='o', label='Air separation unit', color='blue')
        plt.plot(years, results['co2_corex'], marker='D', label='COREX', color='orange')
        plt.plot(years, results['co2_bof'], marker='*', label='BOF', color='blueviolet')
        plt.plot(years, results['ccs'], marker='*', label='CCS', color='purple')
        plt.plot(years, results['t_co2'], marker = 's', label='Total',color='red')
        plt.xticks(np.arange(min(years), max(years) + 1, 5))
        plt.title(f'CO2 emission for COREX-BOF routes CCS:{self.ccs}')
        plt.xlabel('Year')
        plt.ylabel('CO2 emissions (tonne CO2/tonne of steel)')
        plt.legend()

        # capex, opex plots
        fig, ax = plt.subplots()
        ax.plot(years, results['limestone_cost'], marker='d', label='Limestone', color='green')
        ax.plot(years, results['electricity_cost'], marker='x', label='Electricity', color='orange')
        ax.plot(years, results['coke_cost'] + results['coal_cost'], marker='p', label='Fossil Fuel', color='olive')
        ax.plot(years, results['iron_ore_cost'] +  results['scrap_cost'], marker='+', label='Scrap+Iron Ore',
                color='purple')
        ax.plot(years, results['cost from carbon tax'], marker='*', label='Cost from Carbon Tax', color='turquoise')
        ax.plot(years, results['opex'], marker='*', label=f'OPEX', color='red')
        ax.set_xlabel('Year')
        plt.xticks(np.arange(min(years), max(years) + 1, 5))
        ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))  # use scientific tick-label for y axis.
        plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))  # use scientific tick-label for y axis.
        plt.title(f'OPEX/CAPEX for COREX-BOF routes CCS: {self.ccs}')
        ax2 = ax.twinx()  # add a second y axis
        ax2.plot(years, results['t_capex'], marker='o', label=f'CAPEX', color='navy')
        ax.set_ylabel(f"OPEX (USD $/tonne steel)", color='black')
        ax2.set_ylabel(f"CAPEX (USD $/tonne steel)", color='navy')
        ax.legend()
        plt.legend()
        plt.show()
