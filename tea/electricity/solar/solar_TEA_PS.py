# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 11:45:44 2021

@author: ChemeGrad2019
"""
import os
import statistics

import pandas as pd
import numpy as np
import us

from tea.electricity.LCOE import LCOE
from core import conditionals, validators
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput
from core.tea import TeaBase


PATH = os.getcwd() + "/tea/electricity/solar/"



class SolarTEA(TeaBase):
    unit = '$/MWh'

    @classmethod
    def user_inputs(cls, with_lca = False):
        TEA_specific_inputs = [
            ContinuousInput('size', 'Input system DC size (MW)', validators=[validators.numeric(), validators.gte(0.1),validators.lte(100)], defaults = [Default(50)]),
            OptionsInput('finance_source', 'Select Data Source for Finance Costs', defaults=[Default('ATB')], options=['ATB', 'EIA', 'ReEDS']),
        ]
        if with_lca:
            return TEA_specific_inputs
        else:
            return [
                OptionsInput('city', 'Select installation location',  options=['US NE (Boston)', 'US SE (Miami)', 'US N (Minneapolis)', 'US NW (Seattle)', 'US W (San Francisco)', 'US SW (Phoenix)', 'China NE (Beijing)', 'China (Lhasa)', 'India (Mumbai)', 'Germany (Berlin)', 'Saudi Arabia (Riyadh)', 'Russia (Moscow)', 'Singapore', 'Spain (Madrid)', 'Colombia (Bogota)', 'Australia (Sydney)', 'US SW (Tucson)'], defaults = [Default('US W (San Francisco)')]),
                OptionsInput('cell', 'Select cell type',  options=['CdTe', 'CIGS', 'single crystal Si', 'multi crystal Si'], defaults = [Default('multi crystal Si')]),
                OptionsInput('location', 'Select installation type',  options=['Residential', 'Commercial', 'Utility'], defaults = [Default('Utility')]),
                   ] + TEA_specific_inputs + \
                [
                OptionsInput('roof', 'Select residential roof type', options=['Retrofit', 'New construction'],
                                 conditionals=[conditionals.input_equal_to('location','Residential')],
                                 defaults=[Default('Retrofit')]),
                OptionsInput('inverter', 'Select residential inverter',
                                 options=['String', 'Power optimizer', 'Microinverter', 'Unknown'],
                                 conditionals=[conditionals.input_equal_to('roof', 'Retrofit')],
                                 defaults=[Default('String')]),
                OptionsInput('installers', 'Select residential installers',
                                 options=['National integrator', 'Small installer', 'Unknown'],
                                 conditionals=[conditionals.input_not_equal_to('inverter', 'Unknown')],
                                 defaults=[Default('National integrator')]),
                OptionsInput('transformer', 'Transformer upgrade?', options=['Yes', 'No'], conditionals = [conditionals.input_equal_to('location','Residential')], defaults = [Default('Yes')]),
                OptionsInput('re_roofing', 'Re-roofing?',  options=['Yes', 'No'], conditionals = [conditionals.input_equal_to('roof','Retrofit')], defaults = [Default('No')]),
                OptionsInput('smaller', 'System smaller than 7kW DC capacity?',  options=['Yes', 'No'], conditionals = [conditionals.input_equal_to('location','Residential')], defaults = [Default('No')]),
                OptionsInput('panel_upgrade', 'Electric panel upgrade?',options=['Yes', 'No'], conditionals = [conditionals.input_equal_to('roof','Retrofit')], defaults = [Default('No')]),
                OptionsInput('commercial_location', 'Select commercial installation location',  options=['Flat roof', 'Ground'], conditionals = [conditionals.input_equal_to('location','Commercial')], defaults = [Default('Flat roof')]),
                OptionsInput('tilt', 'Select tilt setup', options=['fixed', '1-axis'], conditionals = [conditionals.input_equal_to('location','Utility')], defaults = [Default('1-axis')]),
                ContinuousInput('shading', 'Input shading losses (%)', validators=[validators.numeric(), validators.gte(0),validators.lte(100)], defaults = [Default(2.5)]),
                ContinuousInput('lifetime', 'Input system lifetime (years)', validators=[validators.numeric(), validators.gte(1),validators.lte(50)], defaults = [Default(30)]),
                ContinuousInput('efficiency', 'Input STC rated efficiency (%)', validators=[validators.numeric(), validators.gte(0),validators.lte(100)], defaults = [Default(18)]),
                ContinuousInput('degradation', 'Input degradation rate (%/year)', validators=[validators.numeric(), validators.gte(0),validators.lte(100)], defaults = [Default(0.8)]),
                ContinuousInput('ILR', 'Input inverter loading ratio', validators=[validators.numeric(), validators.gte(1),validators.lte(1.5)], defaults = [Default(1.3)])
                ]

    def __init__(self, lca_pathway=None):
        # print(lca_pathway)
        self.lca_pathway = lca_pathway
        self.finance = pd.read_csv(PATH + "finance.csv")
        if lca_pathway is None:
            # print('Hi')
            pass
        if lca_pathway is not None:
            self.cell = self.lca_pathway.instance('process').cell_type
            self.city = self.lca_pathway.instance('process').location
            self.shading = self.lca_pathway.instance('process').shading
            self.lifetime = self.lca_pathway.instance('process').lifetime
            self.efficiency = self.lca_pathway.instance('process').efficiency *100
            self.degradation = self.lca_pathway.instance('process').degradation
            self.ILR = self.lca_pathway.instance('process').ilr
            install_lca = self.lca_pathway.instance('process').cell_type
            if 'Utility' in install_lca:
                self.location = 'Utility'
                if 'fixed' in install_lca:
                    self.tilt = 'fixed'
                else:
                    self.tilt = '1-axis'
            else:
                self.location = 'Residential'
                self.roof = 'Retrofit'
                self.installers = 'National integrator'
                self.inverter = 'String'
                self.re_roofing = 'No'
                self.transformer = 'Yes'
                self.smaller = 'No'
                self.panel_upgrade = 'No'
        super().__init__()

    def get_finance_values(self):
        finance_costs = {}
        filtered = self.finance[self.finance['Source'] == self.finance_source]
        for row in filtered.to_dict(orient='records'):
            finance_costs[row['Abbr']] = float(row['value'])
        return finance_costs
    
    def get_capacity_factor(self):
        return float(self.CF)
    
    def set_capacity_factor(self,cf):
        # add check that cf is a float or int between 0, 1 inclusive
        self.CF = cf
        return None

    def get_lcoe(self):
        #creating adjustment factors
        efficiency_mf = 19.5/float(self.efficiency)
        efficiency_cost = 0
        ILR_cost = 0
        
        # print(self.shading)
        #pulling initial TEA values based on user input and then adjusting necessary values based on input efficiency and ILR
        if self.cell or self.cell == 'CIGS':
            cost_perW = pd.read_csv(PATH + 'thin film.csv', index_col = 0)
            if self.cell == 'CdTe':
                efficiency_mf = 14/float(self.efficiency) 
                ILR_mf = 1.3/float(self.ILR)         
                cost_perW = cost_perW.drop(['CIGS'], axis=1)
                
                efficiency_module_cost = cost_perW.loc['Module']*efficiency_mf - cost_perW.loc['Module']
                efficiency_cost = efficiency_cost + efficiency_module_cost
                cost_perW.loc['Module'] = cost_perW.loc['Module']*efficiency_mf
        
                ILR_inverter_cost = cost_perW.loc['Inverter']*ILR_mf - cost_perW.loc['Inverter']
                ILR_cost = ILR_cost + ILR_inverter_cost
                cost_perW.loc['Inverter'] = cost_perW.loc['Inverter']*ILR_mf
        
                efficiency_profit_cost = efficiency_cost*0.05
                efficiency_cost = efficiency_cost + efficiency_profit_cost
                cost_perW.loc['EPC Overhead & Profit'] = cost_perW.loc['EPC Overhead & Profit'] + efficiency_profit_cost        
        
                ILR_profit_cost = ILR_cost*0.05
                ILR_cost = ILR_cost + ILR_profit_cost
                cost_perW.loc['EPC Overhead & Profit'] = cost_perW.loc['EPC Overhead & Profit'] + ILR_profit_cost        
                
                efficiency_tax_cost = efficiency_cost*0.07
                efficiency_cost = efficiency_cost + efficiency_tax_cost
                cost_perW.loc['Sales Tax'] = cost_perW.loc['Sales Tax'] + efficiency_tax_cost        
        
                ILR_tax_cost = ILR_cost*0.07
                ILR_cost = ILR_cost + ILR_tax_cost
                cost_perW.loc['Sales Tax'] = cost_perW.loc['Sales Tax'] + ILR_tax_cost            
        
                cost_perW.loc['Total'] = cost_perW.loc['Total'] + efficiency_cost + ILR_cost
            
            else:
                efficiency_mf = 16/float(self.efficiency)
                ILR_mf = 1.3/float(self.ILR)         
                cost_perW = cost_perW.drop(['CdTe'], axis=1)
        
                efficiency_module_cost = cost_perW.loc['Module']*efficiency_mf - cost_perW.loc['Module']
                efficiency_cost = efficiency_cost + efficiency_module_cost
                cost_perW.loc['Module'] = cost_perW.loc['Module']*efficiency_mf
        
                ILR_inverter_cost = cost_perW.loc['Inverter']*ILR_mf - cost_perW.loc['Inverter']
                ILR_cost = ILR_cost + ILR_inverter_cost
                cost_perW.loc['Inverter'] = cost_perW.loc['Inverter']*ILR_mf
        
                efficiency_profit_cost = efficiency_cost*0.05
                efficiency_cost = efficiency_cost + efficiency_profit_cost
                cost_perW.loc['EPC Overhead & Profit'] = cost_perW.loc['EPC Overhead & Profit'] + efficiency_profit_cost        
        
                ILR_profit_cost = ILR_cost*0.05
                ILR_cost = ILR_cost + ILR_profit_cost
                cost_perW.loc['EPC Overhead & Profit'] = cost_perW.loc['EPC Overhead & Profit'] + ILR_profit_cost        
                
                efficiency_tax_cost = efficiency_cost*0.07
                efficiency_cost = efficiency_cost + efficiency_tax_cost
                cost_perW.loc['Sales Tax'] = cost_perW.loc['Sales Tax'] + efficiency_tax_cost        
        
                ILR_tax_cost = ILR_cost*0.07
                ILR_cost = ILR_cost + ILR_tax_cost
                cost_perW.loc['Sales Tax'] = cost_perW.loc['Sales Tax'] + ILR_tax_cost            
        
                cost_perW.loc['Total'] = cost_perW.loc['Total'] + efficiency_cost + ILR_cost
            #print('Results assume a 100MW system with fixed tilt') 
        
        if self.location == 'Residential':
            ILR_mf = 1.14/float(self.ILR)  
            if self.roof == 'Retrofit':
                cost_perW = pd.read_csv(PATH + 'residential.csv', index_col = 0)
            elif self.roof != 'Retrofit':
                cost_perW = pd.read_csv(PATH + 'residential_new.csv', index_col = 0)
        
            if self.cell == 'multi crystal Si':
                multi_cost = -0.06
                if self.roof != 'Retrofit':
                    cost_perW.iloc[-1, 0] = cost_perW.iloc[-1, 0] + multi_cost
                    cost_perW.loc['Install Cost'] = cost_perW.loc['Install Cost'] + multi_cost
                elif self.roof == 'Retrofit':
                    cost_perW.iloc[-1, 0] = cost_perW.iloc[-1, 0] + multi_cost
                    cost_perW.loc['Module'] = cost_perW.loc['Module'] + multi_cost       
            
            if self.roof == 'Retrofit':     
                if self.inverter == 'Unknown':
                    cost_perW = cost_perW['Residential - Unknown Inverter']
                elif self.inverter == 'String':
                    ILR_mf = 1.11/float(self.ILR)
                    if self.installers == 'Small installer':
                        cost_perW = cost_perW['Residential - String Inverter - Small Installer']
                    elif self.installers == 'National integrator':
                        cost_perW = cost_perW['Residential - String Inverter - National Integrator']
                    elif self.installers == 'Unknown':
                        cost_perW = cost_perW['Residential - String Inverter - Unknown Installer']
                    else:
                        print('Issue with selected installer option')
                elif self.inverter == 'Power optimizer':
                    ILR_mf = 1.16/float(self.ILR)
                    if self.installers == 'Small installer':
                        cost_perW = cost_perW['Residential - Power Optimizer - Small Installer']
                    elif self.installers == 'National integrator':
                        cost_perW = cost_perW['Residential - Power Optimizer - National Integrator']
                    elif self.installers == 'Unknown':
                        cost_perW = cost_perW['Residential - Power Optimizer - Unknown Installer']            
                    else:
                        print('Issue with selected installer option')
                elif self.inverter == 'Microinverter':
                    ILR_mf = 1.16/float(self.ILR)
                    if self.installers == 'Small installer':
                        cost_perW = cost_perW['Residential - Microinverter - Small Installer']
                    elif self.installers == 'National integrator':
                        cost_perW = cost_perW['Residential - Microinverter - National Integrator']
                    elif self.installers == 'Unknown':
                        cost_perW = cost_perW['Residential - Microinverter - Unknown Installer'] 
                    else:
                        print('Issue with selected installer option')
                else:
                    print('Isssue with selected inverter option')           
            #print('Results assume a 7kW system')    
        
            cost_perW = pd.DataFrame(cost_perW)
            cost_perW_shape = cost_perW.shape
            if self.transformer == 'Yes':
                transformer_cost = 0.1
                cost_perW2 = pd.DataFrame(transformer_cost, index=range(1),columns=range(1))
                cost_perW2.columns = cost_perW.columns
                cost_perW.iloc[-1, 0] = cost_perW.iloc[-1, 0] + transformer_cost
                cost_perW = pd.concat([cost_perW2, cost_perW], axis=0)
                cost_perW.rename({cost_perW.index[0]: 'transformer'}, inplace=True) 
        
            if self.re_roofing == 'Yes':
                re_roofing_cost = 0.1
                cost_perW2 = pd.DataFrame(re_roofing_cost, index=range(1),columns=range(1))
                cost_perW2.columns = cost_perW.columns
                cost_perW.iloc[-1, 0] = cost_perW.iloc[-1, 0] + re_roofing_cost
                cost_perW = pd.concat([cost_perW2, cost_perW], axis=0)
                cost_perW.rename({cost_perW.index[0]: 're-roofing'}, inplace=True)  
                
            if self.smaller == 'Yes':
                smaller_cost = 0.03*efficiency_mf
                efficiency_smaller_cost = smaller_cost - smaller_cost/efficiency_mf
                efficiency_cost = efficiency_cost + efficiency_smaller_cost        
                cost_perW2 = pd.DataFrame(smaller_cost, index=range(1),columns=range(1))
                cost_perW2.columns = cost_perW.columns
                cost_perW.iloc[-1, 0] = cost_perW.iloc[-1, 0] + smaller_cost
                cost_perW = pd.concat([cost_perW2, cost_perW], axis=0)
                cost_perW.rename({cost_perW.index[0]: 'smaller system'}, inplace=True) 
        
            if self.panel_upgrade == 'Yes':
                upgrade_cost = 0.1*efficiency_mf
                efficiency_upgrade_cost = upgrade_cost - upgrade_cost/efficiency_mf
                efficiency_cost = efficiency_cost + efficiency_upgrade_cost         
                cost_perW2 = pd.DataFrame(upgrade_cost, index=range(1),columns=range(1))
                cost_perW2.columns = cost_perW.columns
                cost_perW.iloc[-1, 0] = cost_perW.iloc[-1, 0] + upgrade_cost
                cost_perW = pd.concat([cost_perW2, cost_perW], axis=0)
                cost_perW.rename({cost_perW.index[0]: 'panel upgrade'}, inplace=True) 
            
            if self.roof != 'Retrofit':
                efficiency_install_cost = cost_perW.loc['Install Cost']*efficiency_mf - cost_perW.loc['Install Cost']
                efficiency_cost = efficiency_cost + efficiency_install_cost
                cost_perW.loc['Install Cost'] = cost_perW.loc['Install Cost']*efficiency_mf
               
                ILR_install_cost = cost_perW.loc['Install Cost']*ILR_mf - cost_perW.loc['Install Cost']
                ILR_cost = ILR_cost + ILR_install_cost
                cost_perW.loc['Install Cost'] = cost_perW.loc['Install Cost']*ILR_mf        
                
                efficiency_profit_cost = efficiency_cost*0.17
                efficiency_cost = efficiency_cost + efficiency_profit_cost
                cost_perW.loc['Profit'] = cost_perW.loc['Profit'] + efficiency_profit_cost
        
                ILR_profit_cost = ILR_cost*0.17
                ILR_cost = ILR_cost + ILR_profit_cost
                cost_perW.loc['Profit'] = cost_perW.loc['Profit'] + ILR_profit_cost
                
                cost_perW.loc['Total'] = cost_perW.loc['Total'] + efficiency_cost + ILR_cost
            
            elif self.roof == 'Retrofit':
                efficiency_module_cost = cost_perW.loc['Module']*efficiency_mf - cost_perW.loc['Module']
                efficiency_cost = efficiency_cost + efficiency_module_cost
                cost_perW.loc['Module'] = cost_perW.loc['Module']*efficiency_mf
                
                efficiency_structural_cost = cost_perW.loc['Structural BoS']*efficiency_mf - cost_perW.loc['Structural BoS']
                efficiency_cost = efficiency_cost + efficiency_structural_cost
                cost_perW.loc['Structural BoS'] = cost_perW.loc['Structural BoS'] + efficiency_structural_cost
        
                ILR_inverter_cost = cost_perW.loc['Inverter']*ILR_mf - cost_perW.loc['Inverter']
                ILR_cost = ILR_cost + ILR_inverter_cost
                cost_perW.loc['Inverter'] = cost_perW.loc['Inverter'] + ILR_inverter_cost
        
                efficiency_supply_cost = efficiency_cost*0.15
                efficiency_profit_cost = efficiency_cost*0.17
                efficiency_cost = efficiency_cost + efficiency_profit_cost + efficiency_supply_cost
                cost_perW.loc['Profit'] = cost_perW.loc['Profit'] + efficiency_profit_cost
                cost_perW.loc['Supply Chain Costs'] = cost_perW.loc['Supply Chain Costs'] + efficiency_supply_cost
        
                ILR_supply_cost = ILR_cost*0.15
                ILR_profit_cost = ILR_cost*0.17
                ILR_cost = ILR_cost + ILR_profit_cost + ILR_supply_cost
                cost_perW.loc['Profit'] = cost_perW.loc['Profit'] + ILR_profit_cost
                cost_perW.loc['Supply Chain Costs'] = cost_perW.loc['Supply Chain Costs'] + ILR_supply_cost
        
        
                efficiency_tax_cost = efficiency_cost*0.07
                efficiency_cost = efficiency_cost + efficiency_tax_cost
                cost_perW.loc['Sales Tax'] = cost_perW.loc['Sales Tax'] + efficiency_tax_cost        
        
                ILR_tax_cost = ILR_cost*0.07
                ILR_cost = ILR_cost + ILR_tax_cost
                cost_perW.loc['Sales Tax'] = cost_perW.loc['Sales Tax'] + ILR_tax_cost        
          
                cost_perW.loc['Total'] = cost_perW.loc['Total'] + efficiency_cost + ILR_cost
           
        
        if self.location == 'Commercial':
            ILR_mf = 1.14/float(self.ILR)
            df = pd.read_csv(PATH +'commercial.csv', index_col = 0)
            alphas_df = pd.read_csv(PATH +'commercial alphas.csv', index_col = 0)
            if self.cell == 'multi crystal Si':
                multi_cost = -0.06
                df.iloc[-1, 0] = df.iloc[-1, 0] + multi_cost
                df.loc['Module'] = df.loc['Module'] + multi_cost
            
            if self.commercial_location ==  'Flat roof':
                base = df['Commericial - flat roof - 0.1MW']*0.1
                base = base.drop(base.index[-1])
                a = alphas_df['a - flat']
                b = alphas_df['b - flat']
                alpha = a*np.log(float(self.size)) + b 
                cost = base*(float(self.size)/0.1)**alpha
                cost['Total'] = cost.sum()
                cost_perW = cost/float(self.size)
                    
            if self.commercial_location ==  'Ground':
                base = df['Commericial - ground mount - 0.1MW']*0.1
                base = base.drop(base.index[-1])
                a = alphas_df['a - ground']
                b = alphas_df['b - ground']
                alpha = a*np.log(float(self.size)) + b 
                cost = base*(float(self.size)/0.1)**alpha
                cost['Total'] = cost.sum()           
                cost_perW = cost/float(self.size)
            
            efficiency_module_cost = cost_perW.loc['Module']*efficiency_mf - cost_perW.loc['Module']
            efficiency_cost = efficiency_cost + efficiency_module_cost
            cost_perW.loc['Module'] = cost_perW.loc['Module']*efficiency_mf
            
            efficiency_structural_cost = cost_perW.loc['Structural BOS']*efficiency_mf - cost_perW.loc['Structural BOS']
            efficiency_cost = efficiency_cost + efficiency_structural_cost
            cost_perW.loc['Structural BOS'] = cost_perW.loc['Structural BOS'] + efficiency_structural_cost
        
            ILR_inverter_cost = cost_perW.loc['Inverter']*ILR_mf - cost_perW.loc['Inverter']
            ILR_cost = ILR_cost + ILR_inverter_cost
            cost_perW.loc['Inverter'] = cost_perW.loc['Inverter'] + ILR_inverter_cost
        
            efficiency_profit_cost = efficiency_cost*0.07
            efficiency_cost = efficiency_cost + efficiency_profit_cost
            cost_perW.loc['EPC/Developer Profit'] = cost_perW.loc['EPC/Developer Profit'] + efficiency_profit_cost
        
            ILR_profit_cost = ILR_cost*0.07
            ILR_cost = ILR_cost + ILR_profit_cost
            cost_perW.loc['EPC/Developer Profit'] = cost_perW.loc['EPC/Developer Profit'] + ILR_profit_cost
        
            efficiency_tax_cost = efficiency_cost*0.07
            efficiency_cost = efficiency_cost + efficiency_tax_cost
            cost_perW.loc['Sales Tax'] = cost_perW.loc['Sales Tax'] + efficiency_tax_cost        
        
            ILR_tax_cost = ILR_cost*0.07
            ILR_cost = ILR_cost + ILR_tax_cost
            cost_perW.loc['Sales Tax'] = cost_perW.loc['Sales Tax'] + ILR_tax_cost      
        
            cost_perW.loc['Total'] = cost_perW.loc['Total'] + efficiency_cost + ILR_cost      
                
            
        if self.location == 'Utility':
            df = pd.read_csv(PATH +'utility.csv', index_col = 0)
            alphas_df = pd.read_csv(PATH +'utility alphas.csv', index_col = 0)
            if self.cell == 'multi crystal Si':
                multi_cost = -0.05
                df.iloc[-1, 0] = df.iloc[-1, 0] + multi_cost
                df.loc['Module'] = df.loc['Module'] + multi_cost
        
            if self.tilt ==  'fixed':
                ILR_mf = 1.37/float(self.ILR)
                base = df['Utility - Fixed Tilt - 5MW']*5
                base = base.drop(base.index[-1])
                a = alphas_df['a - fixed']
                b = alphas_df['b - fixed']
                alpha = a*np.log(float(self.size)) + b 
                cost = base*(float(self.size)/5)**alpha
                cost['Total'] = cost.sum() 
                cost_perW = cost/float(self.size)
                    
            if self.tilt ==  '1-axis':
                ILR_mf = 1.34/float(self.ILR)
                base = df['Utility - Fixed Tilt - 5MW']*5
                base = base.drop(base.index[-1])
                a = alphas_df['a - fixed']
                b = alphas_df['b - fixed']
                alpha = a*np.log(float(self.size)) + b 
                cost = base*(float(self.size)/5)**alpha
                cost['Total'] = cost.sum() 
                cost_perW = cost/float(self.size)
        
            efficiency_module_cost = cost_perW.loc['Module']*efficiency_mf - cost_perW.loc['Module']
            efficiency_cost = efficiency_cost + efficiency_module_cost
            cost_perW.loc['Module'] = cost_perW.loc['Module']*efficiency_mf
            
            efficiency_structural_cost = cost_perW.loc['Structural BOS']*efficiency_mf - cost_perW.loc['Structural BOS']
            efficiency_cost = efficiency_cost + efficiency_structural_cost
            cost_perW.loc['Structural BOS'] = cost_perW.loc['Structural BOS'] + efficiency_structural_cost
        
            ILR_inverter_cost = cost_perW.loc['Inverter']*ILR_mf - cost_perW.loc['Inverter']
            ILR_cost = ILR_cost + ILR_inverter_cost
            cost_perW.loc['Inverter'] = cost_perW.loc['Inverter'] + ILR_inverter_cost
        
            efficiency_profit_cost = efficiency_cost*0.07
            efficiency_cost = efficiency_cost + efficiency_profit_cost
            cost_perW.loc['EPC/Developer Profit'] = cost_perW.loc['EPC/Developer Profit'] + efficiency_profit_cost.values[0]
        
            ILR_profit_cost = ILR_cost*0.07
            ILR_cost = ILR_cost + ILR_profit_cost
            cost_perW.loc['EPC/Developer Profit'] = cost_perW.loc['EPC/Developer Profit'] + ILR_profit_cost.values[0]
        
            efficiency_tax_cost = efficiency_cost*0.07
            efficiency_cost = efficiency_cost + efficiency_tax_cost
            cost_perW.loc['Sales Tax'] = cost_perW.loc['Sales Tax'] + efficiency_tax_cost.values[0]       
        
            ILR_tax_cost = ILR_cost*0.07
            ILR_cost = ILR_cost + ILR_tax_cost
            cost_perW.loc['Sales Tax'] = cost_perW.loc['Sales Tax'] + ILR_tax_cost.values[0]      
        
            cost_perW.loc['Total'] = cost_perW.loc['Total'] + efficiency_cost.values[0] + ILR_cost.values[0]
                  

        # Calculation of maintenance costs
        if self.location == 'Residential':
            maintenance_cost = 28.94 * float(self.lifetime)*7
        elif self.location == 'Commercial':
            if self.commercial_location ==  'Flat roof':
                maintenance_cost = 18.55 * float(self.lifetime)*float(self.size)*1000
            else:
                maintenance_cost = 18.71 * float(self.lifetime)*float(self.size)*1000
        elif self.location == 'Utility':
            if self.tilt ==  'fixed':
                maintenance_cost = 16.32 * float(self.lifetime)*float(self.size)*1000
            else:
                maintenance_cost = 17.46 * float(self.lifetime)*float(self.size)*1000
        elif self.cell == 'CdTe' or self.cell == 'CGIS':
            maintenance_cost = 16.32 * float(self.lifetime)*100*1000           
        else:
            print('Error with calculating maintenance cost')  
        

        if self.location == 'Residential':
            total_cost = cost_perW.loc['Total']*7.0*1000 + maintenance_cost
        elif self.cell == 'CIGS' or self.cell == 'CdTe':  
            total_cost = cost_perW.loc['Total']*100*1000000 + maintenance_cost
        else:
            total_cost = cost_perW.loc['Total']*float(self.size)*1000000 + maintenance_cost
        
        
        # Calculation of required CF
        if self.location == 'Residential':
            install_type = 'rooftop, typical tilt'
        elif self.tilt == '1-axis':
            install_type = 'utility, 1-axis tracking'
        else: 
            install_type = 'utility, fixed tilt'
            
        tec=0.4223 # Typical tracker energy consumption per panel area in kWh/m²/yr
        # (Source: (5) Sinha, Eco-Efficiency of CdTe Photovoltaics with Tracking Systems, 2013, IEEE)
        
        cf_table=pd.read_csv(PATH +"solar_tables.csv")
        if 'Si' in self.cell:
             pat=' Si'
        else:
             pat=' TF'
             
        column_key=install_type+pat
        cf_row = cf_table.loc[cf_table['Location'] == self.city]
        
        cf_loc = cf_row[column_key].values
        cf_loc = float(cf_loc)
        snow_loss=cf_row['snow loss if any (%)'].values
        CF_DC_1 = cf_loc*(1-snow_loss/100)
        CF_DC_2 = CF_DC_1*(1-float(self.shading)/100)
        CF_DC = CF_DC_2*(1-float(self.lifetime)*float(self.degradation)/100/2)
        if install_type == 'utility, 1-axis tracking':
            CF_DC = CF_DC - 100*tec/self.efficiency/8760
        
        CF_AC = CF_DC/float(self.ILR)
        
        if self.location == 'Residential': 
            max_output = 7000*8760*float(self.lifetime)
        else:
            # MW * 10^6 * hr * lifetime --> Wh
            # max_output = float(self.size)*1000000*8760*float(self.lifetime)
            # MW * hr * lifetime --> MWh
            max_output = float(self.size)*8760*float(self.lifetime)
        # self.CF = CF_AC
        # output = CF_AC/100*max_output

        # call set_capacity_factor() in power_and_storage.py before get_cost_breakdown()
        output = self.CF*max_output
        # LCOE = total_cost/output
        
        
        #creation of capital costs dictionary
        cost_perW_df = cost_perW.copy()#to_frame()
        cost_perW_transposed = cost_perW_df.T
        cost_perW_transposed = cost_perW_transposed.drop(columns = ['Total'])
        
        
        # if self.location == 'Residential':
        #     capital_LCOE = cost_perW_transposed*7.0*1000/float(output)*1000000
        # elif self.cell == 'CIGS' or self.cell == 'CdTe':  
        #     capital_LCOE = cost_perW_transposed*100*1000000/float(output)*1000000
        # else:
        #     # capital_LCOE = cost_perW_transposed*float(self.size)*1000000/float(output)*1000000
        #     # $/W * (MW * 10^6) / MWh_lifetime --> $/MWh
        #     capital_LCOE = cost_perW_transposed*float(self.size)*1000000/float(output)
        
        # # capital_cost_dict = capital_LCOE.to_dict('records')
        # capital_cost_dict = capital_LCOE.to_dict()

        # # solar_cost_breakdown = {'Capital and Fixed':capital_cost_dict['Total'],'Operational':0,'Maintenance':float(maintenance_cost/output)*1000000}
        # solar_cost_breakdown = {'Capital and Fixed':capital_cost_dict['Total'],'Operational':0,'Maintenance':float(maintenance_cost/output)*1000}
        
        # return solar_cost_breakdown



        # Change LCOE calculation to use LCOE()
        cap_reg_mult = 1
        # $/W * 1000 --> $/kW
        OCC = cost_perW_transposed['Total'] * 1000
        # FOM value copied from above (line 467)
        FOM = 17.46
        VOM = 0
        finance_values = self.get_finance_values()
        grid_cost = 0
        fuel_cost = 0 
        solar_lcoe = LCOE(self.CF, cap_reg_mult, OCC, FOM, VOM, finance_values, self.lifetime, grid_cost, fuel_cost)

        return solar_lcoe

    def get_cost_breakdown(self):
        lcoe = self.get_lcoe()
        cost_breakdown = lcoe.get_cost_breakdown()
        return cost_breakdown