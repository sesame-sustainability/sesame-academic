import pandas as pd
import os
import us, statistics

from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from core.tea import TeaBase
from core import validators, conditionals


PATH = os.getcwd() + "/tea/electricity/ccs/pointsources/"


class CcsTea:

    @classmethod
    def user_inputs(cls, source = "Hydrogen Production", tea_lca = False, cost_or_not = "Cost"):
        cost_defaults = pd.read_csv(PATH + "transport&storage costs.csv")

        cap_tech = "amine" 
        tea_only_inputs1 = [
            ContinuousInput(
                'cap_percent_plant', 'CO\u2082 Captured from Plant',
                unit='%',
                defaults=[Default(85)],
                validators=[validators.numeric(), validators.gte(0), validators.lt(100)],
                conditionals=[conditionals.input_equal_to('use_CCS', 'Yes')],
                tooltip=Tooltip(
                    'Percent of CO2, from the plant, captured by the CCS unit. Default 85% is from the NPC report, along with other emission and cost data from Tables 2-x. Also, the IEA study (e.g., Tables 7) shows that capital cost does not scale very non-linearly with capture %, so we assume linear scaling here, i.e., increasing capture % by 10% will increase capital cost by 10%. The same linearity is adopted for CCS energy consumption, because the NPC report assumes a fixed specific energy per CO2 captured amount. Thus, note that the further away from the default 85% capture, the less accurate our TEA results would be.',
                    source='NPC 2020; IEA 2020',
                    source_link='https://www.energy.gov/sites/default/files/2021-06/2019%20-%20Meeting%20the%20Dual%20Challenge%20Vol%20II%20Chapter%202.pdf; https://ieaghg.org/publications/technical-reports/reports-list/9-technical-reports/1041-2020-07-update-techno-economic-benchmarks-for-fossil-fuel-fired-power-plants-with-co2-capture',
                )

            ),
            ContinuousInput(
                'cap_percent_regen', 'CO\u2082 Captured from Amine Regeneration',
                unit='%',
                defaults=[Default(85)],
                validators=[validators.numeric(), validators.gte(0), validators.lt(100)],
                conditionals=[conditionals.input_equal_to('use_CCS', 'Yes')],
                tooltip=Tooltip(
                    'Amine regeneration for continuous CO2 capture requires heating. For CCS with natural gas/coal power plant, the heating source is natural gas/coal, respectively; for H2 production plant, the heating source is natural gas. If CO2 from such combustion processes is desired, then specify the capture %.',
                    source='NPC 2020',
                    source_link='https://www.energy.gov/sites/default/files/2021-06/2019%20-%20Meeting%20the%20Dual%20Challenge%20Vol%20II%20Chapter%202.pdf',
                )

            ),
        ]

        tea_only_inputs2 = [
            ContinuousInput(
                'pipeline_miles', 'Pipeline Distance from Capture to Sequester',
                unit='mi',
                defaults=[Default(240)], 
                validators=[validators.numeric(), validators.gte(0)],
                conditionals=[conditionals.input_equal_to('use_CCS', 'Yes')],
                tooltip=Tooltip(
                    'The distance could vary significantly by projects. 240 mi roughly translates to ~ 20 $/T CO2 for transportation and sequestration, assuming storage costs 8 $/T CO2, and transportation costs 0.05 $/T CO2/mi.',
                    source='NPC 2020',
                    source_link='https://dualchallenge.npc.org/files/CCUS-Chap_2-060520.pdf',
                )
            ),
        ]

        tea_lca_inputs = [
            OptionsInput(
                'storage_cost_source', 'Source for CO\u2082 Storage Cost',
                options = ['Default','User defined'],
                defaults=[Default('Default')],
                conditionals=[conditionals.input_equal_to('use_CCS', 'Yes')],
                tooltip=Tooltip(
                    'Default is from the NPC report. For US average, storage costs 8 $/T CO2, and transportation costs 0.05 $/T CO2/mi.',
                    source='NPC 2020',
                    source_link='https://dualchallenge.npc.org/files/CCUS-Chap_2-060520.pdf',
                )
            ),
            ContinuousInput(
                'storage_cost', 'CO\u2082 Storage Cost',
                unit='$/tonCO2',
                defaults=[Default(8)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                conditionals=[conditionals.input_equal_to('storage_cost_source', 'User defined')],
                tooltip=Tooltip(
                    'For US average, storage costs 8 $/T CO2, and transportation costs 0.05 $/T CO2/mi.',
                    source='NPC 2020',
                    source_link='https://dualchallenge.npc.org/files/CCUS-Chap_2-060520.pdf',
                )

            ),
        ]

        coal_ng_specific_inputs = [
            OptionsInput(
                'use_user_ci', 'Source of Compression Power',
                options=['User', 'Powerplant'],
                defaults=[Default('Powerplant')],
                conditionals=[
                    conditionals.context_equal_to('compute_cost', False),
                    conditionals.input_not_equal_to('use_CCS', 'No'),
                ],
                tooltip=Tooltip(
                    'Life cycle carbon intensity of the power used for compressing captured CO2 for transportation to sequester site. Default for natural gas and coal plants is to use the electricity generated onsite.'
                )

            ),
            ContinuousInput(
                'user_ci', 'Emissions of Compression Power (in g/kWh)',
                validators=[validators.numeric(), validators.gte(0)],
                conditionals=[
                    conditionals.input_equal_to('use_CCS', 'Yes'),
                    conditionals.input_equal_to('use_user_ci', 'User'),
                ],
                tooltip=Tooltip(
                    'Life cycle carbon intensity of the power used for compressing captured CO2 for transportation to sequester site. Default for natural gas and coal plants is to use the electricity generated onsite.'
                )

            ),
        ]

        if tea_lca:
            return tea_lca_inputs
        else:
            if source == "Hydrogen Production":
                return tea_only_inputs1 + tea_only_inputs2 + tea_lca_inputs
            else:
                return tea_only_inputs1 + coal_ng_specific_inputs + tea_only_inputs2 + tea_lca_inputs

    def __init__(self, plant_type, plant_size, economies_of_scale_factor, cap_percent_plant, cap_percent_regen, storage_cost_source,
                 storage_cost, crf, gr, distance, electricity_ci, electricity_price, natural_gas_price, CO2_captured, extra_inputs = None):
        self.plant_type = plant_type
        self.plant_size = float(plant_size)  
        self.economies_of_scale_factor = economies_of_scale_factor
        self.capture_tech = "amine"  
        self.cap_percent_plant = cap_percent_plant  
        self.cap_percent_regen = cap_percent_regen  
        self.storage_cost_source = storage_cost_source
        self.storage_cost = storage_cost  
        self.crf = crf 
        self.gr = gr 
        self.distance = distance  
        self.electricity_ci = electricity_ci  
        self.Power_Price = electricity_price 
        self.Gas_Cost = natural_gas_price
        self.extra_inputs = extra_inputs

        if CO2_captured is not None:
            self.CO2_captured = CO2_captured['total'] 
            self.CO2_captured_plant = CO2_captured['plant']
            self.CO2_captured_regen = CO2_captured['regen']
            self.CO2_captured_comp = CO2_captured['comp']
        else:
            self.CO2_captured = None

    def get_capture_cost_breakdown(self):
        global cap_regen_emissions, cap_comp_emissions
        ref_plant = pd.read_csv(PATH + "reference.csv")
        filtered = ref_plant[ref_plant['plant type'] == self.plant_type]
        ref_plant_size = float(
            filtered[filtered['technology'] == self.capture_tech].iloc[0].refsize)  
        ref_co2_captured = float(
            filtered[filtered['technology'] == self.capture_tech].iloc[0].co2captured)  
        ref_avg_capital_cost = float(
            filtered[filtered['technology'] == self.capture_tech].iloc[0].avgcapex) * 1000000  
        ref_min_capital_cost = float(
            filtered[filtered['technology'] == self.capture_tech].iloc[0].mincapex) * 1000000  
        ref_max_capital_cost = float(
            filtered[filtered['technology'] == self.capture_tech].iloc[0].maxcapex) * 1000000  
        fuel_consumption = float(
            filtered[filtered['technology'] == self.capture_tech].iloc[0].fuel)  
        elec_consumption = float(
            filtered[filtered['technology'] == self.capture_tech].iloc[0].electricity)  
        fom_capex = float(
            filtered[filtered['technology'] == self.capture_tech].iloc[0].fom_capex)  

        other_costs = pd.read_csv(PATH + "transport&storage costs.csv")
        ref_transp_cost = float(other_costs[other_costs["Generation Region"] == self.gr].iloc[0].transport)  
        if self.storage_cost_source != 'User defined':
            ref_storage_cost = float(other_costs[other_costs["Generation Region"] == self.gr].iloc[0].storage)  
            self.storage_cost = ref_storage_cost
        capture_scaling_factor = float(self.cap_percent_plant) / 85  

        if self.plant_type == "Hydrogen Production":
            self.cap_percent_comp = 0  
            mmcfd_m3_per_hr = 1177.17
            m3_MW = 0.003 
            plant_size = self.plant_size 
            ref_plant_size = ref_plant_size * mmcfd_m3_per_hr * m3_MW 
        else:
            self.cap_percent_comp = self.cap_percent_plant  
            plant_size = float(self.plant_size / (
                        1 - elec_consumption * ref_co2_captured * capture_scaling_factor / (
                            ref_plant_size * 3.6 * 8760))) 
        flow_scaling_factor = float(plant_size) / float(ref_plant_size)
        capex_scaling_factor = float(flow_scaling_factor ** self.economies_of_scale_factor)
        g_in_kg = 1000
        btu_in_mj = 947.81712
        g_C_in_mol_co2 = 12.0107
        g_co2_in_mol_co2 = 44.009
        g_in_short_ton = 907185

        if self.plant_type == "Coal Power Plants":
            coal_rank = self.extra_inputs['coal_rank']
            print(coal_rank)
            coal_properties = pd.read_csv(PATH [:- len ("ccs/pointsources/")] + "coal/coal_properties.csv")
            coal_densities = coal_properties[coal_properties['characteristic'] == 'energy density']
            filtered = coal_densities[coal_densities['coal rank'] == coal_rank] 
            btu_in_short_ton = float(filtered.iloc[0].value)
            coal_carbon = coal_properties[coal_properties['characteristic'] == 'carbon content']
            filtered = coal_carbon[coal_carbon['coal rank'] == coal_rank]  
            g_C_in_coal = float(filtered.iloc[0].value) / 100
            fuel_co2_kg_MJ = btu_in_mj / btu_in_short_ton * g_in_short_ton * g_C_in_coal / g_C_in_mol_co2 * \
                             g_co2_in_mol_co2 / g_in_kg

        else:
            g_nat_gas_in_ft3 = 22
            btu_in_ft3 = 983
            g_C_in_nat_gas = 0.724
            fuel_co2_kg_MJ = float(btu_in_mj / btu_in_ft3 * g_nat_gas_in_ft3 * g_C_in_nat_gas / g_C_in_mol_co2 * \
                                 g_co2_in_mol_co2 / g_in_kg)

        if self.CO2_captured is not None:
            cap_total_emissions = self.CO2_captured
            cap_plant_emissions = self.CO2_captured_plant
            cap_regen_emissions = self.CO2_captured_regen
            cap_comp_emissions = self.CO2_captured_comp
        else:
            cap_plant_emissions = ref_co2_captured * flow_scaling_factor * capture_scaling_factor  
            elec_co2_kg_MJ = self.electricity_ci / 3.6  
            a = float(fuel_consumption * fuel_co2_kg_MJ * cap_plant_emissions)
            b = float(fuel_consumption * fuel_co2_kg_MJ * self.cap_percent_regen / 100)
            c = float(fuel_consumption * fuel_co2_kg_MJ * self.cap_percent_comp / 100)
            d = float(elec_consumption * elec_co2_kg_MJ * cap_plant_emissions)
            e = float(elec_consumption * elec_co2_kg_MJ * self.cap_percent_regen / 100)
            f = float(elec_consumption * elec_co2_kg_MJ * self.cap_percent_comp / 100)
            if self.cap_percent_regen == 0:
                cap_regen_emissions = 0
            else:
                cap_regen_emissions = ((a / (1 - b) + c * d / (1 - f)) / (
                    1 - c * e / (1 - f))) * self.cap_percent_regen / 100
            if self.cap_percent_comp == 0:
                cap_comp_emissions = 0
            else:
                cap_comp_emissions = (d + e * cap_regen_emissions) / (1 - f)
            cap_total_emissions = cap_plant_emissions + cap_regen_emissions + cap_comp_emissions

        extra_scaling_factor = cap_total_emissions / cap_plant_emissions  
        ovrnght_avg_cap_cost = float(
            ref_avg_capital_cost * capex_scaling_factor * capture_scaling_factor * extra_scaling_factor)  
        ovrnght_min_cap_cost = float(
            ref_min_capital_cost * capex_scaling_factor * capture_scaling_factor * extra_scaling_factor)  
        ovrnght_max_cap_cost = float(
            ref_max_capital_cost * capex_scaling_factor * capture_scaling_factor * extra_scaling_factor)  
        annualized_avg_cap_cost = self.crf * ovrnght_avg_cap_cost  
        annualized_min_cap_cost = self.crf * ovrnght_min_cap_cost  
        annualized_max_cap_cost = self.crf * ovrnght_max_cap_cost  
        fom_avg_cost = ovrnght_avg_cap_cost * fom_capex / 100  
        fom_min_cost = ovrnght_min_cap_cost * fom_capex / 100  
        fom_max_cost = ovrnght_max_cap_cost * fom_capex / 100  
        nat_gas_cost = self.Gas_Cost * fuel_consumption * cap_total_emissions * 1000 * 0.000948 
        electricity_cost = self.Power_Price * elec_consumption * cap_total_emissions * 1000 * 0.000277778 
        vom_cost = nat_gas_cost + electricity_cost  

        ccs_parasitic_load = plant_size/self.plant_size-1 
        fuel_consumption_per_MWh= fuel_consumption * 1000 * cap_total_emissions * (btu_in_mj/ 1000000) / (plant_size  * 8760) 
        capture_avg_cost = annualized_avg_cap_cost + fom_avg_cost + vom_cost
        capture_min_cost = annualized_min_cap_cost + fom_min_cost + vom_cost
        capture_max_cost = annualized_max_cap_cost + fom_max_cost + vom_cost
        capture_avg_taxes = 0.21 * capture_avg_cost  
        capture_min_taxes = 0.21 * capture_min_cost  
        capture_max_taxes = 0.21 * capture_max_cost  
        transp_cost = ref_transp_cost * self.distance * cap_total_emissions  
        storage_cost = self.storage_cost * cap_total_emissions 
        print(cap_total_emissions)
        cost_breakdown = {
            "Total AVG capture, transport and storage cost in USD/tCO2":
                (
                            annualized_avg_cap_cost + fom_avg_cost + vom_cost + capture_avg_taxes + transp_cost + storage_cost) / cap_total_emissions,
            "Total MIN capture, transport and storage cost in USD/tCO2":
                (
                            annualized_min_cap_cost + fom_min_cost + vom_cost + capture_min_taxes + transp_cost + storage_cost) / cap_total_emissions,
            "Total MAX capture, transport and storage cost in USD/tCO2":
                (
                            annualized_max_cap_cost + fom_max_cost + vom_cost + capture_max_taxes + transp_cost + storage_cost) / cap_total_emissions,
            "AVG Capital Cost in USD/tCO2": annualized_avg_cap_cost / cap_total_emissions,
            "MIN Capital Cost in USD/tCO2": annualized_min_cap_cost / cap_total_emissions,
            "MAX Capital Cost in USD/tCO2": annualized_max_cap_cost / cap_total_emissions,
            "AVG Fixed O&M Cost in USD/tCO2": fom_avg_cost / cap_total_emissions,
            "MIN Fixed O&M Cost in USD/tCO2": fom_min_cost / cap_total_emissions,
            "MAX Fixed O&M Cost in USD/tCO2": fom_max_cost / cap_total_emissions,
            "Natural Gas & Electricity Costs in USD/tCO2": (vom_cost / cap_total_emissions),
            "AVG Capture Taxes in USD/CO2": capture_avg_taxes / cap_total_emissions,
            "MIN Capture Taxes in USD/CO2": capture_min_taxes / cap_total_emissions,
            "MAX Capture Taxes in USD/CO2": capture_max_taxes / cap_total_emissions,
            "Transport Cost in USD/tCO2": transp_cost / cap_total_emissions,
            "Storage Cost in USD/tCO2": storage_cost / cap_total_emissions
        }
        print(cost_breakdown["Total AVG capture, transport and storage cost in USD/tCO2"])
        emissions = {'Plant':cap_plant_emissions, 'Regen':cap_regen_emissions, 'Compression':cap_comp_emissions, 'Total': cap_total_emissions}
        avg_cost_breakdown = {'Capital & Fixed' : {'Capex': annualized_avg_cap_cost,'FOM':fom_avg_cost}, 'Operational' : {'VOM': vom_cost, 'Tax': capture_avg_taxes, 'Transport': transp_cost , 'Storage': storage_cost}, 'Maintenance':0}

        return avg_cost_breakdown, emissions, ccs_parasitic_load, ovrnght_avg_cap_cost, fuel_consumption_per_MWh
