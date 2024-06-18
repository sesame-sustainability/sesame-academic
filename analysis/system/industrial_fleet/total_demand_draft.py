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
from core.inputs import OptionsInput, ContinuousInput, PercentInput, Default, InputSet
import core.validators as validators
from analysis.system.industry.iron_steel.bf_bof import BFBOF
from analysis.system.industry.iron_steel.corex import COREX
from analysis.system.industry.iron_steel.hisarna_bof import HisarnaBOF
from analysis.system.industry.iron_steel.h_dri_eaf import HDRIEAF
from analysis.system.industry.iron_steel.eaf import EAF
from analysis.system.industry.iron_steel.india_iron_steel_co2emission_prediction import co2_ub

PATH = os.getcwd() + '/analysis/system/industrial_fleet/'
#READ DATA FILES FOR EPPA & TERI
eppa_table_demand = pd.read_csv(PATH + 'EPPA Projections.csv')  #EPPA Hard to Abate Report : https://globalchange.mit.edu/sites/default/files/MITJPSPGC_Rpt355.pdf
iea_table = pd.read_csv(PATH + 'iea_steel_production.csv') #https://www.iea.org/data-and-statistics/charts/production-of-iron-by-route-in-india-in-the-sustainable-development-scenario
teri_table = pd.read_csv(PATH + 'teri_steel_demand.csv')#  TERI analysis based on data from WSA (2018b); World Bank (2017): https://shaktifoundation.in/wp-content/uploads/2020/01/Towards-a-Low-Carbon-Steel-Sector-Report.pdf
perc_table = pd.read_csv(PATH + 'iea_steel_pathway_perc.csv')# IEA Percentage of each pathway https://www.iea.org/data-and-statistics/charts/production-of-iron-by-route-in-india-in-the-sustainable-development-scenario
eppa_co2_table = pd.read_csv(PATH + 'EPPA_CO2_Projections.csv')


def user_inputs():

    #CREATE DEMAND DICT
    demand_dict = {'EPPA':eppa_table_demand,'TERI':teri_table} #,IEA':iea_table
    keys = list(demand_dict.keys())

    #ASK USER FOR PROJECTION
    print('Demand Options:')
    for i in keys:
        print('(' + str(keys.index(i) + 1) + ')'+str(i))

    proj = keys[int(input('Which Indian crude steel demand/production scenario? : '))-1]

    #GET DATA
    d_table = demand_dict[proj]
    years = [int(item) for item in d_table['Year']]

    if proj == 'TERI':
        scenarios = list(d_table.columns[1:6])
    elif proj == 'IEA':
        scenarios = list([d_table.columns[1],d_table.columns[9]])
    else:
        scenarios = list(d_table.columns[1:8])
    for s in scenarios:
        print('(' + str(scenarios.index(s) + 1) + ')'+str(s))
    scen = scenarios[int(input('Choose Scenario:'))-1]
    s_demand = list(d_table[scen]) #steel demand values

    #check for nan
    for s in s_demand:
        if math.isnan(s):
            years.remove(years[s_demand.index(s)])
            s_demand.remove(s)

    # if choosing EPPA, can access the CO2 emission predictions
    # print(s_demand)
    return years,s_demand,d_table,proj,scen

