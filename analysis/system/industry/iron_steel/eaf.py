"""
Function unit: 1 tonne of steel
EAF steel making route. source: 1. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019). page 39
2.Unal Camdali and Murat Tunc. Modelling of electric energy consumption in the AC electric arc furnace. 2002
3. Simon, et al. "Techno-economic analysis of MEA CO2 capture from a cement kiln–impact of steam supply scenario." Energy Procedia 114 (2017): 6229-6239
"""

import matplotlib.pyplot as plt
import numpy as np
import json
from core.common import InputSource
import core.conditionals as conditionals
from core.inputs import OptionsInput, ContinuousInput, PercentInput, Default,Tooltip,InputGroup
import core.validators as validators

from analysis.system.industry.iron_steel.m_eaf_input import m_eaf_input as mei
from analysis.system.industry.iron_steel.steel_projectory import steel_route as sr
from analysis.system.industry.iron_steel.fuel_type import fuel_type, options as fuel_type_options
from analysis.system.industry.iron_steel.eaf_elec import eaf_elec
from analysis.system.industry.iron_steel.project_elec_co2 import elec_co2
from analysis.system.industry.iron_steel.co2_asu import m_co2_asu as mca
from analysis.system.industry.iron_steel.india_iron_steel_co2emission_prediction import co2_ub
from analysis.system.industry.iron_steel.capex import capexs, capexes
from analysis.system.industry.iron_steel.cepci import cepci_v as cep
from analysis.system.industry.iron_steel.ppp import pppv
from analysis.system.industry.iron_steel.material_cost import c_materials as cm, water as cw
from analysis.system.industry.iron_steel.exchange_rate import exchange_country as er
from analysis.system.industry.iron_steel.linear_elec_projection import linproj
from analysis.system.industry.iron_steel.elec_input import user_inputs_ft_cap as elec_inputs
from analysis.system.industry.iron_steel.elec_input import co2_int, COUNTRIES

