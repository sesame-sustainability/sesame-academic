"""
Created on Friday August 13, 2021

Author : Jon-Marc McGregor - ExxonMobil CSR Intern (jon-marc.mcgregor@utexas.edu)"""

from core.pathway import ActivitySource
from core.inputs import ContinuousInput, CategoricalInput, OptionsInput, Default, Tooltip
import core.conditionals as  conditionals
from analysis.lca import compute_input_flows, compute_emission_flows
import core.validators as validators
import sys
import pandas as pd
import os

PATH = os.getcwd() + '/pathway/process/biofuel/'


class StoverEthanolProduction(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [

            # CategoricalInput('natural_gas_and_power_emissions_model', 'Natural Gas & Power Emissions Model'),
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
            OptionsInput('boiler_cap_tech', 'CCS Technology', options=['amine absorption'],
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
                            validators=[validators.numeric(), validators.gte(1), validators.lte(1.7)],
                            # A 70% increase is an extreme upper boundary, 20-30% increase is reasonable
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
            'primary': flow_dict['stover'],
            #            'secondary': [flow_dict[key] for key in flow_dict if key != 'natural gas']
            'secondary': []
        }

    # get_emission function CCS Variables and their units
    # ferment_co2, kgCo2e
    # electric_ci_compression , kg/MJ
    # co2_cap, kgCo2e
    # new_ferment_emissions, kgCo2e
    # chemical_co2, kgCo2e
    # stack_co2 , kgCo2e
    # total_kg_kg_mil, kg/kg mil
    # pipeline_emissions , kgCo2e
    # overall_emissions_ccs,kgCo2e

    def get_emissions(self):
        emissions = compute_emission_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )

        if self.use_ccs == 'Yes':
            print('What is in this dictionary', emissions)

        # Section 1 : Gathering emissiosn value from the point sources for cornstover EtOH process

        # point source :ferment vent
        ferment_co2 = emissions.get("Fermenter vent")
        ferment_co2 = ferment_co2.get("co2")
        ferment_co2 = ferment_co2.get("value")  # This is the emission value from ferment vent

        # point source : Boiler stack
        stack_co2 = emissions.get("Boiler stack")
        stack_co2 = stack_co2.get("co2")
        stack_co2 = stack_co2.get("value")  # This is the emission value from boilerstack

        if self.use_ccs == 'No':
            return emissions

        # Section 2 : LCA calculations for emissions capture from fermenter vent

        # Conversion factors
        kwh_mj = 3.6
        kg_g = 1000
        btu_in_mj = 947.81712
        g_C_in_mol_co2 = 12.0107
        g_co2_in_mol_co2 = 44.009
        g_nat_gas_in_ft3 = 22
        btu_in_ft3 = 983  # LHV
        g_C_in_nat_gas = 0.724
        elec_ci_compression = self.user_electric_ci /1000 / kwh_mj  # User Defined Electricity CI converted to #units: kgCo2/MJ

        ng_co2_kg_MJ = btu_in_mj / btu_in_ft3 * g_nat_gas_in_ft3 * g_C_in_nat_gas / g_C_in_mol_co2 * \
                       g_co2_in_mol_co2 / kg_g  # emission factor of NG

        # Modeling the co2 emission related to pipeline transportation of captured co2
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

            # Reading csv file and extracting the energy usage value for compression & dehydration
            CCS_inputs = pd.read_csv(PATH + 'stover_ethanol_withbiogen_ccs_lcidata.csv')

            for i in CCS_inputs.values:
                ferment_electric_ccs = CCS_inputs.get("value").iloc[0]  # indexing to locate the data value in csv file

            ferment_co2_cap = (ferment_co2 * (
                    self.ferment_co2_cap_percent / 100))  # Calculating co2 emissions captured from fermenter vent

            co2_cap = ferment_co2_cap
            compress_dehy_emission = (
                    ferment_electric_ccs * co2_cap * elec_ci_compression)  # calculating emission from compression & dehydration step

            # new_ferment_emission = (ferment_co2 - co2_cap) + compress_dehy_emission  # kgCo2e

            pipeline_emissions = (total_kg_kg_mil * self.pipeline_miles * co2_cap)
            # overall_emissions_ccs = pipeline_emissions + new_ferment_emission

            CCS_value = (-co2_cap + compress_dehy_emission + pipeline_emissions)
            print('The Fermenter CO2 emission (gCo2e):', ferment_co2 * kg_g)
            print('Mass amount of co2 captured (gCo2e):', co2_cap * kg_g)
            print('Emissions due to compression & dehydration:(gCo2e)', compress_dehy_emission * kg_g)
            print('Pipeline Emissions : (gCO2e)', pipeline_emissions * kg_g)

        # Model for capturing Co2 from boiler stack and fermenter

        elif self.amine_regen_ccs == 'No':
            CCS_inputs = pd.read_csv(PATH + 'stover_ethanol_withbiogen_ccs_lcidata.csv')
            for i in CCS_inputs:
                ferment_electric_ccs = CCS_inputs.get("value").iloc[0]  # MJ elec/kgCO2
                boiler_electric_ccs = CCS_inputs.get("value").iloc[1]  # MJ elec/kgCO2
                nat_gas_ccs = CCS_inputs.get("value").iloc[2] * self.fuel_adj_factor  # MJ NG/kgCO2

            # Calculating new ferment emissions
            ferment_co2_cap = (ferment_co2 * (
                    self.ferment_co2_cap_percent / 100))  # Calculating co2 emissions captured from fermenter vent
            compress_dehy_emission = ferment_electric_ccs * ferment_co2_cap * elec_ci_compression  # z stream
            #new_ferment_emission = (ferment_co2 - ferment_co2_cap) + compress_dehy_emission  # kgCo2e

            # Calculating new boiler emissions w/o amine regeneration CCS
            boiler_co2_cap = stack_co2 * (self.boiler_co2_cap_percent / 100)
            compression_emission = boiler_electric_ccs * boiler_co2_cap * elec_ci_compression  # c stream
            amine_emission = nat_gas_ccs * boiler_co2_cap * ng_co2_kg_MJ

            # new_boiler_emissions = (stack_co2 - boiler_co2_cap) + c + b
            co2_cap = ferment_co2_cap + boiler_co2_cap  # kgco2e

            boiler_pipeline_emission = (
                    total_kg_kg_mil * self.pipeline_miles * boiler_co2_cap)  # pipeline emission with just co2 captured from boilerstack
            ferment_pipeline_emission = (total_kg_kg_mil * self.pipeline_miles * ferment_co2_cap)

            # pipeline_emissions = (total_kg_kg_mil * self.pipeline_miles * co2_cap)  # total pipeline emission with captured co2 from fermenter and boilerstack
            # total_emission_ccs = new_ferment_emission + new_boiler_emissions + pipeline_emissions

            CCS_value = (-ferment_co2_cap + compress_dehy_emission + ferment_pipeline_emission) + \
                        (-boiler_co2_cap + compression_emission + amine_emission + boiler_pipeline_emission)

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
            CCS_inputs = pd.read_csv(PATH + 'stover_ethanol_withbiogen_ccs_lcidata.csv')
            for i in CCS_inputs:
                ferment_electric_ccs = CCS_inputs.get("value").iloc[0]  # MJ elec/kgCO2
                boiler_electric_ccs = CCS_inputs.get("value").iloc[1]  # MJ elec/kgCO2
                nat_gas_ccs = CCS_inputs.get("value").iloc[2] * self.fuel_adj_factor  # MJ NG/kgCO2

            # Calculating new ferment emissions
            ferment_co2_cap = (ferment_co2 * (
                    self.ferment_co2_cap_percent / 100))  # Calculating co2 emissions captured from fermenter vent
            compress_dehy_emission = ferment_electric_ccs * ferment_co2_cap * elec_ci_compression  # z stream
            new_ferment_emission = (ferment_co2 - ferment_co2_cap) + compress_dehy_emission  # kgCo2e
            ferment_pipeline_emission = total_kg_kg_mil * self.pipeline_miles * ferment_co2_cap

            # Calculating boiler emission with amine regeneration CCS
            boiler_co2_cap = stack_co2 * (self.boiler_co2_cap_percent / 100)

            # Calculating emission due to amine regeneration w CCS
            amine_regen_emissions = nat_gas_ccs * boiler_co2_cap * ng_co2_kg_MJ  # emission after amine regeneration
            amine_co2_cap = (self.amine_co2_cap_percent / 100) * amine_regen_emissions # mass co2 captured
            new_amine_emission = amine_regen_emissions - amine_co2_cap  # emission released after amine regen w/ccs

            compression_emission = boiler_electric_ccs * elec_ci_compression * \
                                   (boiler_co2_cap + amine_co2_cap)

            # new_boiler_emissions = (stack_co2 - (boiler_co2_cap + amine_co2_cap)) + x + compression_emission

            co2_cap = ferment_co2_cap + boiler_co2_cap + amine_co2_cap

            boiler_pipeline_emission = total_kg_kg_mil * self.pipeline_miles * (boiler_co2_cap + amine_co2_cap)

            # total_pipeline_emission = boiler_pipeline_emission + ferment_pipeline_emission
            CCS_value = (-ferment_co2_cap + compress_dehy_emission + ferment_pipeline_emission) \
                        + (-boiler_co2_cap + compression_emission + boiler_pipeline_emission) + (
                                -amine_co2_cap + new_amine_emission)

            print('The boiler stack emissions : (gCo2e)', stack_co2 * kg_g)
            print('Mass amount of Co2 captured from boilerstack : (gCo2e)', boiler_co2_cap * kg_g)
            print('The Fermenter Co2 emissions :(gCo2e)', ferment_co2 * kg_g)
            print('Mass amount of co2 captured from fermenter (gCo2e) :', ferment_co2_cap * kg_g)
            print('The total amount of Co2 captured :(gCo2e) ', co2_cap * kg_g)

            print('Emissions due to compression & dehydration:(gCo2e)', compress_dehy_emission * kg_g)
            print('Emissions due to compression only :(gCo2e) ', compression_emission * kg_g)
            print('Emissions due to amine regeneration : (gCo2e)', amine_regen_emissions * kg_g)
            print('Mass amount captured from amine reg: (gCo2e)', amine_co2_cap * kg_g)
            print('Emissions due to amine regeneration with CCS', new_amine_emission * kg_g)

            print('')
            print('Boiler pipeline emissions', boiler_pipeline_emission * kg_g)
            print('Ferment pipeline emissions', ferment_pipeline_emission * kg_g)

            # print('Total process emissions with CCS', total_process_co2_ccs * kg_g)

        emissions["CCS"] = {'co2': {'name': 'co2', 'unit': 'kg', 'value': CCS_value}}

        return emissions