def prod_pathway(year,s_demand,d_table):

    pathways = list(iea_table.columns[2:9]) #based on IEA production pathways
    y_mix = {} #dict of p_mix for specific years

    #ask user or default input
    print('(1) User Input')
    # if proj == 'IEA': # only option available if IEA was initially chosen
    print('(2) IEA SDS')
    print('(3) EPPA')
    p_choice = int(input('Choose source for steel production mix:'))

    if p_choice == 1:
         # years of interest
        y1 = year[0]
        y2 = year[-1]
        year_int = [y1, y2]

        #choose 2020 & 2050 production shares
        perc_2020 = [42,0,2,0,26,0,30]
        perc_2050 = [23,5,0,20,11,16,25]
        for y in year_int:
            total_demand = s_demand[years.index(y)]
            p_mix = {}
            g = 0
            for i in pathways:
                if y == 2020:
                    perc = perc_2020[g]/100
                if y ==2050:
                    perc = perc_2050[g]/100
                # perc = int(input('Choose Percent of Steel Produced via ' + i + '(0-100):')) / 100
                p_mix[i] = perc * total_demand
                g += 1
            y_mix[y] = p_mix

        #pathway slope
        p_slope = {}
        for i in pathways:
            p_slope[i] = (y_mix[y2][i]/s_demand[years.index(y2)] - y_mix[y1][i]/s_demand[years.index(y1)])/ (y2 - y1)

        #project shares for years in between
        for y in year:
            total_demand = s_demand[years.index(y)]
            p_mix = {}  # dictionary of production mix
            for i in pathways:
                perc = (y_mix[y1][i]/s_demand[years.index(y1)] + p_slope[i]*(y - y1))
                p_mix[i] = perc * total_demand
            y_mix[y] = p_mix

    elif p_choice == 2 : #IEA Projections
        year_int = year
        for y in year_int:
            p_df = perc_table.iloc[:,:8] #IEA table of year & production percentages
            total_demand = s_demand[year.index(y)]
            p_mix = {}  # dictionary of production mix
            p_mix_by_yr = dict.fromkeys(pathways,None)
            if y == 2020:
                y2 = 2019 #set to 2019 for IEA estimation
                for i in pathways:
                    perc = float(p_df.loc[ p_df['Year'] == y2, i]) #get percent of production
                    p_mix[i] = perc*total_demand
                    # p_mix_by_yr[i].append(perc * total_demand)
            else:
                for i in pathways:
                    perc = float(p_df.loc[ p_df['Year'] == y, i]) #get percent of production
                    p_mix[i] = perc*total_demand
                    # p_mix_by_yr[i].append(perc * total_demand)
            y_mix[y] = p_mix
        eppa_p_mix = 0
    else:
        eppa_p_mix = pd.read_csv(PATH + 'EPPA_tech_mix_hcp_lcp_ccs.csv', header=1)
        eppa_p_mix = eppa_p_mix.set_index('Year')
        if 'CCS' in scen:
            t_mix = eppa_p_mix.columns[0:4]
            if 'LCP' in scen:
                eppa_p_mix = eppa_p_mix[0:7]
            if 'HCP' in scen:
                eppa_p_mix = eppa_p_mix[11:18]
        for y in year:
            p_mix = {}  # dictionary of production mix
            for i in t_mix:
                p_mix[i] = float(eppa_p_mix[i][str(y)])
            y_mix[y] = p_mix
        pathways = t_mix

    if p_choice != 3:
        p_mix_by_yr = {}
        for p in pathways:
            p_mix_by_yr[p] = []
            for y in year:
                p_mix_by_yr[p].append(y_mix[y][p])
    # print(p_df)
    # print(p_mix_by_yr)
    return y_mix,pathways,p_choice,eppa_p_mix

