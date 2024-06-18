import pandas as pd
import os
from core.inputs import CategoricalInput, ContinuousInput, OptionsInput, Default
from core.tea import TeaBase
from core import validators
import core.conditionals as conditionals
from us import STATES

"""
Created on Friday Nov 27 2020

LCA + TEA for Carbon Capture, Transport and Storage - DIRECT AIR CAPTURE

@author: MITEI-SESAME MP Etcheverry (metcheve@mit.edu)
"""

PATH = os.getcwd() + "/tea/electricity/ccs/dac/"

class CcsDacTea(TeaBase):
    unit = '$/tCO2'

    @classmethod

    #for inputs conditionals see inputs relationship diagram
    def user_inputs(cls):
        return [
            CategoricalInput('tech', 'Plant Technology'),
            ContinuousInput('capacity', 'Plant Size in tCO2/year',
                            # defaults=[Default()],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(100)]),
            OptionsInput('use_user_capex_cost', 'Use User Capex Cost', options=['Yes', 'No']),
            ContinuousInput('user_capex_cost', 'Capex Cost in USD/tCO2 capacity',
                            validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                            conditionals=[conditionals.input_equal_to('use_user_capex_cost', 'Yes')]),
            OptionsInput('use_co2_free_elec', 'Use CO2 free electricity', options=['Yes', 'No']),
            OptionsInput('use_user_elec_ci', 'Use User Electricity Carbon Intensity', options=['Yes', 'No'],
                         defaults=[Default('No')],
                         conditionals=[conditionals.input_equal_to('use_co2_free_elec','No')]),
            ContinuousInput('user_elec_ci', 'Electricity Carbon Intensity in tCO2/kWh',
                            defaults=[Default(0.48)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                            conditionals=[conditionals.input_equal_to('use_user_elec_ci', 'Yes')]),
            OptionsInput('use_user_elec_price', 'Use User Electricity Price', options=['Yes', 'No'],
                         defaults=[Default('No')]),
            ContinuousInput('user_elec_price', 'Electricity Price in USD/kWh ', defaults=[Default(0.1)],
                            conditionals=[conditionals.input_equal_to('use_user_elec_price', 'Yes')]),
            OptionsInput('nat_gas_capture', 'Capture Natural Gas Emissions using Thermal Amine? (85% Capture)', options=['Yes', 'No']),
            OptionsInput('state', 'State', options=[state.abbr for state in STATES]),
            ContinuousInput('distance', '# of miles CO2 is transported by pipeline to sequestration site',
                            defaults=[Default(0)],
                            validators=[validators.numeric(), validators.gte(0)]),
            OptionsInput('use_user_storage_cost', 'Use User Storage Cost', options=['Yes', 'No']),
            ContinuousInput('user_storage_cost', 'Storage Cost in USD/tCO2 ', defaults=[Default(12)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                            conditionals=[conditionals.input_equal_to('use_user_storage_cost', 'Yes')]),
            OptionsInput('use_user_crf', 'Use User Defined CRF', options=['Yes', 'No']),
            ContinuousInput('user_crf', 'CRF in %', defaults=[Default(7)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                            conditionals=[conditionals.input_equal_to('use_user_crf', 'Yes')]),
            ContinuousInput('interest_rate', 'Interest Rate in %', defaults=[Default(5)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                            conditionals=[conditionals.input_equal_to('use_user_crf', 'No')]),
            ContinuousInput('lifetime', 'Lifetime', defaults=[Default(30)],
                            validators=[validators.integer(), validators.gte(0)],
                            conditionals=[conditionals.input_equal_to('use_user_crf', 'No')])
        ]

    # NG Carbon Intensity calculation
    def get_natgas_ci(self):
        g_in_kg = 1000
        btu_in_mj = 947.81712
        g_C_in_mol_co2 = 12.0107
        g_co2_in_mol_co2 = 44.009
        g_nat_gas_in_ft3 = 22
        btu_in_ft3 = 983
        g_C_in_nat_gas = 0.724
        natgas_ci = float(btu_in_mj / btu_in_ft3 * g_nat_gas_in_ft3 * g_C_in_nat_gas / g_C_in_mol_co2 * \
                             g_co2_in_mol_co2 / g_in_kg) #co2_kg_MJ
        return natgas_ci

    #Electricity Carbon Intensity is assumed as US Mix 0.48 kgCO2/KWh. It can also be a function if considering different electricity ci

    #Electricity consumption calculation based on dac process electricity requiremens and compression electricity requirements
    def get_elec_consumption(self):
        ref_plant = pd.read_csv(PATH + "plant_ref_data_dac.csv")
        filtered = ref_plant[ref_plant['Plant Technology'] == self.tech]
        dac_elec_consumption = float(
            filtered[filtered['Plant Technology'] == self.tech].iloc[0].dac_electricity)  # in MJ/kgCO2 captured
        comp_elec_consumption = float(
            filtered[filtered['Plant Technology'] == self.tech].iloc[0].comp_electricity)
        total_elec_consumption = dac_elec_consumption + comp_elec_consumption
        return total_elec_consumption

    #NG dac process consumption calculation based on technology requirements
    def get_natgas_dac_consumption(self): # dac
        ref_plant = pd.read_csv(PATH + "plant_ref_data_dac.csv")
        filtered = ref_plant[ref_plant['Plant Technology'] == self.tech]
        nat_gas_dac_consumption = float(
            filtered[filtered['Plant Technology'] == self.tech].iloc[0].gas)  # in MJ/kgCO2 captured from dac
        return nat_gas_dac_consumption

    # NG consumed for point source thermal amine carbon capture
    def get_natgas_ps_consumption(self): #point source
        if self.nat_gas_capture == 'Yes':
            nat_gas_ps_consumption = self.get_natgas_dac_consumption()* self.get_natgas_ci() * 0.85 * 2.95 # in MJ/kgCO2 captured from ps
            # 0.85 = capture rate
            # 2.95 = natural gas consumption in MJ per kg of CO2 captured (from table reference.csv in tea/nat gas)
        else:
            nat_gas_ps_consumption = 0
        return nat_gas_ps_consumption

    #captured CO2
    def get_co2_captured(self):
        co2_captured_dac = self.capacity #tCO2/year
        if self.nat_gas_capture == 'Yes':
            co2_captured_ps = self.get_natgas_dac_consumption()* self.get_natgas_ci() * 0.85 #tCO2/year
        else:
            co2_captured_ps =0 #tCO2/year
        total_co2_captured = co2_captured_dac + co2_captured_ps
        return co2_captured_dac, co2_captured_ps, total_co2_captured

    # TEA
    #Fuel cost calculation based on natural gas consumption and natural gas price
    def get_fuel_cost(self):
        us_prices = pd.read_csv(PATH + "us_prices.csv")
        filtered = us_prices[us_prices['state'] == self.state]
        nat_gas_price = float(filtered[filtered['state'] == self.state].iloc[0].gas)
        natgas_dac_consumption = self.get_natgas_dac_consumption() * 1000 * self.capacity # MJ/year for dac capture
        natgas_ps_consumption = self.get_natgas_ps_consumption() * 1000 *  self.capacity * (self.get_natgas_dac_consumption()* self.get_natgas_ci() * 0.85)  #MJ/year for point source capture
        total_natgas_consumption = natgas_dac_consumption + natgas_ps_consumption # MJ/year
        nat_gas_cost = total_natgas_consumption * nat_gas_price #USD/year
        fuel_consumption_and_cost = {'Nat Gas DAC Consumption in MJ/year':natgas_dac_consumption,
                                     'Nat Gas PS Consumption in MJ/year':natgas_ps_consumption,
                                     'Nat GAs Cost in USD/year': nat_gas_cost}
        return nat_gas_cost,fuel_consumption_and_cost  # in USD/year

    # Electricity cost calculation based on electricity consumption and electricity price
    def get_elec_cost(self):
        if self.use_user_elec_price == 'No':
            us_prices = pd.read_csv(PATH + "us_prices.csv")
            filtered = us_prices[us_prices['state'] == self.state]
            elec_price = float(filtered[filtered['state'] == self.state].iloc[0].electricity)  # in USD/MJ
            elec_cost = self.get_elec_consumption() * 1000 * self.capacity * elec_price  # in USD/year
        else:
            elec_cost = self.get_elec_consumption() * 1000 * self.capacity * float(self.user_elec_price)
        return elec_cost

    #Capital cost calculation
    def get_capital_cost(self):
        if self.use_user_capex_cost == 'No':
            ref_plant = pd.read_csv(PATH + "plant_ref_data_dac.csv")
            filtered = ref_plant[ref_plant['Plant Technology'] == self.tech]
            ref_capacity = float(
                filtered[filtered['Plant Technology'] == self.tech].iloc[0].refsize)  # ton/year
            ref_capex_cost = float(
                filtered[filtered['Plant Technology'] == self.tech].iloc[0].capex)
            capex_scaling_factor = self.capacity / float(ref_capacity)
            # NO ECONOMIES OF SCALE FACTOR: dac approaches benefit from the repetitive use of a single contactor geometry
            dac_ovrnght_cap_cost = float(
                ref_capex_cost * ref_capacity * capex_scaling_factor) #USD
        else:
            dac_ovrnght_cap_cost = float(
                self.user_capex_cost * self.capacity)

            # add capital cost due to ps capture (capital cost 500USD/tCO2 capacity is considered for amine thermal unit, it can be updated)
        if self.nat_gas_capture == "Yes":
            ps_overnght_cap_cost = 500 * self.get_co2_captured()[1] #USD
        else:
            ps_overnght_cap_cost = 0

        ovrnght_cap_cost = dac_ovrnght_cap_cost + ps_overnght_cap_cost #USD
        return ovrnght_cap_cost

    # Capital Recovery Factor Calculation
    def get_crf(self):
        if self.use_user_crf == 'Yes':
            crf = self.user_crf / 100
        else:
            crf = self.interest_rate / 100 * (1 + self.interest_rate / 100) ** self.lifetime / (
                    ((1 + self.interest_rate / 100) ** self.lifetime) - 1)
        return crf #dless

    # Annualized Capital Cost Calculation
    def get_ann_cap_cost(self):
        annualized_cap_cost = self.get_crf() * self.get_capital_cost()  # in USD/year
        return annualized_cap_cost

    # Fixed O&M Cost Calculation
    def get_fom_cost(self):
        ref_plant = pd.read_csv(PATH + "plant_ref_data_dac.csv")
        filtered = ref_plant[ref_plant['Plant Technology'] == self.tech]
        opex = float(
            filtered[filtered['Plant Technology'] == self.tech].iloc[0].opex)  # in MJ/kgCO2 captured
        fom_cost = self.get_capital_cost() * opex / 100  # in USD/year #add fixed cost due to ps capture
        return fom_cost

    # Variable O&M Cost Calculation based on fuel and electricity costs
    def get_vom_cost(self):
        vom_cost = self.get_fuel_cost()[0] + self.get_elec_cost()
        return vom_cost

    # Transport Cost Calculation based on distance
    def get_transport_cost(self):
        us_prices = pd.read_csv(PATH + "us_prices.csv")
        filtered = us_prices[us_prices['state'] == self.state]
        ref_transp_cost = float(filtered[filtered['state'] == self.state].iloc[0].transport)  # in USD/mile-tCO2
        transp_cost = ref_transp_cost * self.distance * self.get_co2_captured()[2]  # in USD/year
        return transp_cost

    # Storage Cost Calculation
    def get_storage_cost(self):
        if self.use_user_storage_cost == 'No':
            us_prices = pd.read_csv(PATH + "us_prices.csv")
            filtered = us_prices[us_prices['state'] == self.state]
            ref_storage_cost = float(filtered[filtered['state'] == self.state].iloc[0].storage)  # in USD/tCO2
            storage_cost = ref_storage_cost * self.get_co2_captured()[2]  # in USD/year
        else:
            storage_cost = self.user_storage_cost * self.get_co2_captured()[2]
        return storage_cost

    # Putting all together
    def get_cost_breakdown(self):
        model = {
            "Total capture, transport and storage cost in USD/tCO2":
                (
                        self.get_ann_cap_cost() + self.get_fom_cost() + self.get_vom_cost() + self.get_transport_cost() + self.get_storage_cost()) / self.get_co2_captured()[2],
            "Capital Cost in USD/tCO2": self.get_ann_cap_cost() / self.get_co2_captured()[2],
            "Fixed O&M Cost in USD/tCO2": self.get_fom_cost() / self.get_co2_captured()[2],
            "Natural Gas & Electricity Costs in USD/tCO2": self.get_vom_cost() / self.get_co2_captured()[2],
            "Transport Cost in USD/tCO2": self.get_transport_cost() / self.get_co2_captured()[2],
            "Storage Cost in USD/tCO2": self.get_storage_cost() / self.get_co2_captured()[2]
        }

        return {key: val for key, val in model.items()}
        #return model


#designvector = CcsDacLcaTea('High Temperature Aqueous Solution (HT)', #tech # HT or LT_TSA
                            #1000000, #capacity # ton/year
                            #'No', #use_user_capex_cost # Yes/No
                            #0, #user_capex_cost #in USD/tCO2 of capacity
                            #1, #economies_of_scale_factor #dless
                            #'Yes', #use_co2_free_elec # Yes/No
                            #'No', #use_user_elec_ci # Yes/No
                            #0, #user_elec_ci #kgCO2/kWh
                            #'No', #use_user_elec_price # Yes/No
                            #0, #user_elec_price #USD/MJ
                            #'No', #use_user_storage_cost # Yes/No
                            #0, #user_storage_cost #USD/tCO2
                            #'Yes', #use_user_crf # Yes/No
                            #7, #user_crf #dless (0-100)
                            #'Yes', #nat_gas_capture # Yes/No
                            #'Texas', # state
                            #200) # distance in miles


#print(designvector.get_fuel_cost()[1])
#print(designvector.get_cost_breakdown())
#print(designvector.get_emissions())
