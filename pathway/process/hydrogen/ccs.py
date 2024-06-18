import numpy as np
import os
import pandas as pd

from core.inputs import ContinuousInput, OptionsInput, Default
import core.conditionals as conditionals
import core.validators as validators
import pathway.process.ccs as ccs

PATH = os.path.join(os.getcwd(), 'pathway', 'process', 'hydrogen')
DATA = {
    'CCS_inputs': pd.read_csv(os.path.join(PATH, 'hydrogen_ccs_lcidata.csv')),
    'co2_transportation': pd.read_csv(os.path.join(os.getcwd(), 'pathway', 'gate_to_enduse', 'transportation_lcidata.csv'))
}

# conversion factors needed for calculations. Fuel specific values are from GREET fuel specs tab
g_in_kg = 1000
mj_in_kwh = 3.6
btu_in_mj = 947.81712
g_C_in_mol_co2 = 12.0107
g_co2_in_mol_co2 = 44.009
g_nat_gas_in_ft3 = 22
btu_in_ft3 = 983
g_C_in_nat_gas = 0.724
ppm_s_nat_gas = 6 / 1E6
g_s_in_mol_sox = 32.065
g_sox_in_mol_sox = 64

def user_inputs(*args, **kwargs):
    return ccs.user_inputs(*args, **kwargs)

class CCS:

    def __init__(self, input_set, data, emissions, technology=None):
        self.technology = technology or 'amine'
        self.input_set = input_set
        self.data = data
        self.emissions = emissions

        # outputs
        self.elec_carbon_intensity = None
        self.CO2_captured_plant = None
        self.CO2_captured_regen = None
        self.CO2_captured_comp = None
        self.CO2_captured = None

    def run(self, grid_intensity):
        # inputs
        cap_percent_regen = self.input_set.value('cap_percent_regen')
        cap_percent_plant = self.input_set.value('cap_percent_plant')
        user_ci = self.input_set.value('user_ci')
        pipeline_miles = self.input_set.value('pipeline_miles')
        cap_regen = cap_percent_regen > 0

        CO2 = SOX = 0

        # emissions from hydrogen plant without CCS
        for sub_stage, flow in self.emissions.items():
            # print(sub_stage, flow)
            if sub_stage == "G.H2 Compression and Precooling": # electricity based emissions not captured
                continue

            CO2 =  CO2 + flow['co2']['value']
            SOX = SOX + flow['sox']['value']

        self.emissions['aggregate'] = {'co2': {'name': 'co2', 'value': CO2, 'unit': 'kg'},'sox': {'name': 'sox', 'value': SOX, 'unit': 'kg'}}

        self.CO2_captured = CO2 * (cap_percent_plant / 100)

        if self.input_set.value('tea') == 'No':
            self.elec_carbon_intensity = user_ci / mj_in_kwh /1000 # g to kg
        else:
            co2_vals = []
            for substage, flow in grid_intensity.items():
                if flow['co2']['value']!=0:
                    co2_vals.append(flow['co2']['value'])
            self.elec_carbon_intensity = np.mean(co2_vals)

        # reads file with data on the required natural gas and electricity inputs for specific pathway and technology
        CCS_inputs = DATA['CCS_inputs']
        filtered = CCS_inputs[CCS_inputs['technology'] == self.technology]
        nat_gas_ccs = float(filtered[filtered['flows'] == "natural gas"].iloc[0].value)
        electricity_ccs = float(filtered[filtered['flows'] == "electricity"].iloc[0].value)

        # ng carbon intensity
        ng_co2_kg_MJ = btu_in_mj / btu_in_ft3 * g_nat_gas_in_ft3 * g_C_in_nat_gas / g_C_in_mol_co2 * \
                       g_co2_in_mol_co2 / g_in_kg
        ng_sox_kg_MJ = ppm_s_nat_gas * g_nat_gas_in_ft3 / btu_in_ft3 / g_s_in_mol_sox * g_sox_in_mol_sox / g_in_kg * btu_in_mj

        # intermediate calculations needed to solve equations
        a = nat_gas_ccs * ng_co2_kg_MJ * (
                cap_percent_plant / 100) * CO2  # Extra CO2 emitted from natural gas required for CCS
        if cap_regen:
            b = nat_gas_ccs * ng_co2_kg_MJ * (
                    cap_percent_regen / 100)  # Extra CO2/kg CO2 captured from natural gas used for amine regeneration
            e = electricity_ccs * self.elec_carbon_intensity * (
                    cap_percent_regen / 100)  # Extra CO2/kg CO2 captured from electricity used for amine regeneration
        c = nat_gas_ccs * ng_co2_kg_MJ * (
                cap_percent_plant / 100)  # CO2 emitted/ kg CO2 captured due to natural gas usage
        d = electricity_ccs * self.elec_carbon_intensity * (
                cap_percent_plant / 100) * CO2  # Extra CO2 emitted from electricity required for CCS
        f = electricity_ccs * self.elec_carbon_intensity * (
                cap_percent_plant / 100)  # CO2 emitted/ kg CO2 captured due to electricity usage

        # calculating total emissions when regeneration is captured
        if cap_regen:
            c = 0
            f = 0

            co2_fuel_for_ccs = ((a / (1 - b)) + ((c * d) / ((1 - f)))) / (
                    1 - ((c * e) / ((1 - f))))
            co2_elec_for_ccs = (d + (e * co2_fuel_for_ccs)) / (1 - f)

            self.CO2_captured_plant = (CO2 * (cap_percent_plant / 100))
            self.CO2_captured_regen = (co2_fuel_for_ccs * (cap_percent_regen / 100))
            self.CO2_captured_comp = 0 # Compression emissions not captured for H2 since electricity is external

        # case 1
        else:
            b = 0
            c = 0
            e = 0
            f = 0

            co2_fuel_for_ccs = ((a / (1 - b)) + ((c * d) / ((1 - f)))) / (
                    1 - ((c * e) / ((1 - f))))
            co2_elec_for_ccs = (d + (e * co2_fuel_for_ccs)) / (1 - f)

            self.CO2_captured_plant = (CO2 * (cap_percent_plant / 100))
            self.CO2_captured_regen = 0
            self.CO2_captured_comp = 0

        self.CO2_captured = self.CO2_captured_plant + self.CO2_captured_regen + self.CO2_captured_comp
        new_emissions = CO2 + co2_elec_for_ccs + co2_fuel_for_ccs

        # setting the emissions to the correct value (updating the emissions to be graph)
        self.emissions['aggregate']['co2']['value'] = new_emissions - self.CO2_captured
        self.emissions['aggregate']['sox']['value'] += ng_sox_kg_MJ * nat_gas_ccs * self.CO2_captured

        # pipeline CO2 transportation emissions review
        co2_transportation = DATA['co2_transportation']
        filtered = co2_transportation[co2_transportation['Feed'] == "co2"]

        for x in (self.emissions['aggregate']):
            self.emissions['aggregate'][x]['value'] += filtered.loc[filtered['flows'] == x]['value'].iloc[0] * pipeline_miles * self.CO2_captured

        eff_cap = 100 - (self.emissions['aggregate']['co2']['value'] / CO2 * 100)
        co2_avoid = CO2 - self.emissions['aggregate']['co2']['value']

        sub = dict(self.emissions)
        for substage, flow in sub.items():
            if substage != 'aggregate':
                self.emissions.pop(substage)