def co2_calc(y_mix,pathways,p_choice):
    co2_t = []
    eppa_co2_t = []
    for y in years:
        co2_y = 0
        eaf_sh = 0.52
        hisarna_sh = 0.03
        if y >= 2035:
            dri_sh = 0.10
            hdri_sh = 0.35
        else:
            dri_sh = 0.45
            hdri_sh = 0
        t_sh = [eaf_sh, hisarna_sh, dri_sh, hdri_sh]
        t_mix = ['eaf','hisarna','dri','hdri']
        #USING EPPA prediction
        if p_choice == 3:
            for p in pathways:
                if 'BF-BOF' in p:
                    model = BFBOF()
                    input_set = InputSet.build_default(BFBOF)
                    input_set.set_value('fuel_type','India-Raniganj Coal')
                    if 'CCS' in p:
                        input_set.set_value('ccs','Yes')  # provide input values for inputs w/o defaults (or override default values)
                    sh = 1
                    model.prepare(input_set)
                    results = model.run()
                    if sh != dri_sh:
                        co2_val = results['t_co2_fossil'][0] * y_mix[y][p] * sh
                    co2_y = co2_y + co2_val
                if 'EAF' in p:
                    if 'CCS' not in p:
                        for i in t_mix:
                            if 'dri' in i:  # until natural gas DRI is finished
                                if 'h' in i:
                                    model = HDRIEAF()
                                    input_set = InputSet.build_default(HDRIEAF)
                                    sh = hdri_sh
                                else:
                                    coal_perc = 0.8  # https://steel.gov.in/sites/default/files/Annual%20Report-Ministry%20of%20Steel%202020-21.pdf
                                    coal_em = 1.7  # (PDF) COMPARISON OF DIFFERENT COAL BASED DIRECT REDUCTION PROCESSES (researchgate.net)
                                    ng_perc = 0.2  # https://steel.gov.in/sites/default/files/Annual%20Report-Ministry%20of%20Steel%202020-21.pdf
                                    ng_em = 1  # IEA Steel Tech Roadmap
                                    sh = dri_sh
                                    co2_val = (ng_em * ng_perc + coal_em * coal_perc)* y_mix[y][p] * sh
                            if i == 'eaf':
                                model = EAF()
                                input_set = InputSet.build_default(EAF)
                                input_set.set_value('f_scrap',0.99) #default # India avg according to shakti foundation "Resource Efficiency Report"
                                sh = eaf_sh
                            if i == 'hisarna':
                                model = HisarnaBOF()
                                input_set = InputSet.build_default(HisarnaBOF)
                                sh = hisarna_sh
                            model.prepare(input_set)
                            results = model.run()
                            if sh != dri_sh:
                                co2_val = results['t_co2_fossil'][0] * y_mix[y][p] * sh
                            co2_y = co2_y + co2_val
                    else:
                        model = HisarnaBOF()
                        input_set = InputSet.build_default(HisarnaBOF)
                        input_set.set_value('ccs', 'Yes')
                        sh = 1
                        model.prepare(input_set)
                        results = model.run()
                        if sh != dri_sh:
                            co2_val = results['t_co2_fossil'][0] * y_mix[y][p]*sh
                        co2_y = co2_y + co2_val
        else:
            for i in pathways:
                if 'Commercial DRI' in i:  # until natural gas DRI is finished
                    coal_perc = 0.8  # https://steel.gov.in/sites/default/files/Annual%20Report-Ministry%20of%20Steel%202020-21.pdf
                    coal_em = 1.7  # (PDF) COMPARISON OF DIFFERENT COAL BASED DIRECT REDUCTION PROCESSES (researchgate.net)
                    ng_perc = 0.2  # https://steel.gov.in/sites/default/files/Annual%20Report-Ministry%20of%20Steel%202020-21.pdf
                    ng_em = 1  # IEA Steel Tech Roadmap
                    co2_val = ng_em * ng_perc + coal_em * coal_perc
                    co2_y = co2_y + co2_val * y_mix[y][i]
                else:
                    if 'BF' in i:
                        model = BFBOF()
                        input_set = InputSet.build_default(BFBOF)
                        input_set.set_value('fuel_type','India-Raniganj Coal')
                        if 'CCUS' in i:
                            input_set.set_value('ccs',
                                                'Yes')  # provide input values for inputs w/o defaults (or override default values)
                    if 'SR' in i:
                        model = HisarnaBOF()
                        input_set = InputSet.build_default(HisarnaBOF)
                        if 'CCUS' in i:
                            input_set.set_value('ccs', 'Yes')
                    if 'EAF' in i:
                        model = EAF()
                        input_set = InputSet.build_default(EAF)
                        input_set.set_value('f_scrap',
                                            0.99)  # India avg according to shakti foundation "Resource Efficiency Report"
                    if 'H2' in i:
                        model = HDRIEAF()
                        input_set = InputSet.build_default(HDRIEAF)
                    model.prepare(input_set)
                    results = model.run()
                    # print(results['t_co2'][0])
                    co2_val = results['t_co2'][0] * y_mix[y][i]  # results['t_co2'][0]*y_mix[y][i]
                    co2_y = co2_y + co2_val
        co2_t.append(co2_y)

    return co2_t