class EAF(InputSource):

    @classmethod
    def user_inputs(cls):
        cp_options = [ 'Coal', 'Solar','Natural Gas','Wind']
        return elec_inputs(cls,cp_options) + [
            ContinuousInput(
                'co2_tax', 'Carbon tax',
                unit = '$/tonne',
                defaults=[Default(50)],
                validators=[validators.numeric(), validators.gte(0)],
            ),
            ContinuousInput(
                'f_ng', 'Fraction of carbon from natural gas (rest coal)',
                defaults=[Default(0.3962)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(1)],
                tooltip=Tooltip('Fraction of EAF carbon input coming from natural gas')
            ),
            OptionsInput(
                'fuel_type', 'Fuel type',
                options=fuel_type_options,
                defaults=[Default('Scrap-EAF')],
                tooltip=Tooltip('Default coal for the EAF (reduction agent)')
            ),
            ContinuousInput(
                'eaf_elec', 'EAF Electricity Requirement',
                defaults=[Default(183.33)],
                unit='kWh/tonne steel',
                validators=[validators.numeric(), validators.gte(0), validators.lte(500)],
                tooltip=Tooltip('Electricity consumption for electric arc furnace')
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
                'ng_price', 'Natural gas',
                unit='$/GJ',
                defaults=[Default(1.697)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip('Default prices  are with respect to  India in 2020. Due to fluctuation in pricing and location specific costs, user may input price', source='Indian Ministry of Petroleum & Natural Gas',
                                source_link='https://www.ppac.gov.in/WriteReadData/CMS/202009300542060502504GasPriceCeilingOct2020toMarch2021.pdf')
            ),
            ContinuousInput(
                'ng_price_change', '% change in natural gas price, 2020-2040',
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
        ]

    def run(self):
        # amount of steel to be produced by chosen route. in the year (2020,2040,5)
        m_steel = sr('Scrap_EAF')[0:5]
        # m_steel = np.array([1.0] * 5)

        f_scrap = 0.9996
        f_ng = self.f_ng

        fuel = fuel_type(fuel_type_options.index(self.fuel_type))
        c_coal = fuel['c'] # c content of coal (%)
        hhv_coal = fuel['hhv'] #hhv of coal (GJ/tonne)

        #get the material, energy input in EAF
        source = mei(m_steel, f_scrap, f_ng, c_coal)
        m_eaf_scrap = source['scrap'] # tonne of scrap+stainless steel input in EAF
        m_eaf_carbon_steel = source['carbon steel'] # tonne of carbon steel input in EAF
        m_eaf_fluxes = source['fluxes'] # tonne of limestone input in EAF
        m_eaf_ng = source['ng'] # tonne of NG input in EAF
        m_eaf_coal = source['coal'] # tonne of coal input in EAF
        m_eaf_water = source['water'] # Nm3 of water input in EAF
        v_eaf_o2 = source['o2'] #Nm3 of oxygen input in EAF

        #CO2 emission data in EAF from coal and NG, flux
        m_co2_coal = source['co2_coal'] # tonne CO2. co2 emission from coal consumption.
        m_co2_ng = source['co2_ng'] # tonne CO2. co2 emission from ng consumption.
        co2_eaf_flux = m_eaf_fluxes* (44/100.09 )   # flux eaf emissions for limestone

        #CO2 emission data in EAF from elec
        cr_eaf_elec = eaf_elec(m_steel, m_eaf_coal, m_eaf_ng, hhv_coal) # GJ of electricity
        elec = elec_co2()
        country= self.country
        years = elec['years'][20:25] #years in database
        # print(f"years: {years}")

        c_elec = co2_int(self,years)

        #user input for cr_eaf
        cr_eaf_elec = self.eaf_elec*np.ones(5)*m_steel*0.0036 # conver to GJ

        m_co2_eaf_elec = np.array(cr_eaf_elec) * np.array(c_elec)  # tonne co2. Element-wise multiplication
        print(m_co2_eaf_elec)
        #ASU
        q_asu_elec = mca(v_eaf_o2,c_elec)['elec'] # GJ of electricity needed
        m_asu_co2 = mca(v_eaf_o2,c_elec)['co2'] # tonne CO2 emisison due to electricity utilization for air seperation
        m_asu_o2 = mca(v_eaf_o2,c_elec)['o2'] # tonne of o2 separated. tonne of o2 needed

        #total co2 emission from EAF. tonne of CO2e
        co2_eaf = m_co2_eaf_elec + m_co2_ng + m_co2_coal + co2_eaf_flux

        #total CO2 emission from ASU. tonne of CO2e
        co2_asu = m_asu_co2

        #total co2 emission. tonne of CO2e
        t_co2 = co2_eaf + co2_asu
        t_co2_fossil = t_co2 - m_co2_eaf_elec
        # print(f"t_co2_fossil:{t_co2_fossil/m_steel}")
        #gettheupperboundofco2emissionaccordingtoIEA-SDSscenario.
        ub=co2_ub(m_steel)#gettheIndiasteelindustryCO2emissionupperboundbysatisfyIEA-SDSscenario. tonne/year

        ############################################################################################################################################
        #Economic analysis
        # carbon tax
        co2_tax = self.co2_tax * np.array(er(country)) #carbon tax $/tonne
        cost_carbon_tax = t_co2_fossil * co2_tax #  $ paid for carbon tax

        #CAPEX
        cepci1 = cep(2017)[0] # get the base cost year. source: Techno-economic evaluation of innovative steel production technologies (wupperinst.org)
        cepci2 = cep(2020)[0] #get the most up to date value available.
        ppp2= pppv(country,2020) # get the ppp for the country of interest

        #ASU source: Yang, F., J. C. Meerman, and A. P. C. Faaij. "Carbon capture and biomass in industry: A techno-economic analysis and comparison of negative emission options." Renewable and Sustainable Energy Reviews 144 (2021): 111028.
        capacity2_asu = capexes['Base Scale'][2]  #Assume the capacity is the same as base scale.
        n_asu = m_asu_o2/capacity2_asu  # number of asu
        #cost2_asu_add = n_asu*capa('ASU',capacity2_asu,cepci1,cepci2,ppp2)['Additional'] # local current unit. depends on ppp2
        cost2_asu= n_asu*capexs(capacity2_asu,cepci1,cepci2,ppp2)['ASU'] # total cost for producting m_steel tonne of steel in specific year. local current unit. depends on ppp2

        #EAF source: Yang, F., J. C. Meerman, and A. P. C. Faaij. "Carbon capture and biomass in industry: A techno-economic analysis and comparison of negative emission options." Renewable and Sustainable Energy Reviews 144 (2021): 111028.
        capacity2_eaf = capexes['Base Scale'][8] # Assume the capacity is the same as base scale.
        n_eaf = m_steel/capacity2_eaf # number of eaf
        #cost2_eaf_add = n_eaf * capa('EAF',capacity2_eaf,cepci1,cepci2,ppp2)['Additional'] # local current unit. depends on ppp2
        cost2_eaf = n_eaf * capexs(capacity2_eaf,cepci1,cepci2,ppp2)['EAF'] # local current unit. depends on ppp2

        #total capex
        t_capex = np.array(cost2_eaf) + np.array(cost2_asu)#/np.array(er(country)) # total capex . # local current unit. depends on ppp2
        #t_capex_add = np.array(cost2_asu_add) + np.array(cost2_eaf_add) # additional capex in year. # local current unit. depends on ppp2

        #OPEX
        #OPEX material/energy price
        scrap_price = []
        limestone_price = []
        coal_price = []
        ng_price = []
        electricity_price = []
        oxygen_price = []
        y_i = 2020 #initial/baseline year
        y_f = 2040 # final year
        for y in years:
            scrap_price_update = self.scrap_price + (y - y_i) * self.limestone_price * (self.scrap_price_change/100)/(y_f - y_i)
            scrap_price.append(scrap_price_update)
            limestone_price_update = self.limestone_price +  (y - y_i) * self.limestone_price * (self.limestone_price_change/100)/(y_f - y_i)
            limestone_price.append(limestone_price_update)
            coal_price_update = self.coal_price + (y - y_i) * self.coal_price *  (self.coal_price_change/100)/(y_f - y_i)
            coal_price.append(coal_price_update)
            ng_price_update = self.ng_price + (y - y_i) * self.ng_price * (self.ng_price_change/100)/(y_f - y_i)
            ng_price.append(ng_price_update)
            electricity_price_update = self.electricity_price + (y - y_i) * self.electricity_price * (self.electricity_price_change/100)/(y_f - y_i)
            electricity_price.append(electricity_price_update)
            oxygen_price_update = self.oxygen_price + (y - y_i) * self.oxygen_price * (self.oxygen_price_change/100)/(y_f - y_i)
            oxygen_price.append(oxygen_price_update)
        # print(f"oxygen price: {oxygen_price}")

        cost_coal = np.array(coal_price) * m_eaf_coal #coal price: usd/t. ($)
        cost_ng = np.array(ng_price) * m_eaf_ng #price: usd/GJ.  ($)
        cost_limestone = np.array(limestone_price) * m_eaf_fluxes # price: usd/t. ($)
        cost_scrap = np.array(scrap_price) * (m_eaf_scrap + m_eaf_carbon_steel)  # price: usd/t. cost of scrap. assume cost of scrap and carbon steel are the same. ($)
        cost_elec = np.array(electricity_price) * (q_asu_elec + cr_eaf_elec) #price: usd/GJ ($)
        cost_oxygen = np.array(oxygen_price) * m_asu_o2 # price usd/tonne ($)
        # print(f"oxygen tonne: {m_asu_o2}; cost of oxygen: {cost_oxygen}")
        m_water = m_eaf_water #total fresh water consumption. Nm3. (=1 tonne of water)

        tc_onm = np.array(m_steel) * 0.8 * np.array(er(country)) #assume steel operation and maintenance cost is $0.8/tonne. source 3.
        tc_ins_loc = np.array(t_capex) * 0.045 # maintenance and labor cost. source 3. Indian Rupee.
        tc_labor = 100*60000/1360000*np.array(m_steel) # assume number of labor needed is linearly correlated to total amount of steel produced. source 3.
        tc_administrative = 0.3 * tc_onm # administrative labor cost. Rupee. source 3.
        t_omt = tc_onm + tc_ins_loc + tc_labor + tc_administrative # operation & management cost of eaf

        tcost_fossil = (cost_ng + cost_coal)* np.array(er(country)) # fossil fuel cost in local current unit. e.g. Rupee if country='India'
        tcost_elec = cost_elec * np.array(er(country)) # electricity cost in local current unit. e.g. Rupee if country='India'
        tcost_iron_ore = cost_scrap * np.array(er(country)) # iron_ore cost in local current unit. e.g. Rupee if country='India'
        tcost_flux = cost_limestone * np.array(er(country)) # limestone cost in local current unit. e.g. Rupee if country='India'
        tcost_oxygen = cost_oxygen * np.array(er(country)) # oxygen cost in local current unit. e.g. Rupee if country='India'

        # print(co2_asu/m_steel)
        tcost_water = [] #np.array(cw(m_water)) * np.array(er(country))  #cost of water. ($)
        opex = []
        for i, water in enumerate(m_water):
            cost_water = cw(water) * er(country)  #cost of water. ($)
            tcost_water.append(cost_water[0])
            opexi = t_omt[i] + tcost_fossil[i] + \
                tcost_elec[i] + tcost_iron_ore[i] + tcost_flux[i] + tcost_oxygen[i] + cost_water # total operation cost in local current unit. e.g. Rupee if country='India'
            opex.append(opexi[0])
        print(m_co2_eaf_elec/m_steel)
        return {
            'country': country,
            'co2_eaf': co2_eaf / m_steel,
            'co2_asu': co2_asu / m_steel,
            't_co2_fossil': t_co2_fossil/m_steel,
            'co2_coal': m_co2_coal / m_steel,
            'co2_ng': m_co2_ng / m_steel,
            'co2_electricity': (m_co2_eaf_elec + m_asu_co2)/m_steel,
            'co2_flux': co2_eaf_flux/m_steel,
            't_co2': t_co2 / m_steel,
            'ub': ub / m_steel,
            'years': years,
            'tc_onm': tc_onm / m_steel / np.array(er(country)),
            'tc_ins_loc': tc_ins_loc / m_steel/ np.array(er(country)),
            'tc_labor': tc_labor / m_steel/ np.array(er(country)),
            'tc_administrative': tc_administrative / m_steel/ np.array(er(country)),
            'tcost_fossil': tcost_fossil / m_steel/ np.array(er(country)),
            'tcost_elec': tcost_elec / m_steel/ np.array(er(country)),
            'tcost_iron_ore': tcost_iron_ore / m_steel/ np.array(er(country)),
            'tcost_flux': tcost_flux / m_steel/ np.array(er(country)),
            'tcost_oxygen': tcost_oxygen / m_steel/ np.array(er(country)),
            'tcost_water': np.array(tcost_water) / m_steel/ np.array(er(country)),
            'opex': opex / m_steel/ np.array(er(country)),
            't_capex': t_capex / m_steel/ np.array(er(country)),
            'cost from carbon tax': cost_carbon_tax/ m_steel/ np.array(er(country)),
            'm_steel': m_steel,
            't_omt': t_omt/m_steel/np.array(er(country)),
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
                'unit': 'tonne CO\u2082 / tonne steel',
                'axis': 0,
                'datasets': [
                    {
                        'label': 'EAF',
                        'color': 'indigo_dark',
                        'data': results['co2_eaf'],
                    },
                    {
                        'label': 'Air separation unit',
                        'color': 'blue',
                        'data': results['co2_asu'],
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
                'unit': 'USD $ / tonne steel',
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
                        'label': 'Operation & Management of EAF',
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
        country = results['country'].title()
        print(f"CO2 emission:{results['t_co2']};opex:{results['opex']}; capex:{results['t_capex']} ")
        #plot trajectory line graph for CO2 emissions
        plot1 = plt.figure(1)
        plt.plot(results['years'], results['co2_eaf'], marker='*', label='EAF', color='blueviolet')
        plt.plot(results['years'], results['co2_asu'], marker='o', label='Air separation unit', color='blue')
        plt.plot(results['years'], results['t_co2'], marker='s', label='Total', color='red')
        plt.plot(results['years'], results['ub'], linestyle='dashed', label='Allowable CO2 emission upper bound:IEA-SDS', color='forestgreen')
        #plt.vlines(2020, 0, 20, label='Past/future', color='black', linestyles='dashed')  # plot vertical lines
        plt.xticks(np.arange(min(results['years']),max(results['years'])+1,5))
        plt.title('CO\u2082 emission for EAF routes')
        plt.xlabel('Year')
        plt.ylabel('CO\u2082 emissions (tonne CO\u2082/tonne steel)')
        plt.legend()
        #plt.ylim([0, 600])  # make sure each route has the same y axis length and interval

        #plot trajectory line graph for operation/capital cost
        fig, ax = plt.subplots()
        ax.plot(results['years'], results['tc_onm'], marker = 's', label='Operation',color='darkorange')
        ax.plot(results['years'], results['tc_ins_loc'], marker = 's', label='Insurance and Tax',color='tan')
        ax.plot(results['years'], results['tc_labor'], marker = 's', label='Labor',color='saddlebrown')
        ax.plot(results['years'], results['tc_administrative'], marker = 's', label='Administrative',color='indigo')
        ax.plot(results['years'], results['tcost_water'], marker = 's', label='Water',color='royalblue')
        ax.plot(results['years'], results['tcost_oxygen'], marker = 's', label='Oxygen',color='blue')
        ax.plot(results['years'], results['tcost_flux'], marker = 'd', label = 'Fluxes', color='green')
        ax.plot(results['years'], results['tcost_elec'], marker = 'x', label='Electricity', color='orange')
        ax.plot(results['years'], results['tcost_fossil'], marker='p', label='Fossil Fuel', color='olive')
        ax.plot(results['years'], results['tcost_iron_ore'], marker='+', label='Scrap', color='purple')
        ax.plot(results['years'], results['opex'], marker='*', label='OPEX', color='red')
        ax.plot(results['years'], results['cost from carbon tax'], marker='*', label='Cost from Carbon Tax', color='turquoise')
        ax2 = ax.twinx() #add a second y axis
        ax2.plot(results['years'], results['t_capex'], marker='o', label='CAPEX', color='navy')
        #ax2.plot(results['years'], results['t_capex_add'], marker='^', label='Additional CAPEX', color='slateblue')
        ax.set_xlabel('Year')
        ax.set_ylabel(f"OPEX ($/tonne steel)")
        ax2.set_ylabel(f"CAPEX ($/tonne steel)", color='navy')
        ax.legend()
        plt.legend()
        plt.xticks(np.arange(min(results['years']), max(results['years']) + 1, 5))
        ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0)) #use scientific tick-label for y axis.
        plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0)) #use scientific tick-label for y axis.
        plt.title('OPEX/CAPEX for EAF routes')
        #plt.ylim([0, 400000])  # make sure each route has the same y axis length and interval
        plt.show()
