import os
import pandas as pd

from core.inputs import ContinuousInput, OptionsInput, Default
import core.conditionals as conditionals
import core.validators as validators
import pathway.process.ccs as ccs

PATH = os.path.join(os.getcwd(), 'pathway', 'process', 'coal')
DATA = {
    'CCS_inputs': pd.read_csv(os.path.join(PATH, 'coal_power_CCS_lcidata.csv')),
    'coal_properties': pd.read_csv(os.path.join(PATH, 'coal_properties.csv')),
    'co2_transportation': pd.read_csv(os.path.join(os.getcwd(), 'pathway', 'gate_to_enduse', 'transportation_lcidata.csv'))
}

g_in_kg = 1000
mj_in_kwh = 3.6
btu_in_mj = 947.81712
g_C_in_mol_co2 = 12.0107
g_co2_in_mol_co2 = 44.009
g_in_short_ton = 907185
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
        self.elec_carbon_intensity = None
        self.CO2_captured_plant = None
        self.CO2_captured_regen = None
        self.CO2_captured_comp = None
        self.CO2_captured = None

    def run(self, coal_rank):
        cap_percent_regen = self.input_set.value('cap_percent_regen')
        cap_percent_plant = self.input_set.value('cap_percent_plant')
        use_user_ci = self.input_set.value('use_user_ci')
        user_ci = self.input_set.value('user_ci')
        pipeline_miles = self.input_set.value('pipeline_miles')

        if self.input_set.value('tea') == 'Yes':
            use_user_ci = 'Powerplant'

        cap_regen = cap_percent_regen > 0
        CO2 = self.emissions['aggregate']['co2']['value']
        if use_user_ci == 'User':
            self.elec_carbon_intensity = user_ci / mj_in_kwh / 1000 
        else:
            self.elec_carbon_intensity = float(self.data.loc[self.data['flows'] == 'co2']['value'].iloc[0]) / mj_in_kwh

        CCS_inputs = DATA['CCS_inputs']
        filtered = CCS_inputs[CCS_inputs['technology'] == self.technology]
        coal_ccs = float(filtered[filtered['flows'] == "coal"].iloc[0].value)
        electricity_ccs = float(filtered[filtered['flows'] == "electricity"].iloc[0].value)
        coal_properties = DATA['coal_properties']
        coal_densities = coal_properties[coal_properties['characteristic'] == 'energy density']
        filtered = coal_densities[coal_densities['coal rank'] == coal_rank]
        btu_in_short_ton = float(filtered.iloc[0].value)
        coal_sulfur = coal_properties[coal_properties['characteristic'] == 'sulfur content']
        filtered = coal_sulfur[coal_sulfur['coal rank'] == coal_rank]
        ppm_s_coal = float(filtered.iloc[0].value)/1E6
        coal_carbon = coal_properties[coal_properties['characteristic'] == 'carbon content']
        filtered = coal_carbon[coal_carbon['coal rank'] == coal_rank]
        g_C_in_coal = float(filtered.iloc[0].value) / 100
        coal_co2_kg_MJ = btu_in_mj / btu_in_short_ton * g_in_short_ton * g_C_in_coal / g_C_in_mol_co2 * \
                         g_co2_in_mol_co2 / g_in_kg
        coal_sox_kg_MJ = ppm_s_coal * g_in_short_ton / btu_in_short_ton / g_s_in_mol_sox * g_sox_in_mol_sox / g_in_kg * btu_in_mj
        a = coal_ccs * coal_co2_kg_MJ * (cap_percent_plant / 100) * CO2
        if use_user_ci == 'Powerplant' and cap_regen:
            b = coal_ccs * coal_co2_kg_MJ * (cap_percent_regen / 100)
            c = coal_ccs * coal_co2_kg_MJ * (cap_percent_plant / 100)
            d = electricity_ccs * self.elec_carbon_intensity * (cap_percent_plant / 100) * CO2
            e = electricity_ccs * self.elec_carbon_intensity * (cap_percent_regen / 100)
            f = electricity_ccs * self.elec_carbon_intensity * (cap_percent_plant / 100)

            co2_fuel_for_ccs = ((a / (1 - b)) + ((c * d) / ((1 - f) * (1 - b)))) / (
                    1 - ((c * e) / ((1 - f) * (1 - b))))
            co2_elec_for_ccs = (d + (e * co2_fuel_for_ccs)) / (1 - f)

            self.CO2_captured_plant = (CO2 * (cap_percent_plant / 100))
            self.CO2_captured_regen = (co2_fuel_for_ccs * (cap_percent_regen / 100))
            self.CO2_captured_comp = (co2_elec_for_ccs * (cap_percent_regen / 100))
        elif use_user_ci == 'Powerplant' and not cap_regen:
            b = coal_ccs * coal_co2_kg_MJ * (cap_percent_plant / 100)
            c = electricity_ccs * self.elec_carbon_intensity * (cap_percent_plant / 100) * CO2
            d = electricity_ccs * self.elec_carbon_intensity * (cap_percent_plant / 100)

            co2_elec_for_ccs = c / (1 - d)
            co2_fuel_for_ccs = a + (b * co2_elec_for_ccs)

            self.CO2_captured_plant = (CO2 * (cap_percent_plant / 100))
            self.CO2_captured_regen = 0
            self.CO2_captured_comp = (co2_elec_for_ccs * (cap_percent_plant / 100))
        elif use_user_ci == 'User' and cap_regen:
            b = coal_ccs * coal_co2_kg_MJ * (cap_percent_regen / 100)

            co2_fuel_for_ccs = a / (1 - b)
            co2_elec_for_ccs = (electricity_ccs * self.elec_carbon_intensity * ((cap_percent_plant / 100 * CO2) + \
                                                                                (cap_percent_regen / 100 * co2_fuel_for_ccs)))

            self.CO2_captured_plant = (CO2 * (cap_percent_plant / 100))
            self.CO2_captured_regen = (co2_fuel_for_ccs * (cap_percent_regen / 100))
            self.CO2_captured_comp = 0
        elif use_user_ci == 'User' and not cap_regen:
            co2_fuel_for_ccs = coal_ccs * CO2 * (cap_percent_plant / 100) * coal_co2_kg_MJ
            co2_elec_for_ccs = electricity_ccs * CO2 * (cap_percent_plant / 100) * self.elec_carbon_intensity

            self.CO2_captured_plant = (CO2 * (cap_percent_plant / 100))
            self.CO2_captured_regen = 0
            self.CO2_captured_comp = 0

        self.CO2_captured = self.CO2_captured_plant + self.CO2_captured_regen + self.CO2_captured_comp
        new_emissions = CO2 + co2_elec_for_ccs + co2_fuel_for_ccs
        self.emissions['aggregate']['co2']['value'] = new_emissions - self.CO2_captured
        if hasattr(self.emissions['aggregate'], 'sox'):
            self.emissions['aggregate']['sox']['value'] += coal_sox_kg_MJ * coal_ccs * self.CO2_captured
        else:
            self.emissions['aggregate']['sox'] = {
                'name': 'sox',
                'unit': 'kg',
                'value': coal_sox_kg_MJ * coal_ccs * self.CO2_captured
            }
        co2_transportation = DATA['co2_transportation']
        filtered = co2_transportation[co2_transportation['Feed'] == "co2"]

        for x in (self.emissions['aggregate']):
            self.emissions['aggregate'][x]['value'] += filtered.loc[filtered['flows'] == x]['value'].iloc[0] * pipeline_miles * self.CO2_captured
