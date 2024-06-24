"""
Created on Wed August 4 10:00:29 2021

@author  Jon-Marc McGregor ExxonMobil Intern
"""

import pandas as pd
import os

PATH = os.getcwd() + "/tea/chemical/corn_ethanol/"


class BECCSTea:

    def __init__(self, plant_type, ethanol_production_rate, ferment_cap_tech, boiler_cap_tech, ferment_co2_cap_percent,
                 boiler_co2_cap_percent, amine_co2_cap_percent, boilerstack_ccs, amine_regen_ccs,
                 fuel_adj_factor, distance, crf):

        self.plant_type = plant_type
        self.ethanol_production_rate = ethanol_production_rate  
        self.ferment_cap_tech = ferment_cap_tech  
        self.ferment_co2_cap_percent = ferment_co2_cap_percent  
        self.boiler_cap_tech = boiler_cap_tech  
        self.boiler_co2_cap_percent = boiler_co2_cap_percent  
        self.amine_co2_cap_percent = amine_co2_cap_percent
        self.boilerstack_ccs = boilerstack_ccs  
        self.amine_regen_ccs = amine_regen_ccs  
        self.fuel_adj_factor = fuel_adj_factor
        self.distance = distance  
        self.crf = crf  

    def get_capture_cost_breakdown(self):
        other_costs = pd.read_csv(PATH + "transport&storage costs.csv")
        ref_transport_cost = float(
            other_costs[other_costs["Generation Region"] == 'US'].iloc[0].transport)  
        ref_storage_cost = float(other_costs[other_costs["Generation Region"] == 'US'].iloc[0].storage)  
        kg_g = 1000  
        btu_in_mj = 947.81712
        g_C_in_mol_co2 = 12.0107
        g_co2_in_mol_co2 = 44.009
        g_nat_gas_in_ft3 = 22
        btu_in_ft3 = 983  
        g_C_in_nat_gas = 0.724

        ng_co2_kg_MJ = btu_in_mj / btu_in_ft3 * g_nat_gas_in_ft3 * g_C_in_nat_gas / g_C_in_mol_co2 * \
                       g_co2_in_mol_co2 / kg_g  

        if self.boilerstack_ccs == 'No':
            ref_plant = pd.read_csv(PATH + "reference.csv")
            filtered = ref_plant[ref_plant['plant type'] == "Ethanol Production"]
            ref_plant_size = float(filtered[filtered['technology'] == self.ferment_cap_tech].iloc[
                                       0].refsize)  # MMgal/yr  

            ferment_ref_co2_captured = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].co2captured)  
            ferment_ref_avg_capital_cost = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].avgcapex) * 1e6  
            ferment_fom_capex = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].fom_capex)  
            ferment_elec_consumption = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].electricity)  

            flow_scaling_factor = self.ethanol_production_rate / float(ref_plant_size)
            capex_scaling_factor = float(flow_scaling_factor ** 0.6)
            ferment_capture_scaling_factor = float(self.ferment_co2_cap_percent) / 85
            ferment_overnght_avg_cap_cost = float(
                ferment_ref_avg_capital_cost * capex_scaling_factor * ferment_capture_scaling_factor)

            cap_plant_emissions = ferment_ref_co2_captured * flow_scaling_factor * ferment_capture_scaling_factor  

            overnight_avg_cap_cost = ferment_overnght_avg_cap_cost  
            annualized_avg_cap_cost = self.crf * overnight_avg_cap_cost  
            fom_avg_cost = overnight_avg_cap_cost * (ferment_fom_capex / 100)
            power_cost = pd.read_csv(PATH + "electricity_industrial.csv")
            electricity_cost = float(power_cost[power_cost['State'] == 'US average'].iloc[0].value) * btu_in_mj * \
                               ferment_elec_consumption * 1000 * cap_plant_emissions

            nat_gas_cost = 0
            capture_vom_cost = nat_gas_cost + electricity_cost  
            capture_avg_cost = annualized_avg_cap_cost + fom_avg_cost + capture_vom_cost

            cap_total_emissions = cap_plant_emissions
            transp_cost = ref_transport_cost * self.distance * cap_plant_emissions  
            storage_cost = ref_storage_cost * cap_plant_emissions  

            capture_avg_taxes = 0.21 * (
                    capture_avg_cost + transp_cost + storage_cost)  


        elif self.amine_regen_ccs == 'No':
            ref_plant = pd.read_csv(PATH + "reference.csv")
            filtered = ref_plant[ref_plant['plant type'] == "Ethanol Production"]
            ref_plant_size = float(filtered[filtered['technology'] == self.ferment_cap_tech].iloc[
                                       0].refsize)  # MMgal/yr  

            ferment_ref_co2_captured = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].co2captured)  
            ferment_ref_avg_capital_cost = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].avgcapex) * 1e6  
            ferment_fom_capex = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].fom_capex)  
            ferment_elec_consumption = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].electricity)  

            flow_scaling_factor = self.ethanol_production_rate / float(ref_plant_size)
            capex_scaling_factor = float(flow_scaling_factor ** 0.6)
            ferment_capture_scaling_factor = float(self.ferment_co2_cap_percent) / 85
            ferment_overnght_avg_cap_cost = float(
                ferment_ref_avg_capital_cost * capex_scaling_factor * ferment_capture_scaling_factor)

            filtered_2 = ref_plant[ref_plant['plant type'] == "Coal Power Plants"]
            coal_ref_avg_capital_cost = float(
                filtered_2[filtered_2['technology'] == self.boiler_cap_tech].iloc[0].avgcapex) * 1e6  
            coal_ref_co2_captured = float(
                filtered_2[filtered_2['technology'] == self.boiler_cap_tech].iloc[0].co2captured)  
            usd_tco2_ratio = coal_ref_avg_capital_cost / coal_ref_co2_captured  

            boiler_fom_capex = float(
                filtered_2[filtered_2['technology'] == self.boiler_cap_tech].iloc[0].fom_capex)  
            boiler_elec_consumption = float(
                filtered_2[filtered_2['technology'] == self.boiler_cap_tech].iloc[0].electricity)  
            boiler_fuel_consumption = float(
                filtered_2[filtered_2['technology'] == self.boiler_cap_tech].iloc[0].fuel) * self.fuel_adj_factor

            boiler_ferment_ratio = 3.52  
            boiler_ref_co2_captured = (ferment_ref_co2_captured / 0.85) * boiler_ferment_ratio * 0.85  
            boiler_capture_scaling_factor = float(self.boiler_co2_cap_percent) / 85
            boiler_ref_avg_capital_cost = usd_tco2_ratio * boiler_ref_co2_captured

            boiler_overnight_avg_cap_cost = float(
                boiler_ref_avg_capital_cost * capex_scaling_factor * boiler_capture_scaling_factor)

            cap_plant_emissions = (ferment_ref_co2_captured * flow_scaling_factor * ferment_capture_scaling_factor) \
                                  + (boiler_ref_co2_captured * flow_scaling_factor * boiler_capture_scaling_factor)

            overnight_avg_cap_cost = ferment_overnght_avg_cap_cost + boiler_overnight_avg_cap_cost  

            annualized_avg_cap_cost = self.crf * overnight_avg_cap_cost  
            fom_avg_cost = boiler_overnight_avg_cap_cost * (boiler_fom_capex / 100) \
                           + ferment_overnght_avg_cap_cost * (ferment_fom_capex / 100)
            power_cost = pd.read_csv(PATH + "electricity_industrial.csv")
            ferment_electricity_cost = float(
                power_cost[power_cost['State'] == 'US average'].iloc[0].value) * btu_in_mj * \
                                       ferment_elec_consumption * 1000 * (
                                               ferment_ref_co2_captured * flow_scaling_factor * ferment_capture_scaling_factor)

            boiler_electricity_cost = float(power_cost[power_cost['State'] == 'US average'].iloc[0].value) * btu_in_mj * \
                                      boiler_elec_consumption * 1000 * (
                                              boiler_ref_co2_captured * flow_scaling_factor * boiler_capture_scaling_factor)

            fuel_costs = pd.read_csv(PATH + "natgas_industrial.csv")
            nat_gas_cost = float(fuel_costs[fuel_costs['State'] == 'US average'].iloc[0].value) * btu_in_mj * \
                           boiler_fuel_consumption * 1000 * (
                                   boiler_ref_co2_captured * flow_scaling_factor * boiler_capture_scaling_factor)

            capture_vom_cost = ferment_electricity_cost + boiler_electricity_cost + nat_gas_cost

            capture_avg_cost = annualized_avg_cap_cost + fom_avg_cost + capture_vom_cost
            transp_cost = ref_transport_cost * self.distance * cap_plant_emissions  
            storage_cost = ref_storage_cost * cap_plant_emissions  
            capture_avg_taxes = 0.21 * (capture_avg_cost + transp_cost + storage_cost)

            cap_total_emissions = cap_plant_emissions


        elif self.amine_regen_ccs == 'Yes':
            ref_plant = pd.read_csv(PATH + "reference.csv")
            filtered = ref_plant[ref_plant['plant type'] == "Ethanol Production"]
            ref_plant_size = float(filtered[filtered['technology'] == self.ferment_cap_tech].iloc[
                                       0].refsize)  # MMgal/yr  

            ferment_ref_co2_captured = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].co2captured)  
            ferment_ref_avg_capital_cost = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].avgcapex) * 1e6  
            ferment_fom_capex = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].fom_capex)  
            ferment_elec_consumption = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].electricity)  

            flow_scaling_factor = self.ethanol_production_rate / float(ref_plant_size)
            capex_scaling_factor = float(flow_scaling_factor ** 0.6)
            ferment_capture_scaling_factor = float(self.ferment_co2_cap_percent) / 85
            ferment_overnght_avg_cap_cost = float(
                ferment_ref_avg_capital_cost * capex_scaling_factor * ferment_capture_scaling_factor)

            filtered_2 = ref_plant[ref_plant['plant type'] == "Coal Power Plants"]
            coal_ref_avg_capital_cost = float(
                filtered_2[filtered_2['technology'] == self.boiler_cap_tech].iloc[0].avgcapex) * 1e6  
            coal_ref_co2_captured = float(
                filtered_2[filtered_2['technology'] == self.boiler_cap_tech].iloc[0].co2captured)  
            usd_tco2_ratio = coal_ref_avg_capital_cost / coal_ref_co2_captured  

            boiler_fom_capex = float(
                filtered_2[filtered_2['technology'] == self.boiler_cap_tech].iloc[0].fom_capex)  
            boiler_elec_consumption = float(
                filtered_2[filtered_2['technology'] == self.boiler_cap_tech].iloc[0].electricity)  
            boiler_fuel_consumption = float(
                filtered_2[filtered_2['technology'] == self.boiler_cap_tech].iloc[
                    0].fuel) * self.fuel_adj_factor  

            boiler_ferment_ratio = 3.52  
            boiler_ref_co2_captured = (
                                              ferment_ref_co2_captured / 0.85) * boiler_ferment_ratio * 0.85  
            boiler_capture_scaling_factor = float(self.boiler_co2_cap_percent) / 85
            boiler_ref_avg_capital_cost = usd_tco2_ratio * boiler_ref_co2_captured

            boiler_overnight_avg_cap_cost = float(
                boiler_ref_avg_capital_cost * capex_scaling_factor * boiler_capture_scaling_factor)

            amine_capture_scaling_factor = float(self.amine_co2_cap_percent) / 85
            amine_regen_emissions = boiler_fuel_consumption * boiler_ref_co2_captured * ng_co2_kg_MJ  
            amine_ref_co2_captured = amine_regen_emissions * (self.amine_co2_cap_percent / 100)

            cap_plant_emissions = (ferment_ref_co2_captured * flow_scaling_factor * ferment_capture_scaling_factor) \
                                  + (
                                          boiler_ref_co2_captured * flow_scaling_factor * boiler_capture_scaling_factor) \
                                  + (amine_ref_co2_captured * flow_scaling_factor * amine_capture_scaling_factor)

            overnight_avg_cap_cost = ferment_overnght_avg_cap_cost + boiler_overnight_avg_cap_cost  
            annualized_avg_cap_cost = self.crf * overnight_avg_cap_cost  
            fom_avg_cost = boiler_overnight_avg_cap_cost * (boiler_fom_capex / 100) \
                           + ferment_overnght_avg_cap_cost * (ferment_fom_capex / 100)  
            power_cost = pd.read_csv(PATH + "electricity_industrial.csv")
            ferment_electricity_cost = float(
                power_cost[power_cost['State'] == 'US average'].iloc[0].value) * btu_in_mj * \
                                       ferment_elec_consumption * 1000 * (
                                               ferment_ref_co2_captured * flow_scaling_factor * ferment_capture_scaling_factor)

            boiler_total_ref_captured = (boiler_ref_co2_captured * flow_scaling_factor * boiler_capture_scaling_factor) \
                                        + (amine_ref_co2_captured * flow_scaling_factor * amine_capture_scaling_factor)

            boiler_electricity_cost = float(power_cost[power_cost['State'] == 'US average'].iloc[0].value) * btu_in_mj * \
                                      boiler_elec_consumption * 1000 * boiler_total_ref_captured

            fuel_costs = pd.read_csv(PATH + "natgas_industrial.csv")
            nat_gas_cost = float(fuel_costs[fuel_costs['State'] == 'US average'].iloc[0].value) * btu_in_mj * \
                           boiler_fuel_consumption * 1000 * boiler_total_ref_captured

            capture_vom_cost = ferment_electricity_cost + boiler_electricity_cost + nat_gas_cost

            capture_avg_cost = annualized_avg_cap_cost + fom_avg_cost + capture_vom_cost
            transp_cost = ref_transport_cost * self.distance * cap_plant_emissions  
            storage_cost = ref_storage_cost * cap_plant_emissions  

            capture_avg_taxes = 0.21 * (capture_avg_cost + transp_cost + storage_cost)

            cap_total_emissions = cap_plant_emissions

        ccs_cost_breakdown = {
            "Total AVG capture, transport and storage cost in USD/tCO2":
                (
                        annualized_avg_cap_cost + fom_avg_cost + capture_vom_cost + capture_avg_taxes + transp_cost + storage_cost) / cap_total_emissions,

            "AVG Capital Cost in USD/tCO2": annualized_avg_cap_cost / cap_total_emissions,
            "AVG Fixed O&M Cost in USD/tCO2": fom_avg_cost / cap_total_emissions,
            "Natural Gas & Electricity Costs in USD/tCO2": (capture_vom_cost / cap_total_emissions),
            "AVG Capture Taxes in USD/CO2": capture_avg_taxes / cap_total_emissions,
            "Transport Cost in USD/tCO2": transp_cost / cap_total_emissions,
            "Storage Cost in USD/tCO2": storage_cost / cap_total_emissions
        }

        return ccs_cost_breakdown, annualized_avg_cap_cost, fom_avg_cost, capture_vom_cost, capture_avg_taxes, transp_cost, storage_cost
