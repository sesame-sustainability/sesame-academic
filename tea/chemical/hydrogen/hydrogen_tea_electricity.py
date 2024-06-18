#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###Notes###
# large portion of H2 produced via SMR, not coal. That's why we don't consider. Source: https://www.hydrogen.energy.gov/pdfs/hydrogen-program-plan-2020.pdf
# See sources for values in 'hydrogen_production_tech.csv' in 'hydrogen_production_tech_sources.csv'

import os
import pandas as pd
import us, statistics


from core.inputs import OptionsInput, Default, ContinuousInput, CategoricalInput, Tooltip, PercentInput, Input
from core.tea import TeaBase
from core import validators, conditionals
from tea.electricity.ccs.pointsources.ccs_tea import CcsTea
from analysis.sensitivity import SensitivityInput

PATH = os.getcwd() + "/tea/chemical/hydrogen/"

class HydrogenTEA(TeaBase):
    unit = '$/kg'

    @classmethod
    def user_inputs(cls, tea_lca=False, prod_type=None):
        tea_only_inputs1 =[
            OptionsInput(
                'pt', 'Production Type',
                options=['Alk', 'PEM'],
                defaults=[Default('PEM')],
                tooltip=Tooltip(
                    'SMR (steam methane reforming) is the most common H2 production method today, which uses natural gas as the feedstock ("grey" H2). If CCS (carbon capture and sequester) is used in combination, "blue" H2 is produced.  Alk (alkaline water electrolysis, relatively traditional) and PEM (polymer electrolyte membrane electrolysis, newer) are water electrolysis technologies using electricity as the major energy input. If the electricity is from renewables, "green" H2 is produced.',
                )

            ),
            # OptionsInput(
            #     'use_CCS', 'Use CCS (Carbon Capture & Sequester)',
            #     options=['Yes', 'No'],
            #     defaults=[Default('No')],
            #     # conditionals=[conditionals.input_equal_to('pt', 'SMR')],
            #     tooltip=Tooltip(
            #         'As a carbon mitigation technology, a CCS unit captures CO2 from a manufacturing plant and transport the captured CO2 to a sequestration site for long-term storage.',
            #     )
            #
            # ),
        ]

        tea_only_inputs2 = [
            # these inputs below are not defined in the LCA
            ContinuousInput(
                'effic', 'Hydrogen Production Efficiency',
                unit='kWh/kg_H\u2082',
                defaults=[Default(57.2)],
                # conditionals=[conditionals.input_not_equal_to('pt', 'SMR')],
                validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
            ),
            # ContinuousInput(
            #     'effic_SMR', 'Hydrogen Production Efficiency',
            #     unit='%',
            #     defaults=[Default(81.3)],
            #     conditionals=[
            #         conditionals.input_not_equal_to('pt', 'Alk'),
            #         conditionals.input_not_equal_to('pt', 'PEM'),
            #     ],
            #     validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
            # ),
            OptionsInput(
                'state', 'Hydrogen Phase',
                # This should be united with LCA
                options=['Gas', 'Liquid'],
                defaults=[Default('Gas')],
                tooltip=Tooltip(
                    'If gas, transportation & distribution is by pipeline. If liquid, transportation is by barge shipping, and distribution is by truck, and H\u2082 liquefaction cost is also included in the transportation & distribution cost.',
                    source='IEA 2019',
                    source_link='https://static1.squarespace.com/static/5c350d6bcc8fedc9b21ec4c5/t/5e968939e89b9e37585b8134/1586923883881/IEA+-+The_Future_of_Hydrogen.pdf',
                ),
            ),
            ContinuousInput(
                'distance', 'Distance, Process to Use',
                unit ='mi',
                defaults=[
                    Default(750, conditionals=[conditionals.input_equal_to('state', 'Gas')]),
                    Default(520, conditionals=[conditionals.input_equal_to('state', 'Liquid')]),
                ],
                validators=[validators.numeric(), validators.gte(0), validators.lte(10000)],
                tooltip=Tooltip(
                    'Distance from H\u2082 production site to demand point. For gas H\u2082, input total pipeline distance for transportation and distribution. For liquid H\u2082, input barge shipping distance for transportation, and 30 mi trucking distance for distribution is assumed based on GREET 2019 data.',
                    source='GREET 2019',
                    source_link='https://greet.es.anl.gov/',
                ),
            ),
        ]

        tea_lca_defaults = {
            'H2_produced': {
                'Alk': 60,
                'PEM': 300,
                # 'SMR': 100000,
            },
            'capex': {
                'Alk': 1214,
                'PEM': 1771,
                # 'SMR': 678,
            },
            'fom': {
                'Alk': 55,
                'PEM': 75,
                # 'SMR': 23,
            },
            'scaling_factor': {
                'Alk': 0.75, # Source: https://www.storeandgo.info/fileadmin/downloads/deliverables_2019/20190801-STOREandGO-D7.7-EIL-Analysis_on_future_technology_options_and_on_techno-economic_optimization.pdf
                'PEM': 0.75,
                # 'SMR': 0.6,
            },
        }

        tea_lca_inputs = [
            ContinuousInput(
                'H2_produced', 'Hydrogen Production Rate',
                unit='m\u00B3/hr',
                validators=[validators.numeric(), validators.gte(0), validators.lte(1000000)],
            ),
            ContinuousInput(
                'capex', 'Capital Cost, Given Default Inputs',
                unit='$/kW',
                validators=[validators.numeric(), validators.gte(0)],
            ),
            ContinuousInput(
                'fom', 'Fixed Operating Cost, Given Defaults',
                unit='$/kW/yr',
                validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
            ),
            ContinuousInput(
                'capacity_factor', 'Asset Capacity Factor',
                unit='%',
                defaults=[Default(90)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
            ),
            ContinuousInput(
                'scaling_factor', 'Capital Cost Scaling Factor',
                validators=[validators.numeric(), validators.gte(0), validators.lte(1)],
            ),
            ContinuousInput(
                'discount_rate', 'Discount Rate',
                unit='%',
                defaults=[Default(4)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
            ),
            ContinuousInput(
                'lifetime', 'Lifetime',
                defaults=[Default(20)],
                validators=[validators.integer(), validators.gte(0)],
            ),
            # ContinuousInput(
            #     'Gas_Cost', 'Natural Gas Price',
            #     unit='$/MMBtu',
            #     defaults=[Default(3)],
            #     conditionals=[
            #         conditionals.input_not_equal_to('pt', 'Alk'),
            #         conditionals.input_not_equal_to('pt', 'PEM'),
            #     ],
            #     validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
            # ),
        ]
# SSS- unchanged. wasnt sure what to do here
        if tea_lca and prod_type == 'SMR':
            # only include single default for given prod type
            for input in tea_lca_inputs:
                if input.name in tea_lca_defaults:
                    input.defaults.append(Default(tea_lca_defaults[input.name][prod_type]))
        else:
            # include conditional defaults for all prod types
            for input in tea_lca_inputs:
                if input.name in tea_lca_defaults:
                    for pt, default in tea_lca_defaults[input.name].items():
                        input.defaults.append(Default(default, conditionals=[conditionals.input_equal_to('pt', pt)]))
# EEE

        # Splitting up the tea only inputs because Power Price should not appear for SMR when LCA is done with TEA but should appear in all other cases
        tea_inputs2 = [
            ContinuousInput(
                'Power_Price','Power Price ($/MWh)',
                defaults=[Default(80)], # Includes 66 production and 14 transmission to represent industrial power price
                validators=[validators.numeric(), validators.gte(0), validators.lte(1000)],
                # conditionals=[conditionals.input_not_equal_to('pt','SMR')] #is this conditional redundant?
            ),
        ]

        if tea_lca:
            # if prod_type == 'SMR':
            #     return tea_lca_inputs + CcsTea.user_inputs(source='Hydrogen Production', tea_lca=tea_lca)
            # else:
            return [
                OptionsInput(
                    'pt', 'Production Type',
                    options=['Alk', 'PEM'],
                    defaults=[Default('PEM')],
                ),
            ] + tea_lca_inputs + tea_inputs2
        else:
            return tea_only_inputs1 + tea_only_inputs2 + tea_lca_inputs + tea_inputs2 + CcsTea.user_inputs(source='Hydrogen Production')
#SSS
    @classmethod
    def sensitivity(cls, lca_pathway=None):
        source_ids = []
        if lca_pathway is not None:
            source_ids = [step.source.id for step in lca_pathway.steps]

        sensitivity_inputs = [
            SensitivityInput('pt', minimizing='Alk', maximizing='PEM'),
            SensitivityInput('effic', data_lacking=True),
            # SensitivityInput('effic_SMR', data_lacking=True),
            SensitivityInput('distance', data_lacking=True),
            SensitivityInput('H2_produced', data_lacking=True),
            SensitivityInput('capex', data_lacking=True),
            SensitivityInput('fom', data_lacking=True),
            SensitivityInput('capacity_factor', minimizing=100,maximizing=.7*90),
            SensitivityInput('scaling_factor', data_lacking=True),
            SensitivityInput('discount_rate', data_lacking=True),
            SensitivityInput('lifetime', data_lacking=True),
            # SensitivityInput('Gas_Cost', data_lacking=True),
            SensitivityInput('Power_Price', data_lacking=True),
            SensitivityInput('state', minimizing='Gas', maximizing='Liquid'),
        ]

        # if lca_pathway is None or 'process-productionusingelectrolysis-greet' in source_ids:
        #     sensitivity_inputs += [
        #         SensitivityInput('pt', minimizing='Alk', maximizing='PEM'),
        #         SensitivityInput('state', minimizing='Gas', maximizing='Liquid'),
        #     ]

        return sensitivity_inputs
#EEE

    def __init__(self, lca_pathway=None):
        self.lca_pathway = lca_pathway
        self.h2_production_param = pd.read_csv(PATH + "hydrogen_production_tech.csv")
        # if lca_pathway is not None:
        super().__init__(lca_pathway)

    def prepare(self, input_set):
        super().prepare(input_set)

        if self.lca_pathway is not None:
            inputs = type(self).user_inputs()
            stage = self.lca_pathway.instance('process')
            stage2 = self.lca_pathway.instance('gatetoenduse')
            ## Setting production type and efficiency values if lca is also done
            flow_dict = stage.get_inputs()
            stage.pt = pt  # SSS
            if stage.pt == 'SMR':
                elec = flow_dict['secondary']['electricity']['value']
            else:
                elec = flow_dict['primary']['value'] # MJ electricity / MJ H2

            ## setting direct inputs
            for input in inputs:
                if hasattr(stage, input.name):
                    value = getattr(stage, input.name)
                    setattr(self, input.name, value)
                else:
                    setattr(self, input.name, input_set.default_value(input.name))

            ## setting input values obtained from calculations in LCA
            if stage.pt == 'SMR':
                ng = flow_dict['primary']['value']
                self.power_efficiency = elec/ng
                self.effic_SMR = 1/ng

                if stage.use_CCS == 'Yes':
                    em = stage.get_emissions()
                    self.electricity_ci = stage.ccs.elec_carbon_intensity
                    self.CO2_captured_dict = {}
                    self.CO2_captured_dict['total'] = stage.ccs.CO2_captured
                    self.CO2_captured_dict['plant'] = stage.ccs.CO2_captured_plant
                    self.CO2_captured_dict['regen'] = stage.ccs.CO2_captured_regen
                    self.CO2_captured_dict['comp'] = stage.ccs.CO2_captured_comp

                if stage.co_produce_steam == 'Yes': # yes = steam co-produced
                    self.steam = flow_dict['secondary']['steam co-generated']['value'] * -1
                else:
                    self.steam = 0
            else:
                MJ_H2_per_kg = 120 # source : https://www.energy.gov/eere/fuelcells/hydrogen-storage#:~:text=On%20a%20mass%20basis%2C%20hydrogen,44%20MJ%2Fkg%20for%20gasoline.
                self.effic = elec * 0.277778 * MJ_H2_per_kg #0.2778 is MJ to kWh

            ## Setting gate2enduse distance value
            self.distance = stage2.distance

#Read Data

    def get_production_type(self):
        if self.lca_pathway:
            process_user_inputs = self.lca_pathway['Process']['user_inputs']
            prod_type = process_user_inputs.get("Production Type")
        else:
            prod_type = self.pt
        return prod_type

    def get_cost_breakdown(self):
        prod_type = self.pt
        # if hasattr(self,'effic') and self.lca_pathway is None:
        #     self.effic = self.effic/100 # converting % to fraction

        if prod_type == 'Alk':
            index = 0
        elif prod_type == 'PEM':
            index = 1
        else:
            index = 2
            # if self.use_CCS == "Yes":
            #     prod_type = prod_type + '_CCS'
            #     index = 3


        self.capacity_factor = self.capacity_factor/100
        self.discount_rate = self.discount_rate/100

        #get values based off user input
        water_cons = self.h2_production_param.iloc[index, 4]
        power_efficiency = self.h2_production_param.iloc[index, 6]
        non_fuel_VOM = self.h2_production_param.iloc[index, 7]
        # if hasattr(self,'power_efficiency'):
        #     power_efficiency = self.power_efficiency
        #Assumptions

        #Upstream
        H2_density = 0.091 # kg/m3
        water_price = 0.0017 # $/liter
        scaling_factor = self.scaling_factor
        Euro_USD_fx = 1.2

        #####################
        ## Midstream Model ##
        #####################
        miles_to_km = 1.60934
        liquefaction_cost = 1 # $/kg Fig 27 from https://static1.squarespace.com/static/5c350d6bcc8fedc9b21ec4c5/t/5e968939e89b9e37585b8134/1586923883881/IEA+-+The_Future_of_Hydrogen.pdf
        barge_cost = 0.001 # $/kg/mi Fig 27 from https://static1.squarespace.com/static/5c350d6bcc8fedc9b21ec4c5/t/5e968939e89b9e37585b8134/1586923883881/IEA+-+The_Future_of_Hydrogen.pdf
        truck_cost = 0.0016 # $/kg/mi Fig 28 from https://static1.squarespace.com/static/5c350d6bcc8fedc9b21ec4c5/t/5e968939e89b9e37585b8134/1586923883881/IEA+-+The_Future_of_Hydrogen.pdf
        liquid_TD_cost = liquefaction_cost + 1*self.distance*barge_cost + 1*30*truck_cost # $/kg Liquid H2 transportation & distribution cost (including liquefaction), assuming 100% barge for transportation and 100% truck for distribution (GREET assumed 50% barge and 50% rail for transportation, but no proper cost data has been found for H2 railing, thus 100% barge is assumed)
                        # the 520 and 30 are US average one-way miles travelled by barge and truck from GREET 2019 T&D tab Row 210-213 and 110
        if self.state == 'Gas':
            self.distance = self.distance * miles_to_km
            transmission_cost = self.distance/1500 # The 1500 factor is based on km unit. Extrapolation based on pipline transportation from Page 80 of: https://static1.squarespace.com/static/5c350d6bcc8fedc9b21ec4c5/t/5e968939e89b9e37585b8134/1586923883881/IEA+-+The_Future_of_Hydrogen.pdf
        else:
            transmission_cost = liquid_TD_cost # $/kg

        #calculations

        hours_operation = 8760 * self.capacity_factor # hr/yr
        H2_produced_kg = self.H2_produced * H2_density * hours_operation

        crf = (self.discount_rate * ((1 + self.discount_rate) ** self.lifetime)) / (
                    (1 + self.discount_rate) ** (self.lifetime) - 1)  # %
        production_m3 = hours_operation * self.H2_produced  # m3/yr
        production_kg = production_m3 * H2_density  # kg/yr

        # if prod_type == 'Alk' or prod_type == 'PEM':
        power_consumption = (self.effic/11) * production_m3 # kWh -kWh/(kg*m3/kg) * (m3/yr) - 11 density of H2
        elect_size = power_consumption / hours_operation # kW
        FOM_cost = elect_size * self.fom # $/yr

        if prod_type == 'Alk':
            capex_scaled = ((300 * self.capex) * (elect_size / 300)**scaling_factor)/elect_size
        else:
            capex_scaled = ((1500 * self.capex) * (elect_size / 1500) ** scaling_factor) / elect_size

        CapEx = capex_scaled * elect_size # $
        capex_cost = crf * CapEx # $/yr
        electricity_cost = (self.Power_Price/1000) * power_consumption # $/yr
        water_consumed = water_cons * production_m3 # liter/yr
        water_cost = water_consumed * water_price # $/yr
        non_fuel_VOM_cost = non_fuel_VOM * production_kg
        fuel_VOM = electricity_cost + water_cost
        total_charge = fuel_VOM + capex_cost + FOM_cost # $/yr
        unit_cost = total_charge / production_kg # $/kg

        Capital = (capex_cost) / production_kg
        Fixed = (FOM_cost) / production_kg
        Non_fuel_variable = (non_fuel_VOM_cost + water_cost) / production_kg
        Fuel_gas_or_power = (electricity_cost) / production_kg
        H2_transmission = transmission_cost
        CO2_transport = 0
        CO2_storage = 0

#         elif self.pt == 'SMR':
#             plant_size = self.H2_produced * 0.003 # in MW# multiply m3/hr by 0.003 to get to MW
#             Gas_Consumed = (plant_size / self.effic_SMR) * 3.41 * hours_operation  # MMBtu consumed annually;0.003 is conversion from m3/hr H2 to MW H2; 3.41 is conversion from MW NG to MMBtu/hr NG
#             if self.lca_pathway is None:
#                 Power_Produced = ( plant_size / self.effic_SMR ) * power_efficiency * hours_operation # Power produced annually
#                 fuel_VOM = ( Gas_Consumed * self.Gas_Cost ) - ( Power_Produced * self.Power_Price )
#             else:
#                 # If LCA and TEA are run together, steam is produced as a co-product by default, given the data we have
#                 ng_saved_with_steam = 0.2 # MJ NG/MJ steam
#                 Cost_Credit_for_ng_steam = self.steam * ng_saved_with_steam * self.Gas_Cost
#                 print("cost credit", Cost_Credit_for_ng_steam)
#                 fuel_VOM = (Gas_Consumed * self.Gas_Cost) - Cost_Credit_for_ng_steam
#
#             non_fuel_VOM_cost = plant_size * hours_operation * non_fuel_VOM
#             FOM_cost = ( plant_size / self.effic_SMR ) * self.fom * 1000
#             capex_scaled = (self.capex*300000*(self.H2_produced/100000)**scaling_factor)/ plant_size #$/kW
#             CapEx = capex_scaled * plant_size # $
#             capex_cost = crf * CapEx # $/yr
#             Capital = (capex_cost * Euro_USD_fx) / H2_produced_kg
#             Fixed = (FOM_cost * Euro_USD_fx) / H2_produced_kg
#             Non_fuel_variable = (non_fuel_VOM_cost * Euro_USD_fx) / H2_produced_kg
#             total_charge = (fuel_VOM + non_fuel_VOM_cost + FOM_cost + capex_cost) * Euro_USD_fx
#             Fuel_gas_or_power = (fuel_VOM * Euro_USD_fx) / H2_produced_kg
#             H2_transmission = transmission_cost
#             CO2_transport = 0
#             CO2_storage = 0
#             # print(H2_produced_kg)
#             if self.use_CCS == "Yes":
#                 ccs_costs = 0
#                 if self.lca_pathway is None:
#                     self.electricity_ci = 0.126 * 3.6 #kg/MJ * 3600 to convert to kg/kWh
#                     self.CO2_captured_dict = None
#                 else:
#                     MJ_H2_per_kg = 120
#                     for key,i in self.CO2_captured_dict.items():
#                         self.CO2_captured_dict[key] = self.CO2_captured_dict[key] * H2_produced_kg * MJ_H2_per_kg/1000 # ton CO2/year
#                 if self.storage_cost_source != 'User defined':
#                     self.storage_cost = None
#                 ccs = CcsTea(plant_type = "Hydrogen Production", plant_size = plant_size,
#                              economies_of_scale_factor = 0.6,# 0.6 is the default economy of scale factor for facilities
#                              cap_percent_plant = self.cap_percent_plant,
#                               cap_percent_regen = self.cap_percent_regen, storage_cost_source=self.storage_cost_source,
#                              storage_cost = self.storage_cost, crf = crf,
#                              gr = "US", distance =self.pipeline_miles, electricity_ci = self.electricity_ci,
#                              electricity_price = self.Power_Price, natural_gas_price= self.Gas_Cost,
#                              CO2_captured = self.CO2_captured_dict)
#
#                 avg_cost_breakdown, emissions, ccs_parasitic_load, overnight_avg_cost,fuel_consumption_per_MWh = ccs.get_capture_cost_breakdown()
#
# # Ian commented out 1/5/22
#                 # # adding CCS costs
#                 # capital_fixed['CCS - CAPEX'] = sum(avg_cost_breakdown['Capital & Fixed'].values())/H2_produced_kg
#                 # # print(capital_fixed['CCS - CAPEX'], capital_fixed['Capital'] + capital_fixed['Fixed'])
#                 # Operation_cost_breakdown['CCS - CO2 Transport Cost'] =  avg_cost_breakdown['Operational']['Transport']/H2_produced_kg
#                 # Operation_cost_breakdown['CCS - CO2 Storage Cost'] = avg_cost_breakdown['Operational'][
#                 #                                                            'Storage'] / H2_produced_kg
#                 # Operation_cost_breakdown['CCS - VOM'] = avg_cost_breakdown['Operational'][
#                 #                                                            'VOM'] / H2_produced_kg
#                 # # Operation_cost_breakdown['CCS - Tax'] = avg_cost_breakdown['Operational'][
#                 # #                                                            'Tax'] / H2_produced_kg
# # Ian added 1/5/22
#                 # adding CCS costs
#                 CCS_capital = sum(avg_cost_breakdown['Capital & Fixed'].values())/H2_produced_kg
#                 Capital = Capital + CCS_capital
#
#                 CO2_transport =  avg_cost_breakdown['Operational']['Transport']/H2_produced_kg
#                 CO2_storage = avg_cost_breakdown['Operational']['Storage'] / H2_produced_kg
#
#                 CCS_VOM = avg_cost_breakdown['Operational']['VOM'] / H2_produced_kg
#                 Non_fuel_variable = Non_fuel_variable + CCS_VOM

        #####################
        ## Cost Breakdown  ##
        #####################

        cost_breakdown = {"Capital": Capital,
                            "Fixed": Fixed,
                            "Fuel (gas or power)": Fuel_gas_or_power,
                            "Non-fuel variable": Non_fuel_variable,
                            "H2 transport": H2_transmission,
                            "CO2 transport": CO2_transport,
                            "CO2 storage": CO2_storage
                              }
        print(cost_breakdown)
        return cost_breakdown
