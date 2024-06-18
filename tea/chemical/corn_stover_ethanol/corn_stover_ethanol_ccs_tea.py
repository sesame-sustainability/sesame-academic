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
        self.ethanol_production_rate = ethanol_production_rate  # MMgal/yr
        self.ferment_cap_tech = ferment_cap_tech  # compression & dehydration
        self.ferment_co2_cap_percent = ferment_co2_cap_percent  # typically 85 %
        self.boiler_cap_tech = boiler_cap_tech  # amine
        self.boiler_co2_cap_percent = boiler_co2_cap_percent  # typically 85 %
        self.amine_co2_cap_percent = amine_co2_cap_percent
        self.boilerstack_ccs = boilerstack_ccs  # Yes or No
        self.amine_regen_ccs = amine_regen_ccs  # Yes or No
        self.fuel_adj_factor = fuel_adj_factor
        self.distance = distance  # distance from source to sink in miles
        self.crf = crf  # capital recovery factor

    def get_capture_cost_breakdown(self):
        # Reading the reference and corn_ethanol_ccs csv file

        # Cost for transporting and storing CO2
        other_costs = pd.read_csv(PATH + "transport&storage costs.csv")
        ref_transport_cost = float(
            other_costs[other_costs["Generation Region"] == 'US'].iloc[0].transport)  # in USD/mile-tCO2
        ref_storage_cost = float(other_costs[other_costs["Generation Region"] == 'US'].iloc[0].storage)  # in USD/tCO2

        # Estimating the emission factor of NG
        kg_g = 1000  # 1 kg = 1000g
        btu_in_mj = 947.81712
        g_C_in_mol_co2 = 12.0107
        g_co2_in_mol_co2 = 44.009
        g_nat_gas_in_ft3 = 22
        btu_in_ft3 = 983  # LHV
        g_C_in_nat_gas = 0.724

        ng_co2_kg_MJ = btu_in_mj / btu_in_ft3 * g_nat_gas_in_ft3 * g_C_in_nat_gas / g_C_in_mol_co2 * \
                       g_co2_in_mol_co2 / kg_g  # emission factor of NG units kgCo2/MJ NG burned

        if self.boilerstack_ccs == 'No':
            ref_plant = pd.read_csv(PATH + "reference.csv")
            filtered = ref_plant[ref_plant['plant type'] == "Ethanol Production"]
            ref_plant_size = float(filtered[filtered['technology'] == self.ferment_cap_tech].iloc[
                                       0].refsize)  # MMgal/yr  #units depend on plant type

            ferment_ref_co2_captured = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].co2captured)  # tco2/year
            ferment_ref_avg_capital_cost = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].avgcapex) * 1e6  # in $USD
            ferment_fom_capex = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].fom_capex)  # in %
            ferment_elec_consumption = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].electricity)  # MJ elec/kgCo2

            flow_scaling_factor = self.ethanol_production_rate / float(ref_plant_size)
            capex_scaling_factor = float(flow_scaling_factor ** 0.6)
            ferment_capture_scaling_factor = float(self.ferment_co2_cap_percent) / 85
            ferment_overnght_avg_cap_cost = float(
                ferment_ref_avg_capital_cost * capex_scaling_factor * ferment_capture_scaling_factor)

            cap_plant_emissions = ferment_ref_co2_captured * flow_scaling_factor * ferment_capture_scaling_factor  # tCo2/year

            overnight_avg_cap_cost = ferment_overnght_avg_cap_cost  # overnight capital cost USD
            annualized_avg_cap_cost = self.crf * overnight_avg_cap_cost  # annualized capital cost USD/yr
            fom_avg_cost = overnight_avg_cap_cost * (ferment_fom_capex / 100)

            # Variable O&M cost
            power_cost = pd.read_csv(PATH + "electricity_industrial.csv")
            electricity_cost = float(power_cost[power_cost['State'] == 'US average'].iloc[0].value) * btu_in_mj * \
                               ferment_elec_consumption * 1000 * cap_plant_emissions

            nat_gas_cost = 0
            capture_vom_cost = nat_gas_cost + electricity_cost  # in USD/year
            capture_avg_cost = annualized_avg_cap_cost + fom_avg_cost + capture_vom_cost

            cap_total_emissions = cap_plant_emissions

            # Transportation & Storage Cost
            transp_cost = ref_transport_cost * self.distance * cap_plant_emissions  # in USD/year
            storage_cost = ref_storage_cost * cap_plant_emissions  # in USD/year

            capture_avg_taxes = 0.21 * (
                    capture_avg_cost + transp_cost + storage_cost)  # Federal tax rate from NPC Report 2019


        elif self.amine_regen_ccs == 'No':

            # Fermenter
            ref_plant = pd.read_csv(PATH + "reference.csv")
            filtered = ref_plant[ref_plant['plant type'] == "Ethanol Production"]
            ref_plant_size = float(filtered[filtered['technology'] == self.ferment_cap_tech].iloc[
                                       0].refsize)  # MMgal/yr  #units depend on plant type

            ferment_ref_co2_captured = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].co2captured)  # tco2/year
            ferment_ref_avg_capital_cost = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].avgcapex) * 1e6  # in $USD
            ferment_fom_capex = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].fom_capex)  # in %
            ferment_elec_consumption = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].electricity)  # MJ elec/kgCo2

            flow_scaling_factor = self.ethanol_production_rate / float(ref_plant_size)
            capex_scaling_factor = float(flow_scaling_factor ** 0.6)
            ferment_capture_scaling_factor = float(self.ferment_co2_cap_percent) / 85
            ferment_overnght_avg_cap_cost = float(
                ferment_ref_avg_capital_cost * capex_scaling_factor * ferment_capture_scaling_factor)

            # Boiler

            filtered_2 = ref_plant[ref_plant['plant type'] == "Coal Power Plants"]
            coal_ref_avg_capital_cost = float(
                filtered_2[filtered_2['technology'] == self.boiler_cap_tech].iloc[0].avgcapex) * 1e6  # $USD
            coal_ref_co2_captured = float(
                filtered_2[filtered_2['technology'] == self.boiler_cap_tech].iloc[0].co2captured)  # tco2/year
            usd_tco2_ratio = coal_ref_avg_capital_cost / coal_ref_co2_captured  # USD/tco2

            boiler_fom_capex = float(
                filtered_2[filtered_2['technology'] == self.boiler_cap_tech].iloc[0].fom_capex)  # in %
            boiler_elec_consumption = float(
                filtered_2[filtered_2['technology'] == self.boiler_cap_tech].iloc[0].electricity)  # MJ elec/kgCo2
            boiler_fuel_consumption = float(
                filtered_2[filtered_2['technology'] == self.boiler_cap_tech].iloc[0].fuel) * self.fuel_adj_factor

            boiler_ferment_ratio = 3.52  # Emission ratio of boiler to fermenter
            boiler_ref_co2_captured = (ferment_ref_co2_captured / 0.85) * boiler_ferment_ratio * 0.85  # tco2/year
            boiler_capture_scaling_factor = float(self.boiler_co2_cap_percent) / 85
            boiler_ref_avg_capital_cost = usd_tco2_ratio * boiler_ref_co2_captured

            boiler_overnight_avg_cap_cost = float(
                boiler_ref_avg_capital_cost * capex_scaling_factor * boiler_capture_scaling_factor)

            cap_plant_emissions = (ferment_ref_co2_captured * flow_scaling_factor * ferment_capture_scaling_factor) \
                                  + (boiler_ref_co2_captured * flow_scaling_factor * boiler_capture_scaling_factor)

            overnight_avg_cap_cost = ferment_overnght_avg_cap_cost + boiler_overnight_avg_cap_cost  # overnight capital cost USD

            annualized_avg_cap_cost = self.crf * overnight_avg_cap_cost  # annualized capital cost USD/yr
            fom_avg_cost = boiler_overnight_avg_cap_cost * (boiler_fom_capex / 100) \
                           + ferment_overnght_avg_cap_cost * (ferment_fom_capex / 100)

            ## Variable O&M cost
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

            # Transportation & Storage Cost
            transp_cost = ref_transport_cost * self.distance * cap_plant_emissions  # in USD/year
            storage_cost = ref_storage_cost * cap_plant_emissions  # in USD/year
            capture_avg_taxes = 0.21 * (capture_avg_cost + transp_cost + storage_cost)

            cap_total_emissions = cap_plant_emissions


        elif self.amine_regen_ccs == 'Yes':
            # Fermenter
            ref_plant = pd.read_csv(PATH + "reference.csv")
            filtered = ref_plant[ref_plant['plant type'] == "Ethanol Production"]
            ref_plant_size = float(filtered[filtered['technology'] == self.ferment_cap_tech].iloc[
                                       0].refsize)  # MMgal/yr  #units depend on plant type

            ferment_ref_co2_captured = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].co2captured)  # tco2/year
            ferment_ref_avg_capital_cost = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].avgcapex) * 1e6  # in $USD
            ferment_fom_capex = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].fom_capex)  # in %
            ferment_elec_consumption = float(
                filtered[filtered['technology'] == self.ferment_cap_tech].iloc[0].electricity)  # MJ elec/kgCo2

            flow_scaling_factor = self.ethanol_production_rate / float(ref_plant_size)
            capex_scaling_factor = float(flow_scaling_factor ** 0.6)
            ferment_capture_scaling_factor = float(self.ferment_co2_cap_percent) / 85
            ferment_overnght_avg_cap_cost = float(
                ferment_ref_avg_capital_cost * capex_scaling_factor * ferment_capture_scaling_factor)

            # Boiler

            filtered_2 = ref_plant[ref_plant['plant type'] == "Coal Power Plants"]
            coal_ref_avg_capital_cost = float(
                filtered_2[filtered_2['technology'] == self.boiler_cap_tech].iloc[0].avgcapex) * 1e6  # $USD
            coal_ref_co2_captured = float(
                filtered_2[filtered_2['technology'] == self.boiler_cap_tech].iloc[0].co2captured)  # tco2/year
            usd_tco2_ratio = coal_ref_avg_capital_cost / coal_ref_co2_captured  # USD/tco2

            boiler_fom_capex = float(
                filtered_2[filtered_2['technology'] == self.boiler_cap_tech].iloc[0].fom_capex)  # in %
            boiler_elec_consumption = float(
                filtered_2[filtered_2['technology'] == self.boiler_cap_tech].iloc[0].electricity)  # MJ elec/kgCo2
            boiler_fuel_consumption = float(
                filtered_2[filtered_2['technology'] == self.boiler_cap_tech].iloc[
                    0].fuel) * self.fuel_adj_factor  # MJ NG/kg Co2

            boiler_ferment_ratio = 3.52  # Emission ratio of boiler to fermenter
            boiler_ref_co2_captured = (
                                              ferment_ref_co2_captured / 0.85) * boiler_ferment_ratio * 0.85  # tco2/year
            boiler_capture_scaling_factor = float(self.boiler_co2_cap_percent) / 85
            boiler_ref_avg_capital_cost = usd_tco2_ratio * boiler_ref_co2_captured

            boiler_overnight_avg_cap_cost = float(
                boiler_ref_avg_capital_cost * capex_scaling_factor * boiler_capture_scaling_factor)

            # Amine Regen

            amine_capture_scaling_factor = float(self.amine_co2_cap_percent) / 85
            amine_regen_emissions = boiler_fuel_consumption * boiler_ref_co2_captured * ng_co2_kg_MJ  # Amine regeneration emissions
            amine_ref_co2_captured = amine_regen_emissions * (self.amine_co2_cap_percent / 100)

            cap_plant_emissions = (ferment_ref_co2_captured * flow_scaling_factor * ferment_capture_scaling_factor) \
                                  + (
                                          boiler_ref_co2_captured * flow_scaling_factor * boiler_capture_scaling_factor) \
                                  + (amine_ref_co2_captured * flow_scaling_factor * amine_capture_scaling_factor)

            overnight_avg_cap_cost = ferment_overnght_avg_cap_cost + boiler_overnight_avg_cap_cost  # overnight capital cost USD
            annualized_avg_cap_cost = self.crf * overnight_avg_cap_cost  # annualized capital cost USD/yr
            fom_avg_cost = boiler_overnight_avg_cap_cost * (boiler_fom_capex / 100) \
                           + ferment_overnght_avg_cap_cost * (ferment_fom_capex / 100)  # fixed O&M USD/yr

            ## Variable O&M cost
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

            # Transportation & Storage Cost
            transp_cost = ref_transport_cost * self.distance * cap_plant_emissions  # in USD/year
            storage_cost = ref_storage_cost * cap_plant_emissions  # in USD/year

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
