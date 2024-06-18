"""
Created on March 3, 2022
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
from analysis.system.industry.cement.cement import Cement

PATH = os.getcwd() + '/analysis/system/industrial_fleet/'
#Data Files for Cement Projections (TBA)
eppa_table_demand = pd.read_csv(PATH + 'EPPA Projections Cement.csv')  #EPPA Hard to Abate Report : https://globalchange.mit.edu/sites/default/files/MITJPSPGC_Rpt355.pdf
eppa_co2_table = pd.read_csv(PATH + 'EPPA_CO2_Projections.csv')

#set values
pathways = ['Ordinary Portland Cement (OPC)','Portland Pozzolana Cement (PPC)','Portland Slag Cement (PSC)','OPC CCS','PPC CCS','PSC CCS','Other']
# init_demand = [24,29,28,0,0,0,19] #https://images.assettype.com/bloombergquint/2021-09/4d7c93fa-1531-426d-a004-61aae5c2ad3b/Systematix_Indian_Cement_Industry_Update.pdf
init_demand = [ 70, 18, 10, 0, 0, 0, 2] #https://www.ibef.org/download/Cement.pdf (2003 values)
demand = dict(zip(pathways,init_demand))


class CementProjection(InputSource):

    @classmethod
    def user_inputs(cls):
        scen_options = []
        for val in list(eppa_table_demand.columns[1:8]):
            scen_options.append(Option(
                val,
                conditionals=[conditionals.input_equal_to('proj', 'EPPA')],
            ))

        return [
            OptionsInput(
                'proj', 'Demand Projection Source',
                options=['EPPA','User'],
                defaults=[Default('User')]
            ),
            ContinuousInput(
                'user_start','Initial Cement Production (Mt)',
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
                defaults=[Default('Reference')],
                conditionals=[conditionals.input_not_equal_to('proj','User')]
            ),
            InputGroup('prod_shares', 'Production Shares', children=[
                OptionsInput( #should be inside input group?
                    'prod_share_opt', 'Production Shares Source',
                    options=['User'],
                    defaults=[Default('User')]
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
                                        Default(demand[p]),
                                    ],
                                    # validators=[validators.numeric(), validators.gte(0), validators.lte(100)]
                                ),
                                ShareTableInput.Cell(
                                    defaults=[Default(demand[p])],
                                    # validators=[validators.numeric(), validators.gte(0), validators.lte(100)]
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
        # #CREATE DEMAND DICT
        years = [int(i*5+2020) for i in range(0,7)]
        # years = [int(item) for item in d_table['Year']]
        if self.proj != 'User':
            demand_dict = {'EPPA': eppa_table_demand}
            # #GET DATA
            d_table = demand_dict[self.proj]
            if self.proj == 'TERI':
                d_table.set_index('TERI Projections for Future Demand\nof Crude Steel')
                # print(d_table)
            c_demand = list(d_table[self.scen]) #steel demand values
            # print(s_demand)
        else:
            c_demand = []
            d_2020 = self.user_start
            perc_change = self.perc_change
            # print(perc_change)
            perc_i = perc_change/(2050-2020)
            for i in years:
                idx = years.index(i)*5
                cur_d = (perc_i*(idx)/100 + 1)*d_2020
                c_demand.append(cur_d)

        #check for nan
        c_demand = [c for c in c_demand if math.isnan(c) == False]
        print(c_demand)
    #Production Pathways (Demand)
        y_mix = {} #dict of p_mix for specific years
        y_perc_mix = {}

        if self.prod_share_opt == 'User':
            # p_df = perc_table.iloc[:, :8]
            prod_shares =self.prod_shares
            # prod_shares = json.loads(self.prod_shares)
           #Linear Projection for User Input
            y1 = years[0]
            y2 = years[-1]
            for y in years:
                total_demand = c_demand[years.index(y)]
                p_mix = {}  #dictionary of production mix
                perc_mix = {}
                for i, pathway in enumerate(pathways):
                    if pathway != 'Other':
                        p_2020 = demand[pathway]
                        p_2050 = self.prod_shares['2050'][i]
                        # p_2050 = prod_shares[i]
                        slope = (p_2050-p_2020)/(y2-y1)
                        perc = (p_2020 + slope*(y-y1))/100
                        p_mix[pathway] = perc*total_demand
                        perc_mix[pathway] = perc
                    else: #other category ( white cement etc. picksup the slack)
                        # print(sum(perc_mix.values()))
                        perc = 1 - sum(perc_mix.values())
                        # print(perc)
                        p_mix[pathway] = perc * total_demand
                        perc_mix[pathway] = perc
                y_mix[y] = p_mix

        # else: #IEA Projections
        #     for y in years:
        #         p_df = perc_table.iloc[:,:8] #IEA table of year & production percentages
        #         # print(s_demand)
        #         total_demand = s_demand[years.index(y)]
        #         p_mix = {}  # dictionary of production mix
        #         if y == 2020:
        #             y2 = 2019 #set to 2019 for IEA estimation
        #             for i in pathways:
        #                 perc = float(p_df.loc[ p_df['Year'] == y2, i]) #get percent of production
        #                 p_mix[i] = perc * total_demand
        #
        #         else:
        #             for i in pathways:
        #                 perc = float(p_df.loc[ p_df['Year'] == y, i]) #get percent of production
        #                 p_mix[i] = perc*total_demand
        #                 # p_mix_by_yr[i].append(perc * total_demand)
        #         # print(perc)
        #         y_mix[y] = p_mix

    #CO2 Calcs
        #for each year multiply emission from production pathway (tCo2/tsteel) times the expected
        #steel production for total CO2
        co2_t = []
        co2_bd ={}
        for y in y_mix.keys():
            co2_y = 0
            co2_mix ={}
            for i in pathways:

                model = Cement()
                input_set = InputSet.build_default(Cement)
                # print(i)
                if 'OPC' in i:
                    input_set.set_value('cement_type','Ordinary Portland Cement (OPC)')
                    # print('testopc')
                if 'PPC' in i:
                    input_set.set_value('cement_type', 'Portland Pozzolana Cement (PPC)')
                    # print('testppc')
                if 'PSC' in i:
                    input_set.set_value('cement_type', 'Portland Slag Cement (PSC)')
                    # print('testport')
                if 'CCS' in i:
                    input_set.set_value('ccs', 'Yes')
                    # print('ccstest')
                if 'Other' in i:
                    #PSC for other calcs
                    # print('othertest')
                    input_set.set_value('cement_type', 'Portland Slag Cement (PSC)')
                model.prepare(input_set)
                results = model.run()
                # if 'PPC' in i:
                #     # print(i)
                #     # print(np.array(results['t_co2_direct'])[0])
                #     print(np.array(results['t_co2_direct'])[0]*y_mix[y][i])
                co2_val = np.array(results['t_co2_direct'])[0]*y_mix[y][i] # only need fossil fuels emissions
                co2_y += co2_val
                co2_mix[i] = co2_val
            co2_bd[y] = co2_mix
            co2_t.append(co2_y)
        print(co2_t)

    # Cost Calc
        t_cost = []
        cost_bd = {} # yearly cost breakdown(pathway)
        for y in y_mix.keys():
            cost_y = 0
            cost_mix = {}
            for i in pathways:
                cem_prod = y_mix[y][i]
                model = Cement()
                input_set = InputSet.build_default(Cement)
                # print(i)
                if 'OPC' in i:
                    input_set.set_value('cement_type', 'Ordinary Portland Cement (OPC)')
                    # print('testopc')
                if 'PPC' in i:
                    input_set.set_value('cement_type', 'Portland Pozzolana Cement (PPC)')
                    # print('testppc')
                if 'PSC' in i:
                    input_set.set_value('cement_type', 'Portland Slag Cement (PSC)')
                    # print('testport')
                if 'CCS' in i:
                    input_set.set_value('ccs', 'Yes')
                    # print('ccstest')
                if 'Other' in i:
                    input_set.set_value('cement_type', 'Portland Slag Cement (PSC)')
                model.prepare(input_set)
                results = model.run()
                # print(np.array(results['capex'])[0] + np.array(results['opex'])[0])
                cost_val = (np.array(results['capex'])[0] + np.array(results['opex'])[0]) * cem_prod  # results['t_co2'][0]*y_mix[y][i]
                cost_y += cost_val
                cost_mix[i] = cost_val
                # if 'PSC' in i and 'CCS' in i:
                #     print(i)
                #     print(np.array(results['cost'])[0])
                #     print(cem_prod)
            cost_bd[y] = cost_mix
            t_cost.append(cost_y)
        # t_cost = [i * 10 ** -3 for i in t_cost]
        #sort data by pathway
        c_mix_by_yr = {}
        for p in pathways:
            c_mix_by_yr[p] = []
            for y in years:
                c_mix_by_yr[p].append(cost_bd[y][p])
        # print(c_mix_by_yr)
        # print(t_cost)
    #
    #     # print(y_mix[2030])
    #     # print(y_mix[2050])
    #     # Allowable CO2 upper bound according to IEA SDS
    #     # ub_demand = [i * 10 ** 6 for i in s_demand[0:5]]
    #     # ub = co2_ub(ub_demand)
    #     ub = [218.7, 304.2, 355.5, 372.5, 373.8, 338.2, 307.9]  # From webplot digitizer of Figure 3.6 in Roadmap Report
    #
    #     #Relative Emissions
    #     rel_co2_t = [i / co2_t[0] for i in co2_t]
    #
    #     # allowable CO2 upper bound
    #     rel_ub = [i / ub[0] for i in ub]
    #     print(y_mix)
        # sort data by pathway

        #production
        p_mix_by_yr = {}
        for p in pathways:
            p_mix_by_yr[p] = []
            for y in years:
                p_mix_by_yr[p].append(y_mix[y][p])

        #direct co2 emissions
        em_mix_by_yr = {}
        for p in pathways:
            em_mix_by_yr[p] = []
            for y in years:
                em_mix_by_yr[p].append(co2_bd[y][p])
        print(em_mix_by_yr)


        results = {
            'years':years,
            'c_demand': c_demand,
            'y_mix':y_mix,
            'pathways': pathways,
            'co2_t':co2_t,
            'em_mix_by_yr': em_mix_by_yr,
            'p_mix_by_yr':p_mix_by_yr,
            'c_mix_by_yr': c_mix_by_yr,
            't_cost':t_cost,
            'cost_bd': cost_bd,
            'eppa_co2_proj': None,
        }
        # print(p_mix_by_yr)
        return results

    def figures(self, results):
        y_mix = results['y_mix']
        c_demand = results['c_demand']
        years = results['years']
        pathways = results['pathways']
        t_cost = results['t_cost']

        prod_by_type = []
        co2_by_type = []
        cost_p = [] # cost by tech
        colors = ['black','orange','grey','yellow','indigo_dark','green','indigo_light']

        for p in pathways:
            prod_by_type +=[{
                'label':p,
                'color':colors[pathways.index(p)],
                'data':results['p_mix_by_yr'][p]
            }]

            co2_by_type += [{
            'label': p,
            'color': colors[pathways.index(p)],
            'data': results['em_mix_by_yr'][p]
            }]

            cost_p += [{
                'label': p,
                'color': colors[pathways.index(p)],
                'data': np.array(results['c_mix_by_yr'][p]), # convert millions to billions
            }]

        figs = [
            {
                'label': 'Cement Production by Type',
                'unit': 'Megatonne (Mt) steel',
                'axis': 0,
                'datasets': prod_by_type,
            },
            {
                'label': 'Total Cement Production ',
                'unit': 'Megatonne (Mt) steel',
                'axis': 1,
                'datasets': [
                    {
                        'label': 'Total Cement Production',
                        'data': c_demand,
                    },
                ],
            },
            {
                'label': 'Direct CO\u2082  Emissions from Cement Production',
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
                'label': 'Direct CO\u2082  Emissions from Cement Production',
                'unit': 'Megatonne (Mt) CO\u2082',
                'axis': 0,
                'datasets':co2_by_type
            },
            {
                'label': 'Total Cost of Fleet',
                'unit': 'Cost (USD)',
                'axis': 1,
                'datasets': [
                    {
                        'data': t_cost,
                    },
                ],
            },
            {
                'label': 'Cost of Fleet by Technology',
                'unit': 'Cost (USD)',
                'axis': 0,
                'datasets': cost_p,
            }
        ]
        if self.proj =='EPPA':
            eppa_co2_table = pd.read_csv(PATH + 'EPPA_CO2_Projections.csv')
            results['eppa_co2_proj'] = eppa_co2_table[[self.scen]]
            eppa_em = [{
                'label': 'Direct CO\u2082  Emissions: EPPA Projection',
                'unit': 'Megatonne (Mt) CO\u2082',
                'axis': 1,
                'datasets': [
                    {
                        'label': 'Direct CO\u2082  Emissions: EPPA Projection',
                        'data': results['eppa_co2_proj'],
                    }
                ],
            },]
        else:
            eppa_em = []

        return figs + eppa_em

    def plot(self,results):

        #UNPACK RESULTS
        years = results['years']
        proj = self.proj
        scen = self.scen
        c_demand = results['c_demand']
        y_mix = results['y_mix']
        co2_t = results['co2_t']

        pathways = results['pathways']
        #PLOT

        #CEMENT DEMAND
        plt.plot(years,c_demand,label='Total')
        plt.title(f" {proj}:Indian Cement Demand")
        years = y_mix.keys() # get the years
        years = [int(y) for y in years]
        # print(y_mix)
        all_d = []
        for p in pathways:
            demand = []
            for y in years:
                y_d = y_mix[y][p] #yearly demand
                demand.append(y_d)
            all_d.append(demand)
        plt.stackplot(years,all_d,labels=pathways)
        plt.ylabel('Cement Demand (Mt)')
        plt.xlabel('Year')
        plt.legend(loc = 'upper left')
        plt.show()

        #CO2
        plt.title(f" {proj}: {scen} Indian Cement $CO_{2}$ Direct Emissions ")
        plt.plot(years, co2_t,label='Model Inputs w/ IEA Distribution')
        plt.ylabel('$CO_{2}$ Emissions (Mt)')
        plt.xlabel('Year')
        plt.ylim(ymin=0)

        if self.proj =='EPPA':
            eppa_co2_table = pd.read_csv(PATH + 'EPPA_CO2_Projections.csv')
            eppa_co2_table = eppa_co2_table[[scen]]#[['Reference','Resource Efficiency','LCP w/ CCS','HCP w/ CCS']]
            plt.plot(years,eppa_co2_table,label=f" {proj}: {scen} ")
            # plt.title('EPPA Iron and Steel - LCP w/ CCS' + '$CO_{2}$' + ' Emissions from Combustion')
            plt.legend(loc='upper left')
        plt.show()



        return
