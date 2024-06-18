from core.pathway import ActivitySource
from analysis.lca import compute_input_flows, compute_emission_flows
import core.validators as validators
import core.conditionals as conditionals
from core.inputs import CategoricalInput, ContinuousInput, OptionsInput, Default
import sys
import pandas as pd
import os

PATH = os.getcwd() + "/pathway/process/ccs/dac/"


class CcsDacLca(ActivitySource):

    @classmethod
    def user_inputs(cls):
        return [
            CategoricalInput('tech', 'Plant Technology'),
            ContinuousInput('capacity', 'Plant Size in tCO2/year',
                            # defaults=[Default()],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(100)]),
            OptionsInput('use_co2_free_elec', 'Use CO2 free electricity', options=['Yes', 'No']),
            OptionsInput('use_user_elec_ci', 'Use User Electricity Carbon Intensity', options=['Yes', 'No'],
                         defaults=[Default('No')],
                         conditionals=[conditionals.input_equal_to('use_co2_free_elec', 'No')]),
            ContinuousInput('user_elec_ci', 'Electricity Carbon Intensity in tCO2/kWh',
                            defaults=[Default(0.48)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                            conditionals=[conditionals.input_equal_to('use_user_elec_ci', 'Yes')]),
            OptionsInput('nat_gas_capture', 'Capture Natural Gas Emissions using Thermal Amine? (85% Capture)',
                         options=['Yes', 'No']),
        ]

    def get_inputs(self):

        return {
            'primary': None,
            'secondary': None
        }

    def get_natgas_ci(self):
        g_in_kg = 1000
        btu_in_mj = 947.81712
        g_C_in_mol_co2 = 12.0107
        g_co2_in_mol_co2 = 44.009
        g_nat_gas_in_ft3 = 22
        btu_in_ft3 = 983
        g_C_in_nat_gas = 0.724
        natgas_ci = float(btu_in_mj / btu_in_ft3 * g_nat_gas_in_ft3 * g_C_in_nat_gas / g_C_in_mol_co2 * \
                          g_co2_in_mol_co2 / g_in_kg)  # co2_kg_MJ
        return natgas_ci

    def get_elec_consumption(self):
        ref_plant = pd.read_csv(PATH + "plant_ref_data_dac.csv")
        filtered = ref_plant[ref_plant['Plant Technology'] == self.tech]
        dac_elec_consumption = float(
            filtered[filtered['Plant Technology'] == self.tech].iloc[0].dac_electricity)  # in MJ/kgCO2 captured
        comp_elec_consumption = float(
            filtered[filtered['Plant Technology'] == self.tech].iloc[0].comp_electricity)
        total_elec_consumption = dac_elec_consumption + comp_elec_consumption
        return total_elec_consumption

    def get_natgas_dac_consumption(self):  # dac
        ref_plant = pd.read_csv(PATH + "plant_ref_data_dac.csv")
        filtered = ref_plant[ref_plant['Plant Technology'] == self.tech]
        nat_gas_dac_consumption = float(
            filtered[filtered['Plant Technology'] == self.tech].iloc[0].gas)  # in MJ/kgCO2 captured from dac
        return nat_gas_dac_consumption

    # NG consumed for point source thermal amine carbon capture
    def get_natgas_ps_consumption(self):  # point source
        if self.nat_gas_capture == 'Yes':
            nat_gas_ps_consumption = self.get_natgas_dac_consumption() * self.get_natgas_ci() * 0.85 * 2.95  # in MJ/kgCO2 captured from ps
            # 0.85 = capture rate
            # 2.95 = natural gas consumption in MJ per kg of CO2 captured (from table reference.csv in tea/nat gas)
        else:
            nat_gas_ps_consumption = 0
        return nat_gas_ps_consumption

    def get_emissions(self):
        # Ton of CO2 captured
        co2_captured_dac = self.capacity

        # Ton of CO2 emitted due to electricity
        if self.use_co2_free_elec == 'Yes':
            elec_co2_kg_MJ = 0
        elif self.use_user_elec_ci == 'Yes':
            elec_co2_kg_MJ = self.user_elec_ci
        else:
            elec_co2_kg_MJ = 0.48 / 3.6  # 0.48 kgCO2/KWh US mix carbon intensity
        co2_emitted_elec = self.get_elec_consumption() * elec_co2_kg_MJ * self.capacity  # in ton/years

        # Ton of CO2 emitted due to nat gas
        if self.nat_gas_capture == 'No':
            co2_emitted_nat_gas = self.get_natgas_dac_consumption() * self.get_natgas_ci() * self.capacity  # in ton/years
            co2_captured_ps = 0
        else:
            co2_emitted_nat_gas = self.get_natgas_dac_consumption() * self.get_natgas_ci() * self.capacity * (
                    1 - 0.85)  # in ton/years
            co2_captured_ps = self.get_natgas_dac_consumption() * self.get_natgas_ci() * self.capacity * 0.85

        total_co2_emitted = co2_emitted_elec + co2_emitted_nat_gas  # in ton/years

        emissions = {'Net emissions in ton/year': total_co2_emitted - co2_captured_dac - co2_captured_ps,
                     'CO2 Captured in ton/year': co2_captured_dac + co2_captured_ps,
                     'CO2 Emitted in ton/year': total_co2_emitted}

        # emission_flows['aggregate'] = {'co2': {'name': 'co2',
        #                                         'unit': 'ton/year',
        #                                         'value': total_co2_emitted - co2_captured_dac - co2_captured_ps}
        #                                 }
        emission_flows = {}
        print(total_co2_emitted - co2_captured_dac - co2_captured_ps)
        emission_flows['CO2 Captured in ton/year'] = {'co2': {'name': 'co2',
                                                'unit': 'ton/year',
                                                'value': - co2_captured_dac - co2_captured_ps}
                                        }
        emission_flows['CO2 Emitted in ton/year'] = {'co2': {'name': 'co2',
                                                'unit': 'ton/year',
                                                'value': total_co2_emitted}
                                        }
        return emission_flows

        # return compute_emission_flows(
        # self.filtered_data_frame(),
        # flow_output=self.output
        # )