def cost_calc(y_mix,pathways,p_choice):
    cost_mix = {}
    t_cost = []
    cost_bd = {}
    for y in y_mix.keys():
        cost_y = 0
        cost_mix = {}
        for p in pathways:
            steel_prod = y_mix[y][p]
            if 'Commercial DRI' in p:  # until natural gas DRI is finished
                cost_int = 400 # approximate based on Zang Presentenation ( MITEI ) for NG-DRI in USD/tcs LCOE
                cost_val = cost_int*steel_prod
            else:
                if 'BF' in p:
                    model = BFBOF()
                    input_set = InputSet.build_default(BFBOF)
                    input_set.set_value('fuel_type','India-Raniganj Coal')

                    if 'CCUS' in p:
                        input_set.set_value('ccs','Yes')  # provide input values for inputs w/o defaults (or override default values)
                if 'SR' in p:
                    model = HisarnaBOF()
                    input_set = InputSet.build_default(HisarnaBOF)
                    if 'CCUS' in p:
                        input_set.set_value('ccs', 'Yes')
                if 'EAF' in p:
                    model = EAF()
                    input_set = InputSet.build_default(EAF)
                    input_set.set_value('f_scrap',0.99)  #now removed - 0.372 = India avg according to shakti foundation "Resource Efficiency Report"
                if 'H2' in p:
                    model = HDRIEAF()
                    input_set = InputSet.build_default(HDRIEAF)
                model.prepare(input_set)
                results = model.run()
                cost_val = (results['t_capex'][0] + results['opex'][0]) * y_mix[y][p]  # results['t_co2'][0]*y_mix[y][i]
            cost_y += cost_val
            cost_mix[p] = cost_val
        cost_bd[y] = cost_mix
        t_cost.append(cost_y)
    # print(cost_bd)
    c_mix_by_yr = {}
    for p in pathways:
        c_mix_by_yr[p] = []
        for y in years:
            c_mix_by_yr[p].append(cost_bd[y][p])
    print(c_mix_by_yr)
    return t_cost,cost_bd

