"""
Created on January 14, 2022
@author: sydney johnson
"""

import json
import os
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from core.common import InputSource
import core.conditionals as conditionals
from core.inputs import OptionsInput, ContinuousInput, PercentInput, Default, InputSet,InputGroup,ShareTableInput,Option
import core.validators as validators
from analysis.system.industry.iron_steel.bf_bof import BFBOF
from analysis.system.industry.iron_steel.corex_bof import COREXBOF
from analysis.system.industry.iron_steel.hisarna_bof import HisarnaBOF
from analysis.system.industry.iron_steel.h_dri_eaf import HDRIEAF
from analysis.system.industry.iron_steel.eaf import EAF
from analysis.system.industry.iron_steel.india_iron_steel_co2emission_prediction import co2_ub
from analysis.system.industry.iron_steel.ng_dri_eaf import NG_DRI_EAF
from analysis.system.industry.iron_steel.coal_dri import Coal_DRI

PATH = os.getcwd() + '/analysis/system/industrial_fleet/'
#READ DATA FILES FOR EPPA, IEA, & TERI
eppa_table_demand = pd.read_csv(PATH + 'EPPA Projections.csv')  #EPPA Hard to Abate Report : https://globalchange.mit.edu/sites/default/files/MITJPSPGC_Rpt355.pdf
iea_table = pd.read_csv(PATH + 'iea_steel_production.csv') #https://www.iea.org/data-and-statistics/charts/production-of-iron-by-route-in-india-in-the-sustainable-development-scenario
teri_table = pd.read_csv(PATH + 'teri_steel_demand.csv',index_col='TERI Projections')#  TERI analysis based on data from WSA (2018b); World Bank (2017): https://shaktifoundation.in/wp-content/uploads/2020/01/Towards-a-Low-Carbon-Steel-Sector-Report.pdf
perc_table = pd.read_csv(PATH + 'iea_steel_pathway_perc.csv')# IEA Percentage of each pathway https://www.iea.org/data-and-statistics/charts/production-of-iron-by-route-in-india-in-the-sustainable-development-scenario
eppa_co2_table = pd.read_csv(PATH + 'EPPA_CO2_Projections.csv')
pathways = list(iea_table.columns[2:9]) #based on IEA production pathways
p_df = perc_table.iloc[:, :8]  # IEA table of year & production percentages
# print(eppa_table_demand)

