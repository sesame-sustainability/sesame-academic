"""
Function unit: 1 tonne of cement.
cement types, blending materials flow, co2 emissions
source: 1. Devaki's ppt: 90% cement industry ppt. page 29
2. Prakasan, Sanoop, Sivakumar Palaniappan, and Ravindra Gettu. "Study of Energy Use and CO 2 Emissions in the
Manufacturing of Clinker and Cement."Journal of The Institution of Engineers (India): Series A 101.1 (2020): 221-232.
3. from Devaki. Technology paper 13: Reducing clinker factor in fly ash based Portland Pozzolana Cement (PPC); Confederation of Indian Industry and National Council for Cement and Building Material, p. 48
4. IS:455-1989; Technology paper no. 14: Reducing clinker factor in slag based Portland Slag Cement (PSC);
Confederation of Indian Industry and National Council for Cement and Building Material, p. 48; Confederation of Indian Industry and National Council for Cement and Building Material, p. 48
"""

import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

from analysis.system.industry.cement.clinkerization import kiln
from analysis.system.industry.cement.quarry import quarry as qua
from analysis.system.industry.cement.quarry import crushing as cru
from analysis.system.industry.cement.fuel_type import fuel_type as ft, options as fuel_type_options
from analysis.system.industry.cement.project_elec_co2 import elec_co2 as ec
from analysis.system.industry.cement.elec_input import user_inputs_ft_cap as elec_inputs
from analysis.system.industry.cement.elec_input import co2_int #, COUNTRIES
from analysis.system.industry.cement.clinker_alternatives import clinker_alternative as ca
from analysis.system.industry.cement.cement_trajectory import cements
#from analysis.system.industry.cement.co2_emission_scenarios import emission_scenario as es
#from analysis.system.industry.cement.eppa import eppa_senarios not applicable for other countries other than India
from analysis.system.industry.cement.cost import capexs
from analysis.system.industry.cement.cepci import cepci_v
from analysis.system.industry.cement.ppp import pppv
from analysis.system.industry.cement.exchange_rate import exchange_country
from analysis.system.industry.cement.material_cost import water as cw, c_materials as mc  # get price of water
from analysis.system.industry.cement.ccs import ccs  # get ccs capex, opex, material consumption, etc.
from analysis.system.industry.cement.ccs_transport_storage import co2_transport, co2_storage, options_storage



from core.common import InputSource, Color, Versioned
import core.conditionals as conditionals
from core.inputs import OptionsInput, ContinuousInput, PercentInput, Default, InputGroup, ShareTableInput,Tooltip
import core.validators as validators

dirname = os.path.dirname(__file__)

#scenarios from eppa. million tonne co2 at specific year
"""reference = eppa_senarios('Reference')['co2']['Reference'][4:9] # India cement Co2 emission with Reference scenario from EPPA
electrification = eppa_senarios('Electrification')['co2']['Electrification'][4:9]
ng_support = eppa_senarios('Natural Gas Support')['co2']['Natural Gas Support'][4:9]
resource_efficiency = eppa_senarios('Resource Efficiency')['co2']['Resource Efficiency'][4:9]
low_carbon_price = eppa_senarios('Low Carbon Price')['co2']['Low Carbon Price'][4:9]
high_carbon_price = eppa_senarios('High Carbon Price')['co2']['High Carbon Price'][4:9]
ccs_low_carbon_price = eppa_senarios('CCS and Low Carbon Price')['co2']['CCS and Low Carbon Price'][4:9]
ccs_high_carbon_price = eppa_senarios('CCS and High Carbon Price')['co2']['CCS and High Carbon Price'][4:9]
"""
years = ec()['years'][20:25] # get the years of electricity prejection


