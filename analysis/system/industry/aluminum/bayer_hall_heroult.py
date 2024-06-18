"""
Functional unit: 1 tonne of aluminum
source: 1. European Aluminum Industry: https://european-aluminium.eu/media/3321/full-environmental-profile-report-2018.pdf
2. IEA electricity carbon intensity: https://www.iea.org/reports/tracking-power-2020
@author: Lingyan Deng
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from core.common import InputSource, Color
import core.conditionals as conditionals
from core.inputs import OptionsInput, ContinuousInput, PercentInput, Default, Tooltip, InputGroup
import core.validators as validators
from analysis.system.industry.cement.elec_input import user_inputs_ft_cap,co2_int
from analysis.system.industry.aluminum.aluminum_production import aluminum_input, aluminum_user
from analysis.system.industry.aluminum.alumina import f_defaults, m_defaults,alumina, alumina_input
from analysis.system.industry.aluminum.anode import anode_carbon, anode_energy, anode_input
from analysis.system.industry.aluminum.bauxite import bauxite
from analysis.system.industry.aluminum.project_elec_co2 import elec_co2
from analysis.system.industry.aluminum.ingot import ingot, ingot_input
from analysis.system.industry.aluminum.capex import capexs
from analysis.system.industry.aluminum.cepci import cepci_v
from analysis.system.industry.aluminum.ppp import pppv
from analysis.system.industry.aluminum.exchange_rate import exchange_country
from analysis.system.industry.aluminum.aluminum_demand import aluminum_demand as ald 
from analysis.system.industry.aluminum.opex_primary import opex_input
from analysis.system.industry.aluminum.ccs import user_inputs as ccs_inputs
from analysis.system.industry.aluminum.ccs import ccs

class BAYERHALLHEROULT(InputSource):

    @classmethod
    def user_inputs(cls):
        COUNTRIES = ['Global', 'EU-27'] #countries available
        return user_inputs_ft_cap(cls,COUNTRIES) \
            + [
            InputGroup('bauxite', 'Bauxite Mining', children=[
                ContinuousInput(
                    'f_heavy_oil_bauxite', 'Fraction of energy from heavy oil (rest diesel oil)',
                    defaults=[Default(0.212)],
                    validators=[validators.numeric(), validators.gte(0), validators.lte(1)],
                )
                ])
            ]+ anode_input(cls) + alumina_input(cls) + aluminum_input(cls) + ingot_input(cls) + [
                InputGroup('capex', 'Cost Analysis', children=[
                ContinuousInput(
                    'alumina_plant_lifetime', 'Alumina plant life time',
                    unit = 'years',
                    defaults=[Default(5)],
                    validators=[validators.numeric(), validators.gte(0)],
                ),
                ContinuousInput(
                    'al_plant_lifetime', 'Aluminum plant life time',
                    unit = 'years',
                    defaults=[Default(50)],
                    validators=[validators.numeric(), validators.gte(0)],
                ),
                ContinuousInput(
                    'capacity_alumina', 'Alumina plant capacity',
                    unit = 'million tonnes annually',
                    defaults=[Default(2.275)],
                    validators=[validators.numeric(), validators.gte(0)],
                ),
                ContinuousInput(
                    'capacity_aluminum', 'Aluminum plant capacity',
                    unit = 'million tonnes annually',
                    defaults=[Default(0.195)],
                    validators=[validators.numeric(), validators.gte(0)],
                ),
            
                ])
                
            ] + ccs_inputs() + opex_input(cls)


    def run(self):
        country = self.country
        m_aluminum_0 =3.6E6 # India present aluminum production
        m_aluminum_n = 1.6E7 + 3.6E6 # India per capital demand 2.5 kg-->11 kg
        y_0 = 2020
        y_n = 2040
        linear_demand = ald(m_aluminum_0,m_aluminum_n,y_0,y_n) # achieve per capital consumption to be the same as global average
        m_ingot = pd.Series([1,1,1,1,1]) # 1 tonne of aluminum
        # print(country)
        years = elec_co2(country)['years'][20:25]
        c_electricity = co2_int(self, years)  # elec_co2(country)['co2'][20:25]
        # print(c_electricity)

        c_coal = 0.0979 #self.c_coal co2 emission factor kg CO2/MJ
        c_ng = 0.0632 # self.c_ng co2 emission factor kg CO2/MJ
        c_heavy_oil = 0.0851 #self.c_heavy_oil co2 emission factor kg CO2/MJ
        c_diesel_oil = 0.0826 #self. c_diesel_oil co2 emission factor kg CO2/MJ
        c_steam = 0.0702 #self.c_steam co2 emission factor kg CO2/MJ
        hhv_coal = 27.05 #self.hhv_coal MJ/kg
        hhv_ng = 49.5 #self.hhv_ng MJ/kg
        hhv_heavy_oil = 43.05 #self.hhv_heavy_oil MJ/kg
        hhv_diesel_oil = 42.9 #self.hhv_diesel_oil MJ/kg
        steam_heat_content = 25.86 #self.steam_heat_content MJ/kg

        # ingot production process
        ingot_material_energy = ingot(self,m_ingot,c_electricity) # material, energy flow of ingot production
        q_electricity_ingot = ingot_material_energy['q_electricity'] # GJ
        m_aluminum = ingot_material_energy['m_aluminum'] # tonne Al
        m_al_alternative = ingot_material_energy['m_al_alternative'] # tonne Al alterntives
        m_heavy_oil_ingot = ingot_material_energy['m_heavy_oil']
        m_diesel_oil_ingot = ingot_material_energy['m_diesel_oil']
        m_vlso_ingot = ingot_material_energy['m_vlso']  # tonne
        m_ng_ingot =  ingot_material_energy['m_ng']
        co2_heavy_oil_ingot = ingot_material_energy['co2_heavy_oil'] # tonne Co2
        co2_diesel_oil_ingot = ingot_material_energy['co2_diesel_oil']
        co2_vlso_ingot = ingot_material_energy['co2 vlso']
        co2_ng_ingot = ingot_material_energy['co2_ng']
        co2_electricity_ingot = ingot_material_energy['co2_electricity']
        t_co2_ingot = co2_heavy_oil_ingot + co2_diesel_oil_ingot + co2_vlso_ingot + co2_ng_ingot + co2_electricity_ingot # total CO2 emission from ingot process

        #aluminum production process
        material_flow_aluminum = aluminum_user(self,m_aluminum,c_electricity) # aluminum production material flows
        m_alumina = material_flow_aluminum['alumina'] #tonne alumina
        #print(f"alumina: {m_alumina}")
        m_anode = material_flow_aluminum['anode'] #tonne anode
        m_aluminum_fluoride = material_flow_aluminum['aluminum fluoride'] #tonne of aluminum fluoride
        m_carthode_carbon = material_flow_aluminum['cathode carbon'] # tonne of cathode carbon
        m_steel = material_flow_aluminum['steel'] #tonne of steel

        q_electricity_aluminum = material_flow_aluminum['electricity'] #GJ
        co2_electricity_aluminum = material_flow_aluminum['co2 electricity'] # tonne of co2 emitted due to electricity use.
        
        #anode production
        anode_material_flow = anode_carbon(self,m_anode)
        anode_raw_carbon = anode_material_flow['total raw carbon'] # tonne of carbon used to produce anode
        co2_anode_carbon = anode_material_flow['co2 anode carbon'] # tonne of co2 emission due to anode carbon consumption

        t_co2_aluminum = co2_electricity_aluminum + co2_anode_carbon # total CO2 in aluminum process. Includs the CO2 emission from anode carbon oxidation.

        #anode energy related
        anode_energy_flow = anode_energy(self,m_anode,c_electricity,c_coal,c_heavy_oil,c_diesel_oil,
                c_ng, hhv_coal, hhv_heavy_oil,hhv_diesel_oil,hhv_ng)

        m_coal_anode = anode_energy_flow['coal']
        m_heavy_oil_anode = anode_energy_flow['heavy oil']
        m_diesel_oil_anode = anode_energy_flow['diesel oil']
        m_vlso_anode = anode_energy_flow['vlso']
        m_ng_anode = anode_energy_flow['ng']
        q_electricity_anode = anode_energy_flow['electricity']


        co2_coal_anode = anode_energy_flow['co2 coal']
        co2_heavy_oil_anode = anode_energy_flow['co2 heavy oil']
        co2_diesel_oil_anode = anode_energy_flow['co2 diesel oil']
        co2_vlso_anode = anode_energy_flow['co2 vlso']
        co2_ng_anode = anode_energy_flow['co2 ng']
        co2_electricity_anode = anode_energy_flow['co2 electricity']
        t_co2_anode = co2_coal_anode + co2_heavy_oil_anode + co2_diesel_oil_anode + co2_vlso_anode + co2_ng_anode + co2_electricity_anode + co2_vlso_anode # total CO2 in aluminum process

        # alumina production
        alumina_material = alumina(self,m_alumina,c_electricity)
        m_bauxite = alumina_material['bauxite'] # tonne of bauxite
        m_naoh = alumina_material['naoh'] #tonne of NaOH
        m_caoh2 = alumina_material['caoh2'] #tonne of CaOH2
        m_flocullant = alumina_material['flocullant'] #tonne of flocullant
        m_cao = alumina_material['cao'] #tonne of CaO

        m_coal_alumina = alumina_material['coal'] #tonne of coal
        m_heavy_oil_alumina = alumina_material['heavy oil'] #tonne
        m_diesel_oil_alumina =alumina_material['diesel oil'] # tonne
        m_vlso_alumina = alumina_material['vlso'] # tonne
        m_ng_alumina = alumina_material['natural gas'] #tonne
        m_steam_alumina = alumina_material['steam'] #tonne

        q_electricity_alumina = alumina_material['electricity alumina'] #GJ
        co2_coal_alumina = alumina_material['co2 coal'] #tonne co2
        co2_heavy_oil_alumina = alumina_material['co2 heavy oil'] #tonne co2
        co2_vlso_alumina = alumina_material['co2 vlso'] #tonne co2
        co2_diesel_oil_alumina = alumina_material['co2 diesel oil']  # tonne co2
        co2_ng_alumina = alumina_material['co2 ng'] #tonne co2
        co2_steam_alumina = alumina_material['co2 steam'] #tonne co2
        co2_electricity_alumina = alumina_material['co2 electricity'] #tonne co2
        t_co2_alumina = (co2_coal_alumina + co2_heavy_oil_alumina + co2_diesel_oil_alumina + co2_vlso_alumina +
        co2_ng_alumina + co2_steam_alumina + co2_electricity_alumina)
        #print(f"alumina coal: {co2_coal_alumina}, heavy oil: {co2_heavy_oil_alumina}, diesel: {co2_diesel_oil_alumina}")
        #print(f"ng: {co2_ng_alumina}, steam: {co2_steam_alumina}, electricity: {co2_electricity_alumina}, t_alumina: {t_co2_alumina} ")

        # bauxite process
        f_heavy_oil_bauxite = self.f_heavy_oil_bauxite
        bauxite_material = bauxite(m_bauxite,f_heavy_oil_bauxite,c_electricity, country,
            c_heavy_oil,c_diesel_oil,hhv_heavy_oil,hhv_diesel_oil)

        m_heavy_oil_bauxite = bauxite_material['heavy oil'] # tonne heavy oil
        m_diesel_oil_bauxite = bauxite_material['diesel oil'] #tonne diesel oil
        q_electricity_bauxite = bauxite_material['electricity'] #GJ

        co2_heavy_oil_bauxite = bauxite_material['co2 heavy oil'] #tonne co2
        co2_diesel_oil_bauxite = bauxite_material['co2 diesel oil'] # tonne co2
        co2_electricity_bauxite = bauxite_material['co2 electricity'] # tonne co2
        t_co2_bauxite = co2_heavy_oil_bauxite + co2_diesel_oil_bauxite + co2_electricity_bauxite # tonne co2



        #co2 emission by source
        # print(m_carthode_carbon)
        # print(co2_coal_anode)
        # print(co2_coal_alumina)
        t_co2_coal = co2_coal_anode + co2_coal_alumina
        t_co2_heavy_oil = co2_heavy_oil_anode + co2_heavy_oil_bauxite + co2_heavy_oil_alumina + co2_heavy_oil_ingot
        t_co2_diesel_oil = co2_diesel_oil_bauxite + co2_diesel_oil_anode + co2_diesel_oil_alumina + co2_diesel_oil_ingot
        t_co2_vlso = co2_vlso_anode + co2_vlso_alumina + co2_vlso_ingot
        t_co2_ng = co2_ng_anode + co2_ng_alumina + co2_ng_ingot
        t_co2_anode_carbon = co2_anode_carbon
        t_co2_steam = co2_steam_alumina
        t_co2_electricity = (co2_electricity_ingot + co2_electricity_aluminum + co2_electricity_anode + co2_electricity_alumina +
                             co2_electricity_bauxite + co2_steam_alumina)

        t_direct_co2 = (co2_heavy_oil_ingot + co2_diesel_oil_ingot + co2_vlso_ingot + co2_ng_ingot +
            co2_anode_carbon + co2_coal_anode + co2_heavy_oil_anode + co2_diesel_oil_anode + co2_vlso_anode + co2_ng_anode +
            co2_coal_alumina + co2_heavy_oil_alumina + co2_diesel_oil_alumina + co2_vlso_alumina + co2_ng_alumina +
            co2_heavy_oil_bauxite + co2_diesel_oil_bauxite)

        t_indirect_co2 = t_co2_electricity
        t_co2 = t_direct_co2 + t_indirect_co2
        # print(t_co2)

        ##############
        # Carbon Capture at Smelting Reduction Stage ( to Aluminium)

        ccs_regen_co2 = 0
        t_co2_ccs = 0
        y = [str(i) for i in years]


        # print(t_co2_anode_carbon) #-= co2_anode_carbon * (self.cap_r) / 100 * ccs_vec
        # # print(t_co2_electricity ) #+= ccs_regen_co2
        # print(t_co2_aluminum) #-= co2_anode_carbon * (self.cap_r) / 100 * ccs_vec
        # print(t_direct_co2)
        # print(t_indirect_co2)
        print(t_co2)
        print('-'*30)

        if self.ccs == 'Yes':
            ccs_idx = y.index(self.ccs_start)
            ccs_vec = np.concatenate((np.zeros(ccs_idx), np.ones(len(years) - ccs_idx)))
            # assuming boiler duty covered by electricity
            t_co2_capture = co2_anode_carbon
            ccs_info = ccs(t_co2_capture*ccs_vec, c_electricity, self.co2_vol, self.solvent, self.cap_r, self.regeneration_u,
                           country, self.elec_price * (1 + self.elec_price_change / 100))
            ccs_regen_co2 = ccs_info['CO2']
            # print( t_co2_capture*(self.cap_r)/100*ccs_vec)
            # print(c_electricity)
            # print(ccs_regen_co2)

            if self.regeneration_u == 'Electricity':
                # co2_anode_carbon = co2_anode_carbon - t_co2_capture*(self.cap_r)/100*ccs_vec
                t_co2_anode_carbon = t_co2_anode_carbon + (-t_co2_capture + t_co2_capture*(100-self.cap_r)/100)*ccs_vec
                t_co2_electricity += ccs_regen_co2
                t_co2_aluminum -=  t_co2_capture*(self.cap_r)/100*ccs_vec
                t_direct_co2 -= t_co2_capture * (self.cap_r) / 100 * ccs_vec
                t_co2 = t_co2 - t_co2_capture * (self.cap_r) / 100 * ccs_vec + ccs_regen_co2

            t_co2_ccs = ccs_regen_co2
            # # print('-'*30)
            # print(co2_anode_carbon)
            # # print('-'*30)
            # print(f"capture: {t_co2_capture * (self.cap_r)/100 * ccs_vec}")
                ##################################
        # print(co2_anode_carbon)
        #     print(t_co2_anode_carbon)  # -= co2_anode_carbon * (self.cap_r) / 100 * ccs_vec
        # print(t_co2_electricity)  # += ccs_regen_co2
        #     print(t_co2_aluminum)  # -= co2_anode_carbon * (self.cap_r) / 100 * ccs_vec
        #     print(t_direct_co2)
            # print(t_indirect_co2)
            print(t_co2)

        #===================================================================================================================
        #Economic analysis
        # CAPEX
        cepci2 = cepci_v(years[20])
        ppp2 = pppv(country,years[20])/exchange_country(country) # converted Euro to USD
        alumina_plant_lifetime = self.alumina_plant_lifetime
        al_plant_lifetime = self.al_plant_lifetime
        capacity_alumina = self.capacity_alumina * 1e6
        capacity_aluminum = self.capacity_aluminum * 1e6
        capex_alumina =  np.array(capexs(capacity_alumina,cepci2, ppp2)['capex_alumina'])
        capex_aluminum = np.array(capexs(capacity_aluminum,cepci2, ppp2)['capex_aluminum'])
        capex =  (capex_alumina*m_alumina/alumina_plant_lifetime + capex_aluminum*m_aluminum/al_plant_lifetime)
        #print('capex', capex_alumina,capex_aluminum)

        #opex
        # material & energy cost
        c_bauxite = m_bauxite * self.bauxite_price * (1 + self.bauxite_price_change/100)
        c_anode = m_anode * self.anode_price* (1 + self.anode_price_change/100)
        c_naoh = m_naoh * self.naoh_price * (1 + self.naoh_price_change/100)
        c_cao = m_cao * self.cao_price * (1 + self.cao_price_change/100)
        c_alf3 = m_aluminum_fluoride * self.alf3_price * (1 + self.alf3_price_change/100)
        c_heavy = (m_heavy_oil_alumina + m_heavy_oil_anode + m_heavy_oil_bauxite + m_heavy_oil_ingot)*self.heavy_price*\
            (1 + self.heavy_price_change/100)
        c_diesel = (m_diesel_oil_alumina + m_diesel_oil_anode + m_diesel_oil_bauxite + m_diesel_oil_ingot)*\
            self.diesel_price * (1+ self.diesel_price_change/100)

        c_vlso = (m_vlso_anode + m_vlso_alumina + m_vlso_ingot)* self.vlso_price * (1+ self.vlso_price_change/100)
        c_ng = (m_ng_alumina + m_ng_anode + m_ng_ingot ) * hhv_ng/1000* \
            self.ng_price * (1+ self.ng_price_change/100)
        c_elec = (q_electricity_ingot + q_electricity_alumina + q_electricity_aluminum + q_electricity_anode + q_electricity_bauxite)*\
            self.elec_price*(1 + self.elec_price_change/100)
        c_material = c_bauxite + c_anode + c_naoh + c_cao + c_alf3
        c_utility = c_heavy + c_diesel + c_vlso + c_ng + c_elec
        c_onm = 5.44 * 2 # assume a fixed value related to plant size
        c_co2 = self.carbon_tax * t_co2 
        opex = (c_material + c_utility + c_onm + c_co2)*np.ones(5)

        # print('material', c_heavy,c_diesel,c_ng,c_elec)
       # print(f't_co2:{t_co2}, t_co2_indirect:{t_indirect_co2}, t_co2_direct:{t_direct_co2}')
        return {
            'country': country,
            'years': years,
            'aluminum': m_aluminum,
            'al_alternative': m_al_alternative,
            'm_heavy_oil_ingot': m_heavy_oil_ingot,
            'm_diesel_oil_ingot': m_diesel_oil_ingot,
            'm_ng_ingot': m_ng_ingot,
            'q_electrivity_ingot': q_electricity_ingot,
            'co2_heavy_oil_ingot': co2_heavy_oil_ingot,
            'co2 vlso ingot': co2_vlso_ingot,
            'co2_diesel_oil_ingot': co2_diesel_oil_ingot,
            'co2_ng_ingot': co2_ng_ingot,
            't_co2_ingot': t_co2_ingot,


            'alumina': m_alumina,
            'anode': m_anode,
            'aluminum fluoride': m_aluminum_fluoride,
            'cathode carbon': m_carthode_carbon,
            'steel': m_steel,
            'electricity aluminum': q_electricity_aluminum,
            'co2 electricity aluminum': co2_electricity_aluminum,

            'coal anode': m_coal_anode,
            'heavy oil anode': m_heavy_oil_anode,
            'diesel oil anode': m_diesel_oil_anode,
            'ng anode': m_ng_anode,
            'electricity anode': q_electricity_anode,
            'co2 coal anode': co2_coal_anode,
            'co2 heavy oil anode': co2_heavy_oil_anode,
            'co2 diesel oil anode': co2_diesel_oil_anode,
            'co2 vlso anode': co2_vlso_anode,
            'co2 ng anode': co2_ng_anode,
            'co2 electricity  anode': co2_electricity_anode,
            'co2 anode carbon': t_co2_anode_carbon,
            'co2_ccs': t_co2_ccs,
            'bauxite': m_bauxite,
            'naoh': m_naoh,
            'caoh2': m_caoh2,
            'flocullant': m_flocullant,
            'cao': m_cao,
            'coal alumina': m_coal_alumina,
            'heavy oil alumina': m_heavy_oil_alumina,
            'diesel oil alumina': m_diesel_oil_alumina,
            'natural gas alumina': m_ng_alumina,
            'steam': m_steam_alumina,
            'electricity alumina': q_electricity_alumina,
            'co2 coal alumina': co2_coal_alumina,
            'co2 heavy oil alumina': co2_heavy_oil_alumina,
            'co2 diesel oil alumina': co2_diesel_oil_alumina,
            'co2 vlso alumina': co2_vlso_alumina,
            'co2 ng alumina': co2_ng_alumina,
            'co2 steam alumina': co2_steam_alumina,
            'co2 electricity alumina': co2_electricity_alumina,

            'heavy oil bauxite': m_heavy_oil_bauxite,
            'diesel oil bauxite': m_diesel_oil_bauxite,
            'electricity bauxite': q_electricity_bauxite,
            'co2 heavy oil bauxite': co2_heavy_oil_bauxite,
            'co2 diesel oil bauxite': co2_diesel_oil_bauxite,
            'co2 electricity bauxite': co2_electricity_bauxite,

            'co2 bauxite': t_co2_bauxite,
            'co2 alumina': t_co2_alumina,
            'co2 anode': t_co2_anode,
            'co2 aluminum': t_co2_aluminum,

            'co2 coal': t_co2_coal,
            'co2 heavy oil': t_co2_heavy_oil,
            'co2 diesel oil': t_co2_diesel_oil,
            'co2 ng': t_co2_ng,
            'co2_vlso': t_co2_vlso,
            'co2 steam': t_co2_steam,
            'co2 electricity': t_co2_electricity,

            'direct co2': t_direct_co2,
            'indirect co2': t_indirect_co2,
            'total co2': t_co2,

            'capex': capex,
            'c_material':c_material,
            'c_utility': c_utility,
            'c_onm':c_onm,
            'carbon_tax': c_co2,
            'opex':opex,
        }
    def figures(self, results):

        if self.ccs == 'Yes':
           ccs_data =[ {
                'label': 'CCS',
                'color': Color(name='yellow'),
                'data': results['co2_ccs'],
            }]
        else:
            ccs_data = []
        return[
            {
                'label': 'GHG Emissions by Source',
                'unit': 'tonne CO\u2082 / tonne aluminum',
                'axis': 0,
                'datasets': [
                    {
                        'label': 'Coal',
                        'color': Color(name='black'),
                        'data': results['co2 coal'],
                    },
                    {
                        'label':'Anode carbon',
                        'color': Color(name='grey'),
                        'data': results['co2 anode carbon'],
                    },
                    {
                        'label': 'Heavy oil',
                        'color': Color(name='darkred'),
                        'data': results['co2 heavy oil'],
                    },
                    {
                        'label': 'Diesel oil',
                        'color': Color(name='brown'),
                        'data': results['co2 diesel oil'],
                    },
                    {
                        'label': 'VLSFO',
                        'color': Color(name='green'),
                        'data': results['co2 diesel oil'],
                    },
                    {
                        'label':'Steam',
                        'color': Color(name='darkorange'),
                        'data': results['co2 steam'],
                    },
                    {
                        'label':'Electricity',
                        'color': Color(name='blueviolet'),
                        'data': results['co2 electricity'],
                    },
                    {
                        'label':'Natural Gas',
                        'color': Color(name='blue'),
                        'data': results['co2 ng'],
                    },

                ]
            },
            {
                'label': 'GHG Emissions by Stage',
                'unit': 'tonne CO\u2082 / tonne aluminum',
                'axis': 0,
                'datasets': [
                    {
                        'label': 'Anode Production',
                        'color': Color(name='grey'),
                        'data': results['co2 anode'],
                    },
                    {
                        'label': 'Bauxite Mining',
                        'color': Color(name='firebrick'),
                        'data': results['co2 bauxite'],
                    },
                    {
                        'label': 'Alumina Refining',
                        'color': Color(name='navy'),
                        'data': results['co2 alumina'],
                    },
                    {
                        'label': 'Aluminum Smelting',
                        'color': Color(name='indigo'),
                        'data': results['co2 aluminum'],
                    },
                    {
                        'label': 'Ingot Production',
                        'color': Color(name='mediumpurple'),
                        'data': results['t_co2_ingot'],
                    },
                ] + ccs_data,
            },
            {
                'label': 'Costs',
                'unit': 'USD $ / tonne Aluminum',
                'axis': 0,
                'datasets': [
                    {
                        'label': 'Operating',
                        'color': Color(name='darkslategrey'),
                        'data': results['opex'],
                    },
                    {
                        'label': 'Capital',
                        'color': Color(name='teal'),
                        'data': results['capex'],
                    },
                ],
            },
            {
                'label': 'Total GHG Emissions',
                'unit': 'tonne CO\u2082 / tonne aluminum',
                'axis': 1,
                'datasets': [
                    {
                        'label': 'Total CO\u2082 Emissions',
                        'data': results['co2_ccs'],
                    },
                ],
            },

        ]



    def plot(self, results):
        # print(f"results: {results}")
        country = results['country'].title()
        plot1 = plt.figure(1)
        # plt.plot(results['years'], results['co2 bauxite'], marker='*', label='Bauxite', color='firebrick')
        # plt.plot(results['years'], results['co2 alumina'], marker='1', label='Alumina', color='navy')
        # plt.plot(results['years'], results['co2 anode'], marker='s', label='Anode', color='grey')
        # plt.plot(results['years'], results['co2 aluminum'], marker = 'v', label='Aluminum', color='purple')
        plt.plot(results['years'], results['total co2'], marker = 'o', label='Total', color='red')
        # plt.plot(results['years'], results['capex'], marker = 'o', label='CAPEX ($/tonne Al Ingot)', color='black')
        # plt.plot(results['years'], results['opex'], marker = 'o', label='OPEX ($/tonne Al Ingot)', color='green')
      
        #plt.vlines(2020, 0, 20, label='Past/future', color='black', linestyles='dashed')  # plot vertical lines
        plt.xticks(np.arange(min(results['years']),max(results['years'])+1,5))
        plt.title('CO\u2082 emission for primary routes')
        plt.xlabel('Year')
        plt.ylabel('CO\u2082 emissions (tonne CO\u2082/tonne aluminum)')
        plt.legend()
        plt.show()