def plot(years,s_demand,y_mix,proj,scen,pathways,co2_t,cost,cost_bd):
    #PLOT
    #DEMAND
    plt.close('all')
    plt.plot(years,s_demand,label='Total')
    plt.title(f" {proj}: {scen} Indian Steel Demand")
    years = [int(y) for y in years]
    all_d = []
    for p in pathways:
        demand = []
        for y in years:
            y_d = y_mix[y][p] #yearly demand
            demand.append(y_d)
        all_d.append(demand)
        #plt.plot(years,demand,label = p)
    plt.stackplot(years,all_d,labels=pathways)
    plt.ylabel('Steel Demand (Mt)')
    plt.xlabel('Year')
    plt.legend(loc = 'upper left')
    plt.show()
    #
    # EPPA
    # if 'CCUS' in scen:
    #     eppa_p_mix = eppa_p_mix[1:7]
    #     t_mix = 3
    #     if 'LCP' in scen:
    #         plt.stackplot(years, all_d, labels=t_mix)
    #     if 'HCP' in scen:
    #         plt.stackplot(years, all_d, labels=pathways)
    #         plt.ylabel('Steel Demand (Mt)')
    #         plt.xlabel('Year')
    #         plt.legend(loc='upper left')
    #         plt.show()

    #CO2
    plt.title(f" {proj}: {scen} Indian Steel $CO_{2}$ Direct Emissions ")
   # plt.plot(years,[103.62178051860904, 126.95702559605894, 168.95863832127912, 194.6894496852311, 219.42816253279696, 239.14847598571487, 253.68155719257464],label='Model Inputs w/ IEA Distribution',color='tab:blue')
    plt.plot(years, co2_t,label='Model Inputs w/ User Input Distribution',color='red')
    plt.ylabel('$CO_{2}$ Emissions (Mt)')
    plt.xlabel('Year')
    plt.ylim(ymin=0,ymax=400)

    #allowable CO2 upper bound
    ub_demand = [ i*10**6 for i in s_demand[0:5]]
    ub = co2_ub(ub_demand)
    ub = [ 218.7,304.2,355.5,372.5,373.8,338.2,307.9] # From webplot digitizer of Figure 3.6 in Roadmap

    plt.plot(years,ub,label='$CO_{2}$ Upper Bound from IEA SDS',color='tab:orange')

    if proj =='EPPA':
        eppa_co2_table = pd.read_csv(PATH + 'EPPA_CO2_Projections.csv')
        eppa_co2_table = eppa_co2_table[[scen]]#[['Reference','Resource Efficiency','LCP w/ CCS','HCP w/ CCS']]
        plt.plot(years,eppa_co2_table,label=f" {proj}: {scen} ",color='green')
        # plt.title('EPPA Iron and Steel - LCP w/ CCS' + '$CO_{2}$' + ' Emissions from Combustion')
        plt.legend(loc='upper left')
    plt.show()


    #Relative estimation
    # CO2
    plt.title(f" {proj}: {scen} Indian Steel $CO_{2}$ Relative Direct Emissions ")
    rel_co2_t = [ i/co2_t[0] for i in co2_t]
    rel_co2_t = [ i/co2_t[0] for i in co2_t]
    iea = [103.62178051860904, 126.95702559605894, 168.95863832127912, 194.6894496852311, 219.42816253279696,
                     239.14847598571487, 253.68155719257464]
    rel_iea = [i/iea[0] for i in iea]
    plt.plot(years, rel_iea, label='Model Inputs w/ IEA Distribution', color='tab:blue')
    plt.plot(years,rel_co2_t, label='Model Inputs w/ EPPA Distribution',color='red')
    plt.ylabel('$CO_{2}$ Emissions relative to 2020')
    plt.xlabel('Year')
    plt.ylim(ymin=0)
    plt.show()
    # allowable CO2 upper bound
    rel_ub = [i / ub[0] for i in ub]
    plt.plot(years,rel_ub, label='$CO_{2}$ Upper Bound from IEA SDS',color='tab:orange')

    rel_eppa = [i / eppa_co2_table[scen][0] for i in eppa_co2_table[scen]]
    plt.plot(years, rel_eppa, label=f" {proj}: {scen} ",color='green')
    plt.legend(loc='upper left')
    plt.show()


    ##COST
    # CO2
    plt.title(f" {proj}: {scen} Indian Steel Production Cost")
    cost_p = []
    # print(cost_bd)
    for p in pathways:
        ind_cost = []
        for y in years:
            c_d = cost_bd[y][p]*10**-3 #yearly cost
            ind_cost.append(c_d)
        cost_p.append(ind_cost)
        #plt.plot(years,demand,label = p)
    # print(cost_p)
    cost = [ i*10**-3 for i in cost]
    plt.stackplot(years,cost_p,labels=pathways)
    plt.plot(years, cost,color='red',label='Total - SESAME')
    plt.ylabel('Cost (billion USD)')
    plt.xlabel('Year')
    plt.legend(loc='upper left')
    plt.show()
    return

# TEST CODE
[years, s_demand, d_table,proj,scen] = user_inputs()
[y_mix,pathways,p_choice,eppa_p_mix] = prod_pathway(years,s_demand,d_table)
co2_em = co2_calc(y_mix,pathways,p_choice)
[cost,cost_bd] = cost_calc(y_mix,pathways,p_choice)
plot(years,s_demand,y_mix,proj,scen,pathways,co2_em,cost,cost_bd)