class Cement(InputSource, Versioned):

    @classmethod
    def user_inputs(cls):
        countries = ['India', 'China', 'United States', 'EU-27']
        return elec_inputs(cls,countries) + [
            OptionsInput(
                'cement_type', 'Cement type',
                defaults=[Default('Ordinary Portland Cement (OPC)')],
                options=[
                    'Ordinary Portland Cement (OPC)',
                    'Portland Pozzolana Cement (PPC)',
                    'Portland Slag Cement (PSC)',
                ],
        tooltip=Tooltip(
                    'Defaults for Stages & Cement Types',
                    source=['Prakasan,2019', 'CSI'],
                    source_link=['https://www.researchgate.net/publication/337333610_Study_of_Energy_Use_and_CO2_Emissions_in_the_Manufacturing_of_Clinker_and_Cement','https://www.ifc.org/wps/wcm/connect/0bd665ef-4497-4d6d-9809-9724888585d2/india-cement-carbon-emissions-reduction.pdf?MOD=AJPERES&CVID=jWEGLpL', ])
            ),
            InputGroup('quarry_transport','Quarry & Transportation', children = [
                ContinuousInput(
                    'limestone_transportation_distance', 'Limestone transportation distance',
                    unit='km',
                    defaults=[Default(1)],
                ),
                OptionsInput(
                    'limestone_transportation_energy_source', 'Limestone transportation energy source',
                    options=['Diesel', 'Electricity','Natural Gas','Hydrogen'],
                    defaults=[Default('Diesel')],
                    tooltip=Tooltip('Quarry Sources',
                        source=['Marceau','Keys'],source_link=['http://large.stanford.edu/courses/2016/ph240/pourshafeie2/docs/marceau-2007.pdf','https://www.pbl.nl/sites/default/files/downloads/pbl-2019-decarbonisation-options-for-the-dutch-steel-industry_3723.pdf'])
                ),
            ]),
            InputGroup('crushing_fuel_prep','Crushing & Fuel preparation', children = [
                OptionsInput(
                'preheat_stage', 'Preheating stages',
                options=['4', '5', '6'],
                defaults=[Default('6')],
            ),
            ]),
            InputGroup('clinkerization','Clinkerization', children = [
                OptionsInput(
                    'fuel_type', 'Fuel type',
                    options=fuel_type_options,
                    defaults=[Default('Bituminous high_volatile b')],
                ),
                ShareTableInput(
                    'f_clinker_alternative_opc', '% of clinker alternative',
                    conditionals=[conditionals.input_equal_to('cement_type', 'Ordinary Portland Cement (OPC)')],
                    columns=[None],
                    rows=[
                        ShareTableInput.Row(
                            'Clinker (90 to 95%)',
                            cells=[
                                ShareTableInput.Cell(defaults=[Default(95)]),
                            ],
                        ),
                        ShareTableInput.Row(
                            'Gypsum (5 to 10%)',
                            cells=[
                                ShareTableInput.Cell(defaults=[Default(5)]),
                            ],
                        ),
                    ],
                ),
                ShareTableInput(
                    'f_clinker_alternative_ppc', '% of clinker alternative',
                    conditionals=[conditionals.input_equal_to('cement_type', 'Portland Pozzolana Cement (PPC)')],
                    columns=[None],
                    rows=[
                        ShareTableInput.Row(
                            'Clinker (60 to 80%)',
                            cells=[
                                ShareTableInput.Cell(defaults=[Default(70)]),
                            ],
                        ),
                        ShareTableInput.Row(
                            'Fly ash (15 to 35%)',
                            cells=[
                                ShareTableInput.Cell(defaults=[Default(25)]),
                            ],
                        ),
                        ShareTableInput.Row(
                            'Gypsum (5 to 10%)',
                            cells=[
                                ShareTableInput.Cell(defaults=[Default(5)]),
                            ],
                        ),
                    ]
                ),
                ShareTableInput(
                    'f_clinker_alternative_psc', '% of clinker alternative',
                    conditionals=[conditionals.input_equal_to('cement_type', 'Portland Slag Cement (PSC)')],
                    columns = [None],
                    rows = [
                        ShareTableInput.Row(
                            'Clinker (35 to 70%)',
                            cells=[
                                ShareTableInput.Cell(defaults=[Default(45)]),
                            ],
                        ),
                        ShareTableInput.Row(
                            'Slag (45 to 60%)',
                            cells=[
                                ShareTableInput.Cell(defaults=[Default(50)]),
                            ],
                        ),
                        ShareTableInput.Row(
                            'Gypsum (5 to 10%)',
                            cells=[
                                ShareTableInput.Cell(defaults=[Default(5)]),
                            ],
                        ),
                    ],
                ),
            ]),
            OptionsInput(
                'ccs', 'With CCS?',
                options=['Yes', 'No'],
                defaults=[Default('No')],
            ),
            OptionsInput(
                'ccs_solvent', 'CCS solvent',
                defaults=[Default('MEA')],
                options=['MEA', 'CESAR'],
                conditionals=[conditionals.input_equal_to('ccs', 'Yes')],
            ),
            PercentInput(
                'co2_capture_rate', 'CO2 Capture rate',
                unit='%',
                defaults=[Default(90)],
                conditionals=[conditionals.input_equal_to('ccs', 'Yes')],
            ),
            OptionsInput(
                'ccs_heating_source', 'CCS heating source',
                options=['NG', 'Electricity'],
                defaults=[Default('NG')],
                conditionals=[conditionals.input_equal_to('ccs', 'Yes')],
            ),
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
            ),
        ]

    def run(self):
        m_cement = cements()['production'][4:9] # default country is India. Amount of cement to be produced (tonne)
        country=self.country
        elec_co2 = co2_int(self,years)  # (tonne CO2/GJ)
        # print(f"elec co2: {elec_co2}")
        # print(self.cement_type)
        # clinkerization, cooling and storing
        if self.cement_type == 'Ordinary Portland Cement (OPC)':
            type = 'Ordinary Portland Cement'
            f_clinker = self.f_clinker_alternative_opc # get clinker alternative data
            m_clinker = f_clinker[0]/100 * m_cement # tonne of clinker needed. source 1.
            m_gypsum = f_clinker[1]/100 * m_cement # tonne of gypsum needed. source 1.
            m_fly_ash_co2 = 0 # tonne of gypsum needed. source 1.
            m_slag_co2 = 0 # tonne of gypsum needed. source 1.
            m_gypsum_co2 = ca(0, 0, m_gypsum)['gypsum']  # tonne CO2 emission due to gypsum use
            #energy consumption for grinding
            q_grind_clinker_elec = (26*0.0036)/0.91 * m_clinker # GJ of electricity needed for 1 tonne of opc produced. source 2. assume linear correlation with m_clinker (GJ)
            q_grind_clinker_elec_co2 = q_grind_clinker_elec * elec_co2 # tonne CO2 emitted due to electricity used for grinding (tonne)

        elif self.cement_type == 'Portland Pozzolana Cement (PPC)':
            type = 'Portland Pozzolana Cement'
            f_clinker = self.f_clinker_alternative_ppc
            m_clinker = f_clinker[0]/100 * m_cement  # tonne of clinker needed. source 1.
            m_fly_ash = f_clinker[1]/100 * m_cement  # tonne of pozzolona needed. source 1.
            m_gypsum = f_clinker[2]/100 * m_cement  # tonne of gypsum needed. source 1.
            m_fly_ash_co2 = ca(m_fly_ash,0,m_gypsum)['fly ash'] # tonne CO2 emission due to fly ash use
            m_slag_co2 = 0 # tonne CO2 emission due to slag use
            m_gypsum_co2 = ca(m_fly_ash, 0, m_gypsum)['gypsum']  # tonne CO2 emission due to gypsum use
            #energy consumption for grinding
            q_grind_clinker_elec = (23.74*0.0036)/0.68*f_clinker[0]/100 * m_cement # GJ of electricity needed for 1 tonne of opc produced. source 2. assume linear correlation with m_clinker (GJ)
            q_grind_clinker_elec_co2 = q_grind_clinker_elec * elec_co2 # tonne CO2 emitted due to electricity used for grinding (tonne)

        elif self.cement_type == 'Portland Slag Cement (PSC)':
            type = 'Portland Slag Cement'
            f_clinker = self.f_clinker_alternative_psc
            m_clinker = f_clinker[0]/100 * m_cement # tonne of clinker needed. source 1.
            m_slag = f_clinker[1]/100 * m_cement # tonne of blast furnace slag needed. source 1.
            m_gypsum = f_clinker[2]/100 * m_cement  # tonne of gypsum needed. source 1.
            m_fly_ash_co2 = 0 # tonne of fly ash needed.
            m_slag_co2 = ca(0,m_slag,m_gypsum)['slag'] # tonne CO2 emission due to slag use
            m_gypsum_co2 = ca(0,m_slag,m_gypsum)['gypsum']   # tonne CO2 emission due to gypsum use
            #energy consumption for grinding. the number 23.74 is assuming linear correlation with data point (0.91,26) and (0.68,23.74)
            q_grind_clinker_elec = (23.74*0.0036)/0.68*f_clinker[0]/100 * m_cement # GJ of electricity needed for 1 tonne of opc produced. source 2. assume linear correlation with m_clinker (GJ)
            q_grind_clinker_elec_co2 = q_grind_clinker_elec * elec_co2 # tonne CO2 emitted due to electricity used for grinding (tonne)

        #mc = pd.read_csv(os.path.join(dirname, 'material_cost.csv'), usecols=['material','price']) #mc: material cost
        preheat_stage = self.preheat_stage

        fuel = ft(fuel_type_options.index(self.fuel_type))
        # print(f'fuel type: {fuel}')
        hhv = fuel['hhv'] #hight heating value of fuel MJ/kg=GJ/tonne
        c_fuel = fuel['c'] # wt% of carbon in fuel
        kil = kiln(m_clinker,float(preheat_stage),hhv,c_fuel,elec_co2) #get information related to kiln and preheater
        m_fuel_kiln = kil['fuel kiln'] # tonne of coal used in kiln
        m_fuel_kiln_co2 = kil['fuel kiln co2'] # tonne of CO2 emitted due to fuel used in clinkerization
        m_elec_kiln_co2 = kil['elec kiln co2'] # tonne of CO2 emitted due to electricity used in clinkerization
        m_dry_co2 = kil['m drying co2'] # tonne of CO2 emitted due to limestone drying out.

        #CO2 emission from clinkerization itself
        m_limestone_co2 = kil['clinkerization'] # tonne CO2 emission due to clinkerization reaction.

        #total co2 emission from kiln
        t_co2_kiln = m_fuel_kiln_co2 + m_elec_kiln_co2 + m_dry_co2 + m_limestone_co2  # tonne of CO2

        # print(f'kiln related emissions:fuel use: {m_fuel_kiln_co2},elec related: {m_elec_kiln_co2},dry out related: {m_dry_co2},clinker reaction: {m_limestone_co2}')
        #CO2 emission from clinker alternative
        t_co2_clinker_alternative = m_fly_ash_co2 + m_slag_co2 + m_gypsum_co2

        # energy consumption for packing and others
        q_packing_others_elec = (0.65 + 3.15)*0.0036 * m_cement # GJ of electricity needed for 1 tonne of opc produced. source 2.
        q_packing_others_elec_co2 = q_packing_others_elec * elec_co2 # tonne CO2 emitted due to electricity used for packing and others

        #CO2 emission for cement production from clinker
        t_co2_cement = q_grind_clinker_elec_co2 + q_packing_others_elec_co2 # tonne of CO2 emitted from clinker to cement

        #quarry
        m_limestone = kil['m limestone'] # tonne of limestone
        distance = self.limestone_transportation_distance
        transport = self.limestone_transportation_energy_source
        quar = qua(m_limestone,distance,elec_co2,transport) #get information for quarry process

        m_diesel_extract = quar['m diesel extract'] # tonne of diesel needed for limestone extraction
        q_elec_extract = quar['q elec extract'] # GJ of electricity needed for limestone extraction
        m_transport = quar['transport'] # GJ of electricity or tonne of fuel for limestone transportation.

        m_elec_extract_co2 = quar['elec extract co2'] # tonne CO2 emitted due to limestone extraction using electricity
        m_diesel_extract_co2 = quar['diesel extract co2'] # tonne CO2 emission due to diesel used for extraction
        m_transport_co2 = quar['transport co2'] # tonne of CO2 emitted due to limestone transportation

        # total CO2 emission from quarry
        t_co2_quarry = m_diesel_extract_co2 + m_elec_extract_co2 + m_transport_co2

        # fuel preparation by electricity
        q_fuel_prep_elec = kil['q fuel prepare'] # GJ electricity needed for fuel preparation
        m_fuel_prepare_elec_co2 = kil['m fuel prepare co2'] # tonne CO2 emisison due to fuel preparation

        #crushing+fuel preparing
        t_co2_crushing = cru(m_limestone,elec_co2)['elec crushing co2'] + m_fuel_prepare_elec_co2 # tonne CO2 emitted due to limestone extraction and fuel preparation using electricity

        #total CO2 emission for cement
        t_co2 = t_co2_quarry + t_co2_kiln + t_co2_crushing + t_co2_cement + t_co2_clinker_alternative # tonne CO2 emitted per tonne of cement produced

        # co2 emission by source
        co2_limestone = m_limestone_co2
        co2_alternative = t_co2_clinker_alternative
        co2_fossil_fuel = m_fuel_kiln_co2 +  m_dry_co2 + m_diesel_extract_co2 + m_transport_co2
        co2_electricity = m_elec_kiln_co2 + q_grind_clinker_elec_co2 + q_packing_others_elec_co2 + m_elec_extract_co2 + t_co2_crushing

        if transport == 'Electricity': #elec transport account for indirect emission
            t_co2_direct = m_fuel_kiln_co2 + m_diesel_extract_co2 + m_limestone_co2 + m_dry_co2 + t_co2_clinker_alternative
            # total indirect CO2 emission for cement
            t_co2_indirect =  m_elec_kiln_co2 + q_grind_clinker_elec_co2 + q_packing_others_elec_co2 + m_elec_extract_co2 + m_transport_co2 +\
                cru(m_limestone, elec_co2)['elec crushing co2'] + m_fuel_prepare_elec_co2
            c_transport = m_transport * mc()['India'][3]/0.0036 # limestone transportation cost (Rupee)
        else: #transport == 'diesel'/'ng','h2': #diesel transport account for direct emission
            # total direct CO2 emission for cement
            t_co2_direct = m_fuel_kiln_co2 + m_diesel_extract_co2 + m_limestone_co2 + m_dry_co2 + m_transport_co2 + t_co2_clinker_alternative
            # total indirect CO2 emission for cement
            t_co2_indirect =  m_elec_kiln_co2 +  q_grind_clinker_elec_co2 + q_packing_others_elec_co2 + m_elec_extract_co2 +  \
                cru(m_limestone, elec_co2)['elec crushing co2'] + m_fuel_prepare_elec_co2
            if transport == 'Diesel':
                c_transport = m_transport*1000/0.846* mc()['India'][4] # density diesel = 0.846 kg/l (https://www.engineeringtoolbox.com/fuels-higher-calorific-values-d_169.html), limestone transportation cost (Rupee)
            elif transport == 'Natural gas':
                c_transport = m_transport * 49.5 * mc()['India'][2]  # lhv ng = 49.5 GJ/tonne. limestone transportation cost (Rupee)
            else: #hydrogen
                c_transport = m_transport * mc()['India'][5] *1000 # limestone transportation cost (Rupee)


        #Economic analysis
        #Total capital investment
        cepci2 = cepci_v(2020)[40] #get the specific year's cepci. only history data available, lack predicted value, et. 2035, 2040
        # print(f'cepcie2{cepci2}')
        ppp2 = pppv()  #use the defaul country =India, year = (2000,2021,5))
        capacity = 117000000 #suppose all the cement plant has same capacity. (tonne/yr). suppose the maximum capacity is 117 million tonne/year. source: https://www.cfic.dz/images/telechargements/global%20cement%20magazine%20decembre%202020.pdf.
        n_plant = m_cement/capacity  # number of plant needed.
        y_plant = 30 # plant life time 30 years.
        capex_total = n_plant * capexs(capacity,cepci2,ppp2) / y_plant #  capital investment each year.  Local currency unit (e.g. Rupee)


        #Operation cost
        # print(mc['price'][0])
        c_limestone =  mc()['India'][0] * np.array(m_limestone)  #India ruppee spend for limestone. (Rupee)
        c_coal = np.array(m_fuel_kiln) * mc()['India'][1]  #India ruppee spend for coal. (Rupee)
        # diesel desity= 0.823 kg/L. https://www.quora.com/What-is-the-weight-of-1-liter-diesel#:~:text=According%20to%20Wiki%2C%20the%20density,That's%20at%20STP.
        c_diesel = np.array(m_diesel_extract)*1000/0.846 * mc()['India'][4] # density diesel = 0.846 kg/l (https://www.engineeringtoolbox.com/fuels-higher-calorific-values-d_169.html) India ruppee spend for limestone extraction using diesel. (Rupee)
        c_elec = (np.array(q_grind_clinker_elec) + np.array(q_packing_others_elec) + np.array(q_fuel_prep_elec)) * mc()['India'][3]/0.0036  #India ruppee spend for electricity. (rupee)
        c_onm = np.array(m_cement) * 0.8  #India ruppee spend for operation and maintenance. source: Roussanaly, Simon, et al. "Techno-economic analysis of MEA CO2 capture from a cement kiln–impact of steam supply scenario." Energy Procedia 114 (2017): 6229-6239
        # be cautious that capex is related to tonne of cement.
        c_ins_loc = np.array(capex_total) *0.045  #India ruppee spend for insurance and location, maintenance labor. source: Roussanaly, Simon, et al. "Techno-economic analysis of MEA CO2 capture from a cement kiln–impact of steam supply scenario." Energy Procedia 114 (2017): 6229-6239
        c_labor = 100*60000/1360000*np.array(m_cement) #labor cost. assume number of labor needed is linearly correlated to total amount of cement produced. base is from reference:.Roussanaly, Simon, et al. "Techno-economic analysis of MEA CO2 capture from a cement kiln–impact of steam supply scenario." Energy Procedia 114 (2017): 6229-6239
        c_administrative = 0.3*c_onm # administrative labor cost
        opex = c_transport + c_limestone + c_coal + c_diesel + c_elec + c_onm + c_ins_loc + c_labor + c_administrative  #total operation cost for cement without ccs (Rupee)

        # print(f'cost, capex: {capex_total}, opex:{opex}')

        co2_ccs = 0
        ccs_cost_transport = 0
        ccs_cost_storage = 0

        # CCS CAPEX
        if self.ccs == 'Yes':
            cap_r = self.co2_capture_rate
            solvent = self.ccs_solvent
            regeneration_u = self.ccs_heating_source

            cost_ccs = ccs(t_co2_direct, solvent, cap_r, regeneration_u, country)
            co2_ccs = cost_ccs['CO2']
            t_co2_kiln = (m_fuel_kiln_co2+m_limestone_co2) * (1-cap_r/100) + m_dry_co2 + m_elec_kiln_co2 # CO2 emission from kiln after capture.
            cost2_ccs = np.array(cost_ccs['tpc']) * cepci_v(2020)[40] / cepci_v(2008)[28] * np.array(exchange_country(country)[0]) / np.array(
                exchange_country('EU_27')[0])  # CAPEX of CCS. convert from 2015 euro to 2020 for country interested
            # print(f"ccs fixed cost:{cost2_ccs}")  # very small fixed cost compared to the main steel making plant
            #p_mea = 1.042  # 2015. source: Manzolini, Giampaolo, et al. "Economic assessment of novel amine based CO2 capture technologies integrated in power plants based on European Benchmarking Task Force methodology." Applied Energy 138 (2015): 546-558.
            #p_cesar = 7  # 2015. source: Manzolini, Giampaolo, et al. "Economic assessment of novel amine based CO2 capture technologies integrated in power plants based on European Benchmarking Task Force methodology." Applied Energy 138 (2015): 546-558.

            #CCS transportation and storage cost
            co2_transportation_distance = float(self.co2_transportation_distance)  #co2 transport to storage location. (km)
            ccs_co2_transport = co2_transport(co2_transportation_distance) #co2 transportation price ($_2020/tCO2)
            ccs_cost_transport = ccs_co2_transport * (m_fuel_kiln_co2+m_limestone_co2) * cap_r/100 # co2 transportation cost ($_2020)
            # print(f'ccs transport cost: {ccs_co2_transport}')

            ccs_co2_storage = co2_storage(options_storage.index(self.co2_storage)) #co2 storage price ($_2020/tCO2)
            ccs_cost_storage = ccs_co2_storage * (m_fuel_kiln_co2+m_limestone_co2) * cap_r/100 # co2 storage cost ($_2020)
            # print(f'ccs storage cost: {ccs_co2_storage}')

            #capex_add += np.array(cost2_ccs)
            capex_total += (np.array(cost2_ccs) + (np.array(ccs_cost_transport) + np.array(ccs_cost_storage)) * exchange_country(country)[0]/exchange_country('United_States')[0])/ y_plant

            # total direct/indirect co2 emission with ccs considered
            if regeneration_u == 'Electricity':
                t_co2_indirect = t_co2_indirect + co2_ccs
                t_co2_direct = t_co2_direct - (m_fuel_kiln_co2+m_limestone_co2) * cap_r/100
            elif regeneration_u =='NG':
                t_co2_indirect = t_co2_indirect
                t_co2_direct = t_co2_direct - (m_fuel_kiln_co2+m_limestone_co2) * cap_r/100 + co2_ccs

            t_co2 = t_co2_direct + t_co2_indirect #+ t_co2_clinker_alternative

            # OPEX
            opex_add = (cost_ccs['raw material'] + cost_ccs['utility'] + cost_ccs['operation_management'])*cepci_v(2020)[40] /cepci_v(2008)[28] * exchange_country(country)[0]/\
                exchange_country('EU_27')[0] # (Rupee)
            opex = np.array(opex) + np.array(opex_add)

        # print( (t_co2_direct)  / m_cement)
        # print(t_co2/ m_cement)
        return {
            'm_cement': m_cement,

            't_co2': t_co2 / m_cement,
            't_co2_direct': t_co2_direct / m_cement,
            't_co2_indirect': t_co2_indirect / m_cement,
            't_co2_quarry': t_co2_quarry / m_cement,
            't_co2_crushing': t_co2_crushing / m_cement,
            't_co2_kiln': t_co2_kiln / m_cement,
            't_co2_clinker_alternative': t_co2_clinker_alternative / m_cement,
            't_co2_cement': t_co2_cement / m_cement,
            'co2_ccs': co2_ccs / m_cement,

            'co2_limestone': co2_limestone / m_cement,
            'co2_alternative': co2_alternative / m_cement,
            'co2_fossil_fuel': co2_fossil_fuel / m_cement,
            'co2_electricity': co2_electricity / m_cement,

            'opex': opex / m_cement * exchange_country('United_States')[0] / exchange_country(country)[0],
            'capex': capex_total / m_cement * exchange_country('United_States')[0] / exchange_country(country)[0],
            'cost': (opex + capex_total) / m_cement * exchange_country('United_States')[0] / exchange_country(country)[0],

            'ccs_cost_transport': ccs_cost_transport / m_cement * exchange_country('United_States')[0],
            'ccs_cost_storage': ccs_cost_storage / m_cement * exchange_country('United_States')[0],

            #'eppa': {
            #    'reference': np.array(reference) / np.array(m_cement),
            #    'electrification': np.array(electrification) / np.array(m_cement),
            #    'ng_support': np.array(ng_support) / np.array(m_cement),
            #    'resource_efficiency': np.array(resource_efficiency) / np.array(m_cement),
            #    'low_carbon_price': np.array(low_carbon_price) / np.array(m_cement),
            #    'high_carbon_price': np.array(high_carbon_price) / np.array(m_cement),
            #    'ccs_low_carbon_price': np.array(ccs_low_carbon_price) / np.array(m_cement),
            #    'ccs_high_carbon_price': np.array(ccs_high_carbon_price) / np.array(m_cement),
            #},
        }

    def figures(self, results):
        """eppa = [
            {
                'label': 'EPPA Reference',
                'data': results['eppa']['reference'],
                'style': 'dashed-line',
            },
            {
                'label': 'EPPA Electrification',
                'data': results['eppa']['electrification'],
                'style': 'dashed-line',
            },
            {
                'label': 'EPPA Natural Gas Support',
                'data': results['eppa']['ng_support'],
                'style': 'dashed-line',
            },
            {
                'label': 'EPPA Resource Efficiency',
                'data': results['eppa']['resource_efficiency'],
                'style': 'dashed-line',
            },
            {
                'label': 'EPPA Low Carbon Price',
                'data': results['eppa']['low_carbon_price'],
                'style': 'dashed-line',
            },
            {
                'label': 'EPPA High Carbon Price',
                'data': results['eppa']['high_carbon_price'],
                'style': 'dashed-line',
            },
            {
                'label': 'EPPA CCS Low Carbon Price',
                'data': results['eppa']['ccs_low_carbon_price'],
                'style': 'dashed-line',
            },
            {
                'label': 'EPPA CCS High Carbon Price',
                'data': results['eppa']['ccs_high_carbon_price'],
                'style': 'dashed-line',
            },
        ]"""

        emissions_by_stage = []

        if self.input_set.value('ccs') == 'Yes':
            emissions_by_stage += [{
                'label': 'CCS',
                'color': Color(name='yellow'),
                'data': results['co2_ccs'],
            }]

        emissions_by_stage += [
            {
                'label': 'Clinker to Cement',
                'color': Color(name='blue'),
                'data': results['t_co2_cement'],
            },
            {
                'label': 'Clinker Alternative',
                'color': Color(name='green'),
                'data': results['t_co2_clinker_alternative'],
            },
            {
                'label': 'Clinkerization',
                'color': Color(name='orange'),
                'data': results['t_co2_kiln'],
            },
            {
                'label': 'Crushing & Fuel Prep',
                'color': Color(name='black'),
                'data': results['t_co2_crushing'],
            },
            {
                'label': 'Quarry & Transport',
                'color': Color(name='gray'),
                'data': results['t_co2_quarry'],
            },
        ]

        return [
            {
                'label': 'GHG Emissions by Source',
                'unit': 'tonne CO\u2082 / tonne cement',
                'axis': 0,
                'datasets': [
                    {
                        'label': 'Limestone',
                        'color': Color(name='orange'),
                        'data': results['co2_limestone'],
                    },
                    {
                        'label': 'Alternatives',
                        'color': Color(name='blue'),
                        'data': results['co2_alternative'],
                    },
                    {
                        'label': 'Fossil fuel',
                        'color': Color(name='gray'),
                        'data': results['co2_fossil_fuel'],
                    },
                    {
                        'label': 'Electricity',
                        'color': Color(name='blueviolet'),
                        'data': results['co2_electricity'],
                    },
                ],
            },
            {
                'label': 'GHG Emissions by Stage',
                'unit': 'tonne CO\u2082 / tonne cement',
                'axis': 0,
                'datasets': emissions_by_stage,
            },


            {
                'label': 'Costs',
                'unit': 'USD $ / tonne cement',
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
                'unit': 'tonne CO\u2082 / tonne cement',
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
                'unit': 'USD $ / tonne cement',
                'axis': 1,
                'datasets': [
                    {
                        'label': 'Total Cost',
                        'data': results['cost'],
                    },
                ],
            },
        ]


    # This is for CLI usage only.
    # The web front-end will re-implement similar plotting using the above results.
    def plot(self, results):
        # print(f"results: {results}")
        if self.ccs == 'Yes':
            # plot CO2 emission trajectory.  tonne co2/tonne cement

            plot1 = plt.figure(1)
            z1 = np.array(results['t_co2_quarry']) # limestone extraction & transportation
            z2 = z1 + np.array(results['t_co2_crushing']) #limestone crushing & fuel preparation
            z3 = z2 + np.array(results['t_co2_kiln']) # clinkerization & limestone drying out
            z4 = z3 + np.array(results['t_co2_clinker_alternative']) # clinker alternatives
            z5 = z4 + np.array(results['t_co2_cement']) # clinker grinding & packing
            z6 = z5 + np.array(results['co2_ccs']) # CO2 emission due to ccs utility utilization

            # print(f'z values:{z1},{z2},{z3},{z4},{z5},{z6}')
            width = 2.75
            plt.bar(years, z6-z5, width, bottom=z5, label=f'CCS', color='turquoise', alpha=0.5)
            plt.bar(years, z5-z4, width, bottom=z4, label=f'Clinker to Cement', color='olive', alpha=0.5) #marker='s',
            plt.bar(years, z4-z3, width, bottom=z3, label=f'Clinker Alternative', color='purple', alpha=0.5)  # marker='s',
            plt.bar(years, z3-z2, width, bottom=z2, label='Clinkerization', color='lightcoral', alpha=0.5)  # marker='d',
            plt.bar(years, z2-z1, width, bottom=z1, label='Crushing+Fuel Prepare', color='blue', alpha=0.5)  # marker='x',
            plt.bar(years, z1, width, label=f'Quarry+Transportation', color='gray', alpha=0.5)  # marker='*',
            plt.scatter(years, np.array(results['t_co2']), marker='o', label=f'Total', color='red') #z4=np.array(t_co2_ccs)/1000
            plt.scatter(years, np.array(results['t_co2_direct']), marker='*', label='Direct CO\u2082 emission', color='purple')
            plt.scatter(years, np.array(results['t_co2_indirect']), marker=5, label='Indirect CO\u2082 emission', color='mediumslateblue')

            #scenarios from EPPA tonne co2/tonne cement
            """plt.plot(years, np.array(reference)/np.array(results['m_cement']), marker='o', linestyle='dashed', label='EPPA Reference',
             color='royalblue', alpha=0.5)
            plt.plot(years, np.array(electrification)/np.array(results['m_cement']), marker='o', linestyle='dashed',
                    label='EPPA Electrification', color='darkorange', alpha=0.5)
            plt.plot(years, np.array(ng_support)/np.array(results['m_cement']), marker='o', linestyle='dashed',
                    label='EPPA Natural Gas Support', color='darkgray', alpha=0.5)
            plt.plot(years, np.array(resource_efficiency)/np.array(results['m_cement']), marker='o', linestyle='dashed',
                    label='EPPA Resource Efficiency', color='khaki', alpha=0.5)
            plt.plot(years, np.array(low_carbon_price)/np.array(results['m_cement']), marker='o', linestyle='dashed',
                    label='EPPA Low Carbon Price', color='cornflowerblue', alpha=0.5)
            plt.plot(years, np.array(high_carbon_price)/np.array(results['m_cement']), marker='o', linestyle='dashed',
                    label='EPPA High Carbon Price', color='green', alpha=0.5)
            plt.plot(years, np.array(ccs_low_carbon_price)/np.array(results['m_cement']), marker='o', linestyle='dashed',
                    label='EPPA CCS and Low Carbon Price', color='mediumblue', alpha=0.5)
            plt.plot(years, np.array(ccs_high_carbon_price)/np.array(results['m_cement']), marker='o', linestyle='dashed',
                    label='EPPA CCS amd High Carbon Price', color='brown', alpha=0.5)
            """

            #plt.vlines(2020, 0, 800, label='Past/future', color='black', linestyles='dashed')  # plot vertical lines
            plt.xticks(np.arange(min(years), max(years) + 1, 5))
            #plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))  # use scientific tick-label for y axis.
            plt.title(f'CO\u2082 emission for {self.cement_type} with {self.ccs_solvent.upper()}_Based CCS:{self.ccs_heating_source}_RU')
            plt.xlabel('Year')
            plt.ylabel('tonne CO\u2082/tonne cement')
            #plt.ylim([0, 1000])  # make sure each route has the same y axis length and interval
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), fancybox=True, shadow=True,
                    ncol=2)  # .get_frame().set_alpha(0.5) #shadow=True, fancybox=True,ncol=2,, mode='expand'
            plt.subplots_adjust(bottom=0.5)

            # print(f"capex: {results['capex']},Opex:{results['opex']}")

            # CAPEX, OPEX plots. million Rupee
            fig, ax = plt.subplots()
            ax.scatter(years, np.array(results['opex']), marker='*', label='OPEX', color='red', alpha=0.5)
            ax.set_ylabel(f"OPEX (USD $/tonne cement)", color='red')
            ax.set_xlabel('Year')
            ax.legend(loc=1, bbox_to_anchor=(0.45, -0.17))  # .get_frame().set_alpha(0.5) #shadow=True, fancybox=True,ncol=2,, mode='expand'
            plt.subplots_adjust(bottom=0.26)
            ax2 = ax.twinx()
            #ax2.plot(years, np.array(cost2_ccs)/np.array(results['m_cement']), marker='d', label=f'CAPEX_CCS_{solvent.upper()}_{regeneration_u.upper()}',
            #         color='cornflowerblue')  # additional capex with ccs
            #ax2.plot(years, np.array(t_capex_add_ccs), marker='^', label='Additional CAPEX',
            #         color='slateblue')  # additional capex with ccs
            ax2.scatter(years, np.array(results['capex']), marker='o', label='CAPEX', color='navy', alpha=0.5)
            ax2.set_ylabel(f"CAPEX (USD $/tonne cement)", color='navy')
            plt.xticks(np.arange(min(years), max(years) + 1, 5))
            #ax2.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))  # use scientific tick-label for y axis.
            plt.title(f'{self.cement_type} OPEX/CAPEX with {self.ccs_solvent.upper()}_based CCS:{self.ccs_heating_source}_RU')
            ax2.legend(loc=2, bbox_to_anchor=(0.45, -0.17))  # .get_frame().set_alpha(0.5) #shadow=True, fancybox=True,ncol=2,, mode='expand'
            plt.subplots_adjust(bottom=0.26)
            #ax.set_ylim([0, 3900])  # make sure each route has the same y axis length and interval
            #ax2.set_ylim([0, 30000])
            plt.show()

        else:
            #plot CO2 emission trajectory million tonne co2
            plot1 = plt.figure(1)
            y1 = np.array(results['t_co2_quarry']) # Limestone extraction & transportaion
            y2 = y1 + np.array(results['t_co2_crushing']) # limestrone crushing and fuel preparation
            y3 = y2 + np.array(results['t_co2_kiln']) # clinkerization & limestone drying
            y4 = y3 + np.array(results['t_co2_clinker_alternative']) # clinker alternatives
            y5 = y4 + np.array(results['t_co2_cement']) # clinker grinding & cement packing
            # print(f'y values:{y1},{y2},{y3},{y4},{y5}')

            width = 2.75
            plt.scatter(years, y5, marker='o', label='Total', color='red')
            plt.scatter(years, np.array(results['t_co2_direct']), marker='*', label='Direct CO\u2082 emission', color='purple')
            plt.scatter(years, np.array(results['t_co2_indirect']), marker=5, label='Indirect CO\u2082 emission', color='mediumslateblue')
            plt.bar(years, y5-y4, width, bottom = y4, label=f'Clinker to Cement', color='olive', alpha=0.5)
            plt.bar(years, y4-y3, width, bottom=y3, label=f'Clinker Alternative', color='purple', alpha=0.5)
            plt.bar(years, y3-y2, width, bottom=y2, label='Clinkerization', color='lightcoral', alpha=0.5)
            plt.bar(years, y2-y1, width, bottom=y1, label='Crushing+Fuel Prepare', color='blue', alpha=0.5)
            plt.bar(years, y1, width, label=f'Quarry+Transportation', color='gray', alpha=0.5)

            # scenarios from EPPA million tonne co2
            """plt.plot(years, np.array(reference)/np.array(results['m_cement']), marker='o', linestyle='dashed', label='EPPA Reference',
             color='royalblue', alpha=0.5)
            plt.plot(years, np.array(electrification)/np.array(results['m_cement']), marker='o', linestyle='dashed',
                    label='EPPA Electrification', color='darkorange', alpha=0.5)
            plt.plot(years, np.array(ng_support)/np.array(results['m_cement']), marker='o', linestyle='dashed',
                    label='EPPA Natural Gas Support', color='darkgray', alpha=0.5)
            plt.plot(years, np.array(resource_efficiency)/np.array(results['m_cement']), marker='o', linestyle='dashed',
                    label='EPPA Resource Efficiency', color='khaki', alpha=0.5)
            plt.plot(years, np.array(low_carbon_price)/np.array(results['m_cement']), marker='o', linestyle='dashed',
                    label='EPPA Low Carbon Price', color='cornflowerblue', alpha=0.5)
            plt.plot(years, np.array(high_carbon_price)/np.array(results['m_cement']), marker='o', linestyle='dashed',
                    label='EPPA High Carbon Price', color='green', alpha=0.5)
            plt.plot(years, np.array(ccs_low_carbon_price)/np.array(results['m_cement']), marker='o', linestyle='dashed',
                    label='EPPA CCS and Low Carbon Price', color='mediumblue', alpha=0.5)
            plt.plot(years, np.array(ccs_high_carbon_price)/np.array(results['m_cement']), marker='o', linestyle='dashed',
                    label='EPPA CCS amd High Carbon Price', color='brown', alpha=0.5)"""

            #plt.vlines(2020, 0, 800, label='Past/future', color='black', linestyles='dashed')  # plot vertical lines
            plt.xticks(np.arange(min(years), max(years) + 1, 5))
            #plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))  # use scientific tick-label for y axis.
            plt.title(f'CO\u2082 emission for {self.cement_type} w/o CCS')
            #plt.title('IEA prediction vs. EPPA prediction')
            plt.xlabel('Year')
            plt.ylabel('tonne CO\u2082/tonne cement')
            #plt.ylim([0, 1000])  # make sure each route has the same y axis length and interval
            plt.legend(loc='upper center', bbox_to_anchor=(0.5,-0.2),fancybox=True,shadow =True, ncol=2) #.get_frame().set_alpha(0.5) #shadow=True, fancybox=True,ncol=2,, mode='expand'
            plt.subplots_adjust(bottom=0.5)

            # print(f"capex: {results['capex']},Opex:{results['opex']}")

            #CAPEX, OPEX plots  rupee/tonne cement
            fig, ax = plt.subplots()
            ax.scatter(years,np.array(results['opex']),marker='*',label='OPEX', color = 'red', alpha=0.5)
            ax.set_ylabel(f"OPEX (USD $/tonne cement)", color='red')
            ax.set_xlabel('Year')
            ax.legend(loc=1, bbox_to_anchor=(0.45, -0.17))  # .get_frame().set_alpha(0.5) #shadow=True, fancybox=True,ncol=2,, mode='expand'
            plt.subplots_adjust(bottom=0.26)
            ax2 = ax.twinx()
            #ax2.plot(years,np.array(capex_add),marker='^',label='Additional CAPEX', color = 'slateblue')
            ax2.scatter(years, np.array(results['capex']),marker='o',label='CAPEX', color = 'navy', alpha=0.5)
            ax2.set_ylabel(f"CAPEX (USD $/tonne cement)", color='navy')
            plt.xticks(np.arange(min(years), max(years) + 1, 5))
            #ax2.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))  # use scientific tick-label for y axis.
            plt.title(f'OPEX/CAPEX for {self.cement_type} w/o CCS')
            #ax.set_ylim([0, 3900])  # make sure each route has the same y axis length and interval
            #ax2.set_ylim([0, 30000])
            ax2.legend(loc=2, bbox_to_anchor=(0.45, -0.17))  # .get_frame().set_alpha(0.5) #shadow=True, fancybox=True,ncol=2,, mode='expand'
            plt.subplots_adjust(bottom=0.26)
            plt.show()

            """ContinuousInput(
                                'clinker_opc', 'Fraction of clinker (0.9-0.95)',
                                defaults=[Default(0.95)],
                                validators=[validators.numeric(), validators.gte(0.9), validators.lte(0.95)],
                                conditionals=[conditionals.input_equal_to('cement_type', 'Ordinary Portland Cement (OPC)')],
                            ),

                            ContinuousInput(
                            'clinker_ppc', 'Fraction of clinker (0.6-0.8)',
                            defaults=[Default(0.7)],
                            validators=[validators.numeric(), validators.gte(0.6), validators.lte(0.8)],
                            conditionals=[conditionals.input_equal_to('cement_type', 'Portland Pozzolana Cement (PPC)')],
                            ),
                            ContinuousInput(
                                'clinker_psc', 'Fraction of clinker (0.35-0.70)',
                                defaults=[Default(0.45)],
                                validators=[validators.numeric(), validators.gte(0.35), validators.lte(0.7)],
                                conditionals=[conditionals.input_equal_to('cement_type', 'Portland Slag Cement (PSC)')],
                            ),
                            ContinuousInput(
                                'fly_ash', 'Fraction of fly ash (0.15-0.35)',
                                defaults=[Default(0.25)],
                                validators=[validators.numeric(), validators.gte(0.15), validators.lte(0.35)],
                                conditionals=[conditionals.input_equal_to('cement_type', 'Portland Pozzolana Cement (PPC)')],
                            ),"""
