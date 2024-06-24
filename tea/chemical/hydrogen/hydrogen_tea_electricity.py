

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
        ]

        tea_only_inputs2 = [
            ContinuousInput(
                'effic', 'Hydrogen Production Efficiency',
                unit='kWh/kg_H\u2082',
                defaults=[Default(57.2)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
            ),
            OptionsInput(
                'state', 'Hydrogen Phase',
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
            },
            'capex': {
                'Alk': 1214,
                'PEM': 1771,
            },
            'fom': {
                'Alk': 55,
                'PEM': 75,
            },
            'scaling_factor': {
                'Alk': 0.75, 
                'PEM': 0.75,
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
        ]
        if tea_lca and prod_type == 'SMR':
            for input in tea_lca_inputs:
                if input.name in tea_lca_defaults:
                    input.defaults.append(Default(tea_lca_defaults[input.name][prod_type]))
        else:
            for input in tea_lca_inputs:
                if input.name in tea_lca_defaults:
                    for pt, default in tea_lca_defaults[input.name].items():
                        input.defaults.append(Default(default, conditionals=[conditionals.input_equal_to('pt', pt)]))
        tea_inputs2 = [
            ContinuousInput(
                'Power_Price','Power Price ($/MWh)',
                defaults=[Default(80)], 
                validators=[validators.numeric(), validators.gte(0), validators.lte(1000)],
            ),
        ]

        if tea_lca:
            return [
                OptionsInput(
                    'pt', 'Production Type',
                    options=['Alk', 'PEM'],
                    defaults=[Default('PEM')],
                ),
            ] + tea_lca_inputs + tea_inputs2
        else:
            return tea_only_inputs1 + tea_only_inputs2 + tea_lca_inputs + tea_inputs2 + CcsTea.user_inputs(source='Hydrogen Production')
    @classmethod
    def sensitivity(cls, lca_pathway=None):
        source_ids = []
        if lca_pathway is not None:
            source_ids = [step.source.id for step in lca_pathway.steps]

        sensitivity_inputs = [
            SensitivityInput('pt', minimizing='Alk', maximizing='PEM'),
            SensitivityInput('effic', data_lacking=True),
            SensitivityInput('distance', data_lacking=True),
            SensitivityInput('H2_produced', data_lacking=True),
            SensitivityInput('capex', data_lacking=True),
            SensitivityInput('fom', data_lacking=True),
            SensitivityInput('capacity_factor', minimizing=100,maximizing=.7*90),
            SensitivityInput('scaling_factor', data_lacking=True),
            SensitivityInput('discount_rate', data_lacking=True),
            SensitivityInput('lifetime', data_lacking=True),
            SensitivityInput('Power_Price', data_lacking=True),
            SensitivityInput('state', minimizing='Gas', maximizing='Liquid'),
        ]

        return sensitivity_inputs

    def __init__(self, lca_pathway=None):
        self.lca_pathway = lca_pathway
        self.h2_production_param = pd.read_csv(PATH + "hydrogen_production_tech.csv")
        super().__init__(lca_pathway)

    def prepare(self, input_set):
        super().prepare(input_set)

        if self.lca_pathway is not None:
            inputs = type(self).user_inputs()
            stage = self.lca_pathway.instance('process')
            stage2 = self.lca_pathway.instance('gatetoenduse')
            flow_dict = stage.get_inputs()
            stage.pt = pt  
            if stage.pt == 'SMR':
                elec = flow_dict['secondary']['electricity']['value']
            else:
                elec = flow_dict['primary']['value'] 
            for input in inputs:
                if hasattr(stage, input.name):
                    value = getattr(stage, input.name)
                    setattr(self, input.name, value)
                else:
                    setattr(self, input.name, input_set.default_value(input.name))
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

                if stage.co_produce_steam == 'Yes': 
                    self.steam = flow_dict['secondary']['steam co-generated']['value'] * -1
                else:
                    self.steam = 0
            else:
                MJ_H2_per_kg = 120 # source : https://www.energy.gov/eere/fuelcells/hydrogen-storage
                self.effic = elec * 0.277778 * MJ_H2_per_kg 
            self.distance = stage2.distance


    def get_production_type(self):
        if self.lca_pathway:
            process_user_inputs = self.lca_pathway['Process']['user_inputs']
            prod_type = process_user_inputs.get("Production Type")
        else:
            prod_type = self.pt
        return prod_type

    def get_cost_breakdown(self):
        prod_type = self.pt

        if prod_type == 'Alk':
            index = 0
        elif prod_type == 'PEM':
            index = 1
        else:
            index = 2


        self.capacity_factor = self.capacity_factor/100
        self.discount_rate = self.discount_rate/100
        water_cons = self.h2_production_param.iloc[index, 4]
        power_efficiency = self.h2_production_param.iloc[index, 6]
        non_fuel_VOM = self.h2_production_param.iloc[index, 7]
        H2_density = 0.091 
        water_price = 0.0017 
        scaling_factor = self.scaling_factor
        Euro_USD_fx = 1.2
        miles_to_km = 1.60934
        liquefaction_cost = 1 
        barge_cost = 0.001 
        truck_cost = 0.0016 
        liquid_TD_cost = liquefaction_cost + 1*self.distance*barge_cost + 1*30*truck_cost 
        if self.state == 'Gas':
            self.distance = self.distance * miles_to_km
            transmission_cost = self.distance/1500 
        else:
            transmission_cost = liquid_TD_cost 

        hours_operation = 8760 * self.capacity_factor 
        H2_produced_kg = self.H2_produced * H2_density * hours_operation

        crf = (self.discount_rate * ((1 + self.discount_rate) ** self.lifetime)) / (
                    (1 + self.discount_rate) ** (self.lifetime) - 1)  
        production_m3 = hours_operation * self.H2_produced  
        production_kg = production_m3 * H2_density  
        power_consumption = (self.effic/11) * production_m3 
        elect_size = power_consumption / hours_operation 
        FOM_cost = elect_size * self.fom 

        if prod_type == 'Alk':
            capex_scaled = ((300 * self.capex) * (elect_size / 300)**scaling_factor)/elect_size
        else:
            capex_scaled = ((1500 * self.capex) * (elect_size / 1500) ** scaling_factor) / elect_size

        CapEx = capex_scaled * elect_size 
        capex_cost = crf * CapEx 
        electricity_cost = (self.Power_Price/1000) * power_consumption 
        water_consumed = water_cons * production_m3 
        water_cost = water_consumed * water_price 
        non_fuel_VOM_cost = non_fuel_VOM * production_kg
        fuel_VOM = electricity_cost + water_cost
        total_charge = fuel_VOM + capex_cost + FOM_cost 
        unit_cost = total_charge / production_kg 

        Capital = (capex_cost) / production_kg
        Fixed = (FOM_cost) / production_kg
        Non_fuel_variable = (non_fuel_VOM_cost + water_cost) / production_kg
        Fuel_gas_or_power = (electricity_cost) / production_kg
        H2_transmission = transmission_cost
        CO2_transport = 0
        CO2_storage = 0

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
