"""
Created on Friday August 13 10:06:47 2021

Author : Jon-Marc McGregor - ExxonMobil CSR Intern"""

from core.pathway import ActivitySource
from core.inputs import ContinuousInput, CategoricalInput, OptionsInput, Default, Tooltip
from analysis.lca import compute_input_flows, compute_emission_flows
import core.validators as validators
import core.conditionals as conditionals
from pathway.enduse.substance import Substance
from core import utils
import sys
import pandas as pd
import os

PATH = os.getcwd() + '/pathway/process/biofuel/'


class CornEthanolProduction(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
            CategoricalInput(
                'natural_gas_and_power_emissions_model', 'Natural Gas & Power Emissions Model',
                defaults=[Default('average of 88 corn ethanol biorefineries (EPA)')],
                tooltip=Tooltip(
                    'Natural gas and power consumption in the biorefining process vary depending on the model selected here. Consumptions of the other materials such as NaOH, H2SO4, ammonia are calcualted using the AECOM model. For the average 88 model, see the 88 links to the referenced biorefineries in the 3a.EPA data on biorefineries tab in the original excel model in SESAME backend folder: pathway/process/corn ethanol folder. For the AECOM model results, see 3b.Biorefinery (AECOM) tab. Also note that the corn ethanol pathway does not include biogenic carbon accounting, due to the offset (carbon neutral) effect, to be consistent with the original excel model',
                    source='EPA',
                ),
            ),
            OptionsInput('use_ccs', 'Use CCS (Carbon Capture & Sequester)', options=['Yes', 'No']),
            OptionsInput('ferment_ccs', 'Capture CO\u2082 from Fermenter ?', options=['Yes'],
                         conditionals=[conditionals.input_equal_to('use_ccs', 'Yes')]),
            OptionsInput('ferment_cap_tech', 'CCS Technology', options=['compression + dehydration'],
                         conditionals=[conditionals.input_equal_to('use_ccs', 'Yes'),
                                       conditionals.input_equal_to('ferment_ccs', 'Yes')]),
            ContinuousInput('ferment_co2_cap_percent', 'CO\u2082 Captured from Fermenter (%)',
                            defaults=[Default(85)],
                            validators=[validators.numeric(), validators.gte(0), validators.lt(100)],
                            conditionals=[conditionals.input_equal_to('ferment_ccs', 'Yes')]),

            OptionsInput('boilerstack_ccs', 'Capture CO\u2082 from Boilerstack ?', options=['Yes', 'No'],
                         conditionals=[conditionals.input_equal_to('ferment_ccs', 'Yes')]),
            OptionsInput('boiler_cap_tech', 'CCS Technology', options=['amine'],
                         conditionals=[conditionals.input_equal_to('boilerstack_ccs', 'Yes')]),
            ContinuousInput('boiler_co2_cap_percent', 'CO\u2082 Captured from Boilerstack (%)',
                            defaults=[Default(85)],
                            validators=[validators.numeric(), validators.gte(0), validators.lt(100)],
                            conditionals=[conditionals.input_equal_to('boilerstack_ccs', 'Yes')]),
            OptionsInput('amine_regen_ccs', 'Capture CO\u2082 from Amine Regeneration ?', options=['Yes', 'No'],
                         conditionals=[conditionals.input_equal_to('boilerstack_ccs', 'Yes')]),
            ContinuousInput('amine_co2_cap_percent', 'CO\u2082 Captured from Amine Regeneration (%)',
                            defaults=[Default(85)],
                            validators=[validators.numeric(), validators.gte(0), validators.lt(100)],
                            conditionals=[conditionals.input_equal_to('amine_regen_ccs', 'Yes')]),

            ContinuousInput('fuel_adj_factor', 'Adjustment Factor for Natural Gas Needed for Amine Regeneration '
                                               '(e.g 1 ~ assumes the value of 2.95,MJ/kg CO2, 1.3 assumes a 30% '
                                               'increase) ',
                            defaults=[Default(1)],
                            validators=[validators.numeric(), validators.gte(1), validators.lte(1.9)],
                            conditionals=[conditionals.input_equal_to('boilerstack_ccs', 'Yes')]),

            ContinuousInput('user_electric_ci', 'Lifecycle Emissions of Compression Power (gCO\u2082/kWh)',
                            defaults=[Default(460)],  
                            validators=[validators.numeric(), validators.gte(0)],
                            conditionals=[conditionals.input_equal_to('use_ccs', 'Yes')]),
            ContinuousInput('pipeline_miles', 'Pipeline Distance from Capture to Sequester (mi)',
                            unit='mi',
                            defaults=[Default(240)],
                            validators=[validators.numeric(), validators.gte(0)],
                            conditionals=[conditionals.input_equal_to('use_ccs', 'Yes')],
                            tooltip=Tooltip(
                                'The distance could vary significantly by projects. 240 mi roughly translates to ~ 20 $/T CO2 for transportation and sequestration, assuming storage costs 8 $/T CO2, and transportation costs 0.05 $/T CO2/mi.',
                                source='NPC 2020',
                                source_link='https://dualchallenge.npc.org/files/CCUS-Chap_2-060520.pdf',
                            )),

        ]

    def get_inputs(self):
        flow_dict = compute_input_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )

        return {
            'primary': flow_dict['corn'],
            'secondary': []
        }

    def get_emissions(self):
        emissions = compute_emission_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )
        ferment_co2 = emissions.get("Fermentation")
        ferment_co2 = ferment_co2.get("fermenter vent biogenic co2")
        ferment_co2 = ferment_co2.get("value")  
        stack_co2 = emissions.get("Carbon footprint of NG & power")
        stack_co2 = stack_co2.get("co2")
        stack_co2 = stack_co2.get("value")  

        if self.use_ccs == 'No':
            print('Fermenter emission value:(gCO2e) ', ferment_co2 * 1000)  
            CCS_value = 0
            emissions["CCS"] = {'co2': {'name': 'co2', 'unit': 'kg', 'value': CCS_value}}

            return emissions
        kwh_mj = 3.6  
        kg_g = 1000  
        btu_in_mj = 947.81712
        g_C_in_mol_co2 = 12.0107
        g_co2_in_mol_co2 = 44.009
        g_nat_gas_in_ft3 = 22
        btu_in_ft3 = 983  
        g_C_in_nat_gas = 0.724

        elec_ci_compression = self.user_electric_ci /1000 / kwh_mj  # User Defined Electricity CI  

        ng_co2_kg_MJ = btu_in_mj / btu_in_ft3 * g_nat_gas_in_ft3 * g_C_in_nat_gas / g_C_in_mol_co2 * \
                       g_co2_in_mol_co2 / kg_g  
        co2_transportation = pd.read_csv(PATH[:-len("process/biofuel/")] + "gate_to_enduse/transportation_lcidata"
                                                                           ".csv")
        transport_emission = co2_transportation[co2_transportation['Feed'] == "co2"]
        transport_emission = transport_emission.get("value")
        total_kg_kg_mil = transport_emission.iloc[0] + transport_emission.iloc[1] + transport_emission.iloc[2] + \
                          transport_emission.iloc[3] + transport_emission.iloc[4] + transport_emission.iloc[5] + \
                          transport_emission.iloc[6] + transport_emission.iloc[7] + transport_emission.iloc[8] + \
                          transport_emission.iloc[9] + transport_emission.iloc[10]

        CCS_value = 0
        if self.boilerstack_ccs == 'No':
            CCS_inputs = pd.read_csv(PATH + 'corn_ethanol_nobiogen_ccs_lcidata.csv')

            for i in CCS_inputs.values:
                ferment_electric_ccs = CCS_inputs.get("value").iloc[0]  

            ferment_co2_cap = (ferment_co2 * (
                    self.ferment_co2_cap_percent / 100))  

            boiler_co2_cap = 0  
            co2_cap = ferment_co2_cap + boiler_co2_cap
            compress_dehy_emission = (
                    ferment_electric_ccs * co2_cap * elec_ci_compression)  

            pipeline_emissions = (total_kg_kg_mil * self.pipeline_miles * co2_cap)
            CCS_value = (-co2_cap + compress_dehy_emission + pipeline_emissions)

            print('The Fermenter CO2 emission (gCo2e):', ferment_co2 * kg_g)
            print('Mass amount of co2 captured (gCo2e):', co2_cap * kg_g)
            print('Emissions due to compression & dehydration:(gCo2e)', compress_dehy_emission * kg_g)
            print('Pipeline Emissions : (gCO2e)', pipeline_emissions * kg_g)

        elif self.amine_regen_ccs == 'No':
            CCS_inputs = pd.read_csv(PATH + 'corn_ethanol_nobiogen_ccs_lcidata.csv')
            for i in CCS_inputs:
                ferment_electric_ccs = CCS_inputs.get("value").iloc[0]  
                boiler_electric_ccs = CCS_inputs.get("value").iloc[1]  
                nat_gas_ccs = CCS_inputs.get("value").iloc[
                                  2] * self.fuel_adj_factor  
            ferment_co2_cap = (ferment_co2 * (
                    self.ferment_co2_cap_percent / 100))  
            compress_dehy_emission = ferment_electric_ccs * ferment_co2_cap * elec_ci_compression
            boiler_co2_cap = stack_co2 * (self.boiler_co2_cap_percent / 100)
            compression_emission = boiler_electric_ccs * boiler_co2_cap * elec_ci_compression  
            amine_emission = nat_gas_ccs * boiler_co2_cap * ng_co2_kg_MJ

            co2_cap = ferment_co2_cap + boiler_co2_cap  

            boiler_pipeline_emission = (
                    total_kg_kg_mil * self.pipeline_miles * boiler_co2_cap)  
            ferment_pipeline_emission = (total_kg_kg_mil * self.pipeline_miles * ferment_co2_cap)

            CCS_value = (-ferment_co2_cap + compress_dehy_emission + ferment_pipeline_emission) + (
                    -boiler_co2_cap + compression_emission + amine_emission + boiler_pipeline_emission)

            print('The boiler stack emissions : (gCo2e)', stack_co2 * kg_g)
            print('Mass amount of Co2 captured from boilerstack : (gCo2e)', boiler_co2_cap * kg_g)
            print('The Fermenter Co2 emissions :(gCo2e)', ferment_co2 * kg_g)
            print('Mass amount of co2 captured from fermenter (gCo2e) :', ferment_co2_cap * kg_g)
            print('The total amount of Co2 captured :(gCo2e) ', co2_cap * kg_g)

            print('Emissions due to compression & dehydration:(gCo2e)', compress_dehy_emission * kg_g)
            print('Emissions due to compression only :(gCo2e) ', compression_emission * kg_g)
            print('Emissions due to amine regeneration : (gCo2e)', amine_emission * kg_g)
            print('Boiler pipeline emissions', boiler_pipeline_emission * kg_g)
            print('Ferment pipeline emissions', ferment_pipeline_emission * kg_g)


        elif self.amine_regen_ccs == 'Yes':
            CCS_inputs = pd.read_csv(PATH + 'corn_ethanol_nobiogen_ccs_lcidata.csv')
            for i in CCS_inputs:
                ferment_electric_ccs = CCS_inputs.get("value").iloc[0]  
                boiler_electric_ccs = CCS_inputs.get("value").iloc[1]  
                nat_gas_ccs = CCS_inputs.get("value").iloc[2] * self.fuel_adj_factor  
            ferment_co2_cap = (ferment_co2 * (
                    self.ferment_co2_cap_percent / 100))  
            compress_dehy_emission = ferment_electric_ccs * ferment_co2_cap * elec_ci_compression  
            ferment_pipeline_emission = total_kg_kg_mil * self.pipeline_miles * ferment_co2_cap
            boiler_co2_cap = stack_co2 * (self.boiler_co2_cap_percent / 100)
            amine_regen_emissions = nat_gas_ccs * boiler_co2_cap * ng_co2_kg_MJ  
            amine_co2_cap = (self.amine_co2_cap_percent / 100) * amine_regen_emissions  
            new_amine_emission = amine_regen_emissions - amine_co2_cap  

            compression_emission = boiler_electric_ccs * elec_ci_compression * (boiler_co2_cap + amine_co2_cap)

            boiler_pipeline_emission = total_kg_kg_mil * self.pipeline_miles * (boiler_co2_cap + amine_co2_cap)

            CCS_value = (-ferment_co2_cap + compress_dehy_emission + ferment_pipeline_emission) \
                        + (-boiler_co2_cap + compression_emission + boiler_pipeline_emission) + (
                                    -amine_co2_cap + new_amine_emission)

            print('The boiler stack emissions : (gCo2e)', stack_co2 * kg_g)
            print('Mass amount of Co2 captured from boilerstack : (gCo2e)', boiler_co2_cap * kg_g)
            print('The Fermenter Co2 emissions :(gCo2e)', ferment_co2 * kg_g)
            print('Mass amount of co2 captured from fermenter (gCo2e) :', ferment_co2_cap * kg_g)

            print('Emissions due to compression & dehydration:(gCo2e)', compress_dehy_emission * kg_g)
            print('Emissions due to compression only :(gCo2e) ', compression_emission * kg_g)
            print('Emissions due to amine regeneration : (gCo2e)', amine_regen_emissions * kg_g)
            print('Mass amount captured from amine reg: (gCo2e)', amine_co2_cap * kg_g)
            print('Emissions due to amine regeneration with CCS', new_amine_emission * kg_g)

            print('')
            print('Boiler pipeline emissions', boiler_pipeline_emission * kg_g)
            print('Ferment pipeline emissions', ferment_pipeline_emission * kg_g)

        emissions["CCS"] = {
            'co2': {'name': 'co2', 'unit': 'kg', 'value': CCS_value}}  

        return emissions