class SteelProjection(InputSource):

    @classmethod
    def user_inputs(cls):
        scen_options = []
        for val in list(eppa_table_demand.columns[1:8]):
            scen_options.append(Option(
                val,
                conditionals=[conditionals.input_equal_to('proj', 'EPPA')],
            ))
        for val in list(teri_table.index):
            scen_options.append(Option(
                val,
                conditionals=[conditionals.input_equal_to('proj', 'TERI')],
            ))

        return [
            OptionsInput(
                'proj', 'Demand Projection Source',
                options=['EPPA','TERI', 'User'],
                defaults=[Default('EPPA')]
            ),
            ContinuousInput(
                'user_start','Initial Steel Production (Mt)',
                defaults=[Default(100)],
                validators=[validators.numeric(), validators.gte(0)],
                conditionals=[conditionals.input_equal_to('proj', 'User')]
            ),
            ContinuousInput(
                'perc_change', 'Percent Change in Production from 2020 to 2050',
                defaults=[Default(1)],
                validators=[validators.numeric(), validators.gte(-100),validators.lte(200)],
                unit='%',
                conditionals=[conditionals.input_equal_to('proj', 'User')]
            ),
            OptionsInput(
                'scen', 'Demand Scenario: India',
                options=scen_options,
                # defaults=[Default('User')],
                conditionals=[conditionals.input_not_equal_to('proj','User')]
            ),
            InputGroup('prod_shares', 'Production Shares', children=[
                OptionsInput( #should be inside input group?
                    'prod_share_opt', 'Production Shares Source',
                    options=['IEA SDS', 'User'],
                    defaults=[Default('IEA SDS')]
                ),
                ShareTableInput(
                    'prod_shares', 'Production Shares (%)',
                    columns=[str(2020), str(2050)],
                    rows=[
                        ShareTableInput.Row(
                            p,
                            cells=[
                                ShareTableInput.Cell(
                                    defaults=[
                                        Default(
                                            float(p_df.loc[p_df['Year'] == 2019, p])*100,
                                        ),
                                    ],
                                    # validators=[validators.numeric(), validators.gte(0), validators.lte(100)]
                                ),
                                ShareTableInput.Cell(
                                    defaults=[
                                        Default(
                                            float(p_df.loc[p_df['Year'] == 2050, p])*100,
                                            conditionals=[conditionals.input_equal_to('prod_share_opt', 'IEA SDS')],
                                        ),
                                        Default(float(p_df.loc[p_df['Year'] == 2050, p])*100,conditionals=[conditionals.input_equal_to('prod_share_opt', 'User')],
                                        ),
                                    ],
                                    # validators=[validators.numeric(), validators.gte(0), validators.lte(100)
                                    #             ]
                                ),
                            ]
                        )
                        for p in pathways
                    ],
                    on_change_actions=[
                        {
                            'type': 'set_input_to',
                            'target': 'prod_share_opt',
                            'value': 'User',
                        }
                    ],
                ),
            ]),
        ]

    def run(self):

        #CREATE DEMAND DICT
        demand_dict = {'EPPA':eppa_table_demand,'TERI':teri_table} #,IEA':iea_table
        # keys = list(demand_dict.keys())
        #GET DATA
        # d_table = demand_dict[self.proj]
        years = [int(item) for item in demand_dict['EPPA']['Year']]
        # years = [int(item) for item in d_table['Year']]

        # if the demand data is from user, calculate.
        # print(d_table)
        if self.proj != 'User':
            d_table = demand_dict[self.proj]
            # print(d_table)
            if self.proj == 'TERI':
            # d_table = d_table.set_index('TERI Projections')
                s_demand = list(d_table.loc[self.scen]) #steel demand values
            else:
                s_demand = list(d_table[self.scen])

        else:
            s_demand = []
            d_2020 = self.user_start
            perc_change = self.perc_change
            perc_i = perc_change/(2050-2020)
            for i in years:
                idx = years.index(i)*5
                cur_d = (perc_i*(idx)/100 + 1)*d_2020
                s_demand.append(cur_d)

        #check for nan/other values
        # for s in s_demand:
            # print(type(s))
            # print(type(s)== np.float)
        s_demand = [s for s in s_demand if (type(s) == np.float64 or type(s) == np.int64 or type(s) == np.float) and (math.isnan(s) ==False)]

    #Production Pathways
        y_mix = {} #dict of p_mix for specific years
        y_perc_mix = {}

        if self.prod_share_opt == 'User':
            p_df = perc_table.iloc[:, :8]
            prod_shares = self.prod_shares
           #Linear Projection for User Input
            y1 = years[0]
            y2 = years[-1]
            for y in years:
                total_demand = s_demand[years.index(y)]
                p_mix = {}  #dictionary of production mix
                perc_mix = {}
                for i, pathway in enumerate(pathways):
                    if pathway != 'Scrap_EAF':
                        p_2020 = float(p_df.loc[p_df['Year'] == 2019, pathway]) * 100
                        p_2050 = prod_shares['2050'][i]
                        # p_2050 = prod_shares[i]
                        slope = (p_2050-p_2020)/(y2-y1)
                        perc = (p_2020 + slope*(y-y1))/100
                        p_mix[pathway] = perc*total_demand
                        perc_mix[pathway] = perc
                    else: #Scrap EAF picks up slack/ensures we reach 100% for total share
                        perc = 1 - sum(perc_mix.values())
                        p_mix[pathway] = perc * total_demand
                y_mix[y] = p_mix
                # y_perc_mix[y] = perc_mix

        else: #IEA Projections

            for y in years:
                p_df = perc_table.iloc[:,:8] #IEA table of year & production percentages
                # print(s_demand)
                total_demand = s_demand[years.index(y)]

                p_mix = {}  # dictionary of production mix
                # fstein = [0.42,0,0.02,0,0.4,0,0.16] #see verification sheet in dropbox, 'Steel Fleet' tab frankenstein dataw
                if y == 2020:
                    y2 = 2019 #set to 2019 for IEA estimation
                    for i in pathways:
                        # perc = fstein[pathways.index(i)]
                        perc = float(p_df.loc[ p_df['Year'] == y2, i]) #get percent of production
                        p_mix[i] = perc * total_demand

                else:
                    for i in pathways:
                        perc = float(p_df.loc[ p_df['Year'] == y, i]) #get percent of production
                        p_mix[i] = perc*total_demand
                        # p_mix_by_yr[i].append(perc * total_demand)
                # print(perc)
                y_mix[y] = p_mix

    #CO2 Calcs
        #for each year multiply emission from production pathway (tCo2/tsteel) times the expected
        #steel production for total CO2
        co2_t = []
        p_dri_ng = 0.183 #Annual Ministry of Steel Report (2020 Provisional Production)
        p_dri_coal = 0.816 #Annual Ministry of Steel Report (2020 Provisional Production)
        for y in y_mix.keys():
            co2_y = 0
            for i in pathways:
                if 'Commercial DRI' in i:
                     #First natural gas
                    model = NG_DRI_EAF()
                    input_set = InputSet.build_default(NG_DRI_EAF)
                    model.prepare(input_set)
                    results = model.run()
                    ng_co2 = results['t_co2_fossil'][0]
                    # print(ng_co2)
                     # then coal
                    model = Coal_DRI()
                    input_set = InputSet.build_default(Coal_DRI)
                    model.prepare(input_set)
                    results = model.run()
                    coal_co2 = results['t_co2_fossil'][0]
                    # print(coal_co2)
                    #create average emission intensity, then multiply by production/demand
                    co2_val = ng_co2*p_dri_ng + coal_co2*p_dri_coal


                    # print(y_mix[y][i])
                    # print(co2_val)

                    co2_y += co2_val * y_mix[y][i]
                # elif 'EAF' in i:
                #     co2_val  = 1.85434
                #     # co2_val = 1.29
                #     co2_y += co2_val * y_mix[y][i]
                #     # input_set.set_value('f_scrap', 0.37) #India avg according to shakti foundation "Resource Efficiency Report"
                else:
                    if 'BF' in i:
                        model = BFBOF()
                        input_set = InputSet.build_default(BFBOF)
                        input_set.set_value('fuel_type', 'India-Raniganj Coal')
                        if 'CCUS' in i:
                            input_set.set_value('ccs','Yes') # provide input values for inputs w/o defaults (or override default values)
                    if 'SR' in i:
                        model = COREXBOF()
                        input_set = InputSet.build_default(COREXBOF)
                        if 'CCUS' in i:
                            input_set.set_value('ccs','Yes')
                    if 'EAF' in i:
                        model = EAF()
                        input_set = InputSet.build_default(EAF)
                        # input_set.set_value('f_scrap', 0.372) #India avg according to shakti foundation "Resource Efficiency Report"
                    if 'H2' in i:
                        model = HDRIEAF()
                        input_set = InputSet.build_default(HDRIEAF)
                    # if 'Commercial DRI' in i:  # until natural gas DRI is finished
                    #     model = NG_DRI_EAF()
                    #     input_set = InputSet.build_default(NG_DRI_EAF)
                    #     model =  Coal_DRI()
                    #     input_set = InputSet.build_default(Coal_DRI)
                    model.prepare(input_set)
                    results = model.run()
                    # if 'BF' in i:
                    #     print(results['t_co2'][0])
                    co2_val = results['t_co2_fossil'][0]*y_mix[y][i] # only need fossil fuels emissions
                    co2_y += co2_val
            co2_t.append(co2_y)
        #get
        p_mix_by_yr = {}
        for p in pathways:
            p_mix_by_yr[p] = []
            for y in years:
                p_mix_by_yr[p].append(y_mix[y][p])

    # Cost Calc
        t_cost = []
        cost_bd = {} # yearly cost breakdown(pathway)
        for y in y_mix.keys():
            cost_y = 0
            cost_mix = {}
            for p in pathways:
                steel_prod = y_mix[y][p]
                if 'Commercial DRI' in p:  # until natural gas DRI is finished
                    # First natural gas
                    model = NG_DRI_EAF()
                    input_set = InputSet.build_default(NG_DRI_EAF)
                    model.prepare(input_set)
                    results = model.run()
                    ng_cost =results['t_capex'][0] + results['opex'][0]
                    # print(ng_cost)
                    # then coal
                    model = Coal_DRI()
                    input_set = InputSet.build_default(Coal_DRI)
                    model.prepare(input_set)
                    results = model.run()
                    coal_cost = results['t_capex'][0] + results['opex'][0]
                    # print(coal_cost)
                    # create average emission intensity, then multiply by production/demand
                    cost_int = ng_cost * p_dri_ng + coal_cost * p_dri_coal
                    # print(cost_int)
                    cost_val = cost_int * steel_prod
                else:
                    if 'BF' in p:
                        model = BFBOF()
                        input_set = InputSet.build_default(BFBOF)
                        input_set.set_value('fuel_type', 'India-Raniganj Coal')
                        input_set.set_value('f_scrap',0.097)
                        if 'CCUS' in p:
                            input_set.set_value('ccs',
                                                'Yes')  # provide input values for inputs w/o defaults (or override default values)
                    if 'SR' in p:
                        model = COREXBOF()
                        input_set = InputSet.build_default(COREXBOF)
                        if 'CCUS' in p:
                            input_set.set_value('ccs', 'Yes')
                    if 'EAF' in p:
                        model = EAF()
                        input_set = InputSet.build_default(EAF)
                        # input_set.set_value('f_scrap',
                        #                     0.99)  # now removed - 0.372 = India avg according to shakti foundation "Resource Efficiency Report"
                    if 'H2' in p:
                        model = HDRIEAF()
                        input_set = InputSet.build_default(HDRIEAF)
                    model.prepare(input_set)
                    results = model.run()
                    # print(results['t_capex'][0] + results['opex'][0])
                    cost_val = (results['t_capex'][0] + results['opex'][0]) * y_mix[y][p]  # results['t_co2'][0]*y_mix[y][i]
                cost_y += cost_val
                cost_mix[p] = cost_val
            cost_bd[y] = cost_mix
            t_cost.append(cost_y)
        t_cost = [i * 10 ** -3 for i in t_cost]
        #sort data by pathway
        c_mix_by_yr = {}
        for p in pathways:
            c_mix_by_yr[p] = []
            for y in years:
                c_mix_by_yr[p].append(cost_bd[y][p])

        # print(y_mix[2030])
        # print(y_mix[2050])
        # Allowable CO2 upper bound according to IEA SDS
        # ub_demand = [i * 10 ** 6 for i in s_demand[0:5]]
        # ub = co2_ub(ub_demand)
        ub = [218.7, 304.2, 355.5, 372.5, 373.8, 338.2, 307.9]  # From webplot digitizer of Figure 3.6 in Roadmap Report

        # #Relative Emissions
        # rel_co2_t = [i / co2_t[0] for i in co2_t]
        #
        # # allowable CO2 upper bound
        # rel_ub = [i / ub[0] for i in ub]

        results = {
            'years':years,
            's_demand': s_demand,
            'y_mix':y_mix,
            'pathways': pathways,
            'co2_t':co2_t,
            'c_mix_by_yr': c_mix_by_yr,
            'p_mix_by_yr':p_mix_by_yr,
            'eppa_co2_proj':None,
            'rel_eppa': None,
            't_cost':t_cost,
            'cost_bd': cost_bd,
        }
        return results

    def figures(self, results):
        y_mix = results['y_mix']
        s_demand = results['s_demand']
        years = results['years']
        pathways = results['pathways']

        prod_by_tech = []
        cost_p = [] # cost by tech
        colors = ['black','orange','grey','yellow','indigo_dark','green','indigo_light']
        for p in pathways:
            prod_by_tech +=[{
                'label':p,
                'color':colors[pathways.index(p)],
                'data':results['p_mix_by_yr'][p]
            }]

            cost_p += [{
                'label': p,
                'color': colors[pathways.index(p)],
                'data': np.array(results['c_mix_by_yr'][p]) * 0.001, # convert millions to billions
            }]

        if self.proj =='EPPA':
            eppa_co2_table = pd.read_csv(PATH + 'EPPA_CO2_Projections.csv')
            results['eppa_co2_proj'] = eppa_co2_table[[self.scen]]
            results['rel_eppa'] = [i / eppa_co2_table[self.scen][0] for i in eppa_co2_table[self.scen]]


        t_cost = results['t_cost']
        return [
            {
                'label': 'Steel Production by Technology',
                'unit': 'Megatonne (Mt) steel',
                'axis': 0,
                'datasets': prod_by_tech,
            },
            {
                'label': 'Total Steel Production ',
                'unit': 'Megatonne (Mt) steel',
                'axis': 1,
                'datasets': [
                    {
                        'label': 'Total Steel Production',
                        'data': results['s_demand'],
                    },
                ],
            },
            {
                'label': 'Direct CO\u2082  Emissions from Steel Production',
                'unit': 'Megatonne (Mt) CO\u2082',
                'axis': 1,
                'datasets': [
                    {
                        'label': 'Direct CO\u2082  Emissions from Steel Production',
                        'data': results['co2_t'],
                    },
                ],
            },
            {
                'label': 'Direct CO\u2082  Emissions: EPPA Projection',
                'unit': 'Megatonne (Mt) CO\u2082',
                'axis': 1,
                'datasets': [
                    {
                        'label': 'Direct CO\u2082  Emissions: EPPA Projection',
                        'data': results['eppa_co2_proj'],
                    },
                ],
            },
            {
                'label': 'Total Cost of Fleet',
                'unit': 'Cost (billion USD)',
                'axis': 1,
                'datasets': [
                    {
                        'data': t_cost,
                    },
                ],
            },
            {
                'label': 'Cost of Fleet by Technology',
                'unit': 'Cost (billion USD)',
                'axis': 0,
                'datasets': cost_p,
            }
        ]

    def plot(self,results):

        #UNPACK RESULTS
        years = results['years']
        proj = self.proj
        scen = self.scen
        s_demand = results['s_demand']
        y_mix = results['y_mix']
        co2_t = results['co2_t']
        pathways = results['pathways']
        #PLOT

        #STEEL DEMAND
        plt.plot(years,s_demand,label='Total')
        plt.title(f" {proj}: {scen} Indian Steel Demand")
        years = y_mix.keys() # get the years
        years = [int(y) for y in years]
        all_d = []
        for p in pathways:
            demand = []
            for y in years:
                y_d = y_mix[y][p] #yearly demand
                demand.append(y_d)
            all_d.append(demand)
        plt.stackplot(years,all_d,labels=pathways)
        plt.ylabel('Steel Demand (Mt)')
        plt.xlabel('Year')
        plt.legend(loc = 'upper left')
        plt.show()

        #CO2
        plt.title(f" {proj}: {scen} Indian Steel $CO_{2}$ Direct Emissions ")
        plt.plot(years, co2_t,label='Model Inputs w/ IEA Distribution')
        plt.ylabel('$CO_{2}$ Emissions (Mt)')
        plt.xlabel('Year')
        plt.ylim(ymin=0)
        # print(co2_t)
        if self.proj =='EPPA':
            eppa_co2_table = pd.read_csv(PATH + 'EPPA_CO2_Projections.csv')
            eppa_co2_table = eppa_co2_table[[scen]]#[['Reference','Resource Efficiency','LCP w/ CCS','HCP w/ CCS']]
            plt.plot(years,eppa_co2_table,label=f" {proj}: {scen} ")
            # plt.title('EPPA Iron and Steel - LCP w/ CCS' + '$CO_{2}$' + ' Emissions from Combustion')
            plt.legend(loc='upper left')
        plt.show()

        #Relative CO2 Emissions
        # Relative estimation
        # CO2
        plt.title(f" {proj}: {scen} Indian Steel $CO_{2}$ Relative Direct Emissions ")
        rel_co2_t = [i / co2_t[0] for i in co2_t]
        # iea = [103.62178051860904, 126.95702559605894, 168.95863832127912, 194.6894496852311, 219.42816253279696,
        #        239.14847598571487, 253.68155719257464]
        # rel_iea = [i / iea[0] for i in iea]
        # plt.plot(years, rel_iea, label='Model Inputs w/ IEA Distribution', color='tab:blue')
        plt.plot(years, rel_co2_t, label='Model Inputs w/ EPPA Distribution', color='red')
        plt.ylabel('$CO_{2}$ Emissions relative to 2020')
        plt.xlabel('Year')
        plt.ylim(ymin=0)


        return
