CAPITAL_FRACTION = [0.8, 0.1, 0.1]
DEPRECIATION = [0.2, 0.32, 0.192, 0.1152, 0.1152, 0.0576]

import os
import pandas as pd
import us, statistics

from tea.electricity.SLCOE import SLCOE
from core import validators
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from core.tea import TeaBase
import core.conditionals as conditionals
from tea.electricity.ccs.pointsources.ccs_tea import CcsTea
from analysis.sensitivity import SensitivityInput

PATH = os.getcwd() + "/tea/electricity/coal/"
REGION_STATE = pd.read_csv(os.getcwd() + "/tea/electricity/regions_mapping.csv")


class CoalTEA(TeaBase):
    unit = '$/MWh'

    @classmethod
    def user_inputs(cls, tea_lca=False):
        tea_lca_inputs = [
            ContinuousInput(
                'plant_size', 'Powerplant Size',
                unit='MW',
                defaults=[Default(650)],
                validators=[validators.numeric(), validators.gte(0)],
                tooltip=Tooltip(
                    'Impacts levelized capital cost via economy of scale.',
                    source='ATB; EIA',
                    source_link='https://atb.nrel.gov/electricity/2020/index.php?t=ei; https://www.eia.gov/todayinenergy/detail.php?id=38312'
                    ),

            ),
            ContinuousInput(
                'economies_of_scale_factor', 'Economies of Scale Factor',
                unit='dless',
                defaults=[Default(0.6)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(1)],
                tooltip=Tooltip(
                    'A scaling factor of 0.6 is commonly assumed for facilities made up of tanks and pipes. The equation used is: capital cost = (default capital cost) * [ capacity / (default capacity) ]^(scaling factor).',
                    source='', source_link=''),

            ),
            ContinuousInput(
                'user_coalprice', 'Coal Price',
                unit='$/MMBtu',
                defaults=[Default(1.9)],
                tooltip=Tooltip(
                    'From 2000-2020, annual coal prices varied from 1.4 to 2.6 $/MMBtu, in real 2021 dollars.',
                    source='EIA', source_link='https://www.eia.gov/coal/annual/'),
                validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
            ),

            ContinuousInput(
                'user_trans_dist_cost', 'Transmission & Distribution Cost',
                unit='$/MWh',
                defaults=[Default(47)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(200)],
                tooltip=Tooltip(
                    '47 $/MWh is the US average transmission AND distribution cost, including 14 transmission, and 33 distribution (mainly to residential and commercial consumers). If the power is intended for industrial use, then 14 is recommended.',
                    source='EIA',
                    source_link='https://www.eia.gov/outlooks/aeo/data/browser/
                ),
            ),

            ContinuousInput(
                'sale_tax_rate', 'Tax',
                unit='%',
                defaults=[Default(6.35)],
                validators=[validators.numeric(), validators.gt(0), validators.lt(100)],
                tooltip=Tooltip(
                    "The default value represents sales tax, which varies by states and specific use cases. 6.35% represents US averegae sales tax. For electricity-specific tax, 7% was found for North Carolina, and 6.25% for Texas non-residential use: https://comptroller.texas.gov/taxes/publications/96-1309.pdf.",
                    source_link='https://www.ncdor.gov/taxes-forms/sales-and-use-tax/electricity
                ),
            ),

        ]

        ccs_tea_only = [
            OptionsInput(
                'use_CCS', 'Use CCS (Carbon Capture & Sequester)',
                options=['Yes', 'No'],
                defaults=[Default('No')],
                tooltip=Tooltip(
                    'As a carbon mitigation technology, a CCS unit captures CO2 from a manufacturing plant and transport the captured CO2 to a sequestration site for long-term storage.',
                )

            ),
        ]
        tea_lca_inputs2 = [
            OptionsInput(
                'interest_rate_or_crf', 'Choose Interest Rate or Capital Recovery Factor',
                options=['Interest Rate', 'Capital Recovery Factor'],
                defaults=[Default('Interest Rate')],
            ),
            ContinuousInput(
                'crf', 'Capital Recovery Factor',
                unit='%',
                defaults=[Default(5)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                conditionals=[conditionals.input_equal_to('interest_rate_or_crf', 'Capital Recovery Factor')],
                tooltip=Tooltip(
                    'Amortized capital cost per year ($/yr) = capital recovery factor * total capital cost ($)',
                    source='ATB 2020', source_link='https://atb.nrel.gov/electricity/2020/index.php?t=ei'),

            ),
            ContinuousInput(
                'interest_rate', 'Interest Rate',
                unit='%',
                defaults=[Default(5)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                conditionals=[conditionals.input_equal_to('interest_rate_or_crf', 'Interest Rate')],
                tooltip=Tooltip(
                    "Levelized capital cost = CRF (capital recovery factor) * PFF (project financial factor) *capital cost; crf = WACC/(1-(1/(1+WACC)^t)), where t=lifetime; WACC = ((1+((1-DF)*((1+RROE)*(1+i)-1)) + (DF*((1+IR)*(1+i)-1)*(1-TR))) / (1+i)) – 1, , where PROE (rate or return on equity) ~5%, DF (debt fraction) ~74%, TR (tax rate) ~ 26%, i (inflation rate) ~2.5%, IR (interest rate_real)=(IR_user input-i)/(1+i)",
                    source='2021 Annual Technology Baseline by NREL (National Renewable Energy Laboratory), Solar Tabs',
                    source_link='https://data.openei.org/submissions/4129',
                ),

            ),
            ContinuousInput(
                'lifetime', 'Lifetime',
                unit='years',
                defaults=[Default(30)],
                validators=[validators.integer(), validators.gte(0)],
                conditionals=[conditionals.input_equal_to('interest_rate_or_crf', 'Interest Rate')],
                tooltip=Tooltip(
                    'Plant lifetime impacts capital cost levelization (see crf equation in interest rate tooltip). Other finance cost parameters (interest rate, inflaction rate, rate of return on equity, debt fraction, tax rate, etc. for capital cost amortization and levelization) are from NREL ATB.',
                    source='ATB 2020',
                    source_link='https://atb.nrel.gov/electricity/2020/index.php?t=ei'),

            ),
        ]

        tea_only_inputs = [
            CategoricalInput(
                'gt', 'Generator Type',
                defaults=[Default('Boiler (~99% of US coal turbines)')],
                tooltip=Tooltip(
                    'For LCA & TEA, generator type impacts power plant efficiency. For TEA, generator type also impacts capacity factor and cost parameters. The generator mix varies by regions. For US average, 99% boiler, 1% IGCC. US mix average efficiency ~36% (LHV basis), capacity factor ~ 54%.',
                    source='GREET2019, EPA',
                    source_link='https://greet.es.anl.gov/; https://www.epa.gov/energy/emissions-generation-resource-integrated-database-egrid',
                )

            ),
            CategoricalInput(
                'gr', 'Region',
                defaults=[Default('US')],
                tooltip=Tooltip(
                    'For LCA & TEA, Region impacts power plant efficiency. For TEA, Region also impacts capacity factor and thus levelized capital cost. US average efficiency = 36% (LHV basis), capacity factor =54%, for a mix of generator types.  .',
                    source='GREET2019, EPA',
                    source_link='https://greet.es.anl.gov/; https://www.epa.gov/energy/emissions-generation-resource-integrated-database-egrid',
                )

            ),
            ContinuousInput(
                'transm_loss', 'Power Lost in Transmission',
                unit='%',
                defaults=[Default(4.7)],
                tooltip=Tooltip(' ', source='Average of 2018 EPA & EIA values',
                                source_link='https://greet.es.anl.gov/files/Update_td_losses_2018'),
                validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
            ),
            OptionsInput(
                'use_user_eff', 'Use User Defined Efficiency',
                options=['Yes', 'No'],
                defaults=[Default('No')],
                tooltip=Tooltip(
                    'Selection of No means efficiency is set by the region and generator type selected.',
                    source='GREET2019, EPA',
                    source_link='https://greet.es.anl.gov/; https://www.epa.gov/energy/emissions-generation-resource-integrated-database-egrid',
                )

            ),
            ContinuousInput(
                'user_eff', 'Efficiency',
                unit='%',
                defaults=[Default(36)],
                validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                conditionals=[conditionals.input_equal_to('use_user_eff', 'Yes')],
                tooltip=Tooltip(
                    'Power generated/input feed energy, on LHV (lower heating value) basis.',
                )

            ),
        ]

        if tea_lca:
            return tea_lca_inputs + CcsTea.user_inputs(source = "Coal Power Plants", tea_lca = tea_lca) + tea_lca_inputs2

        return tea_only_inputs + tea_lca_inputs + ccs_tea_only + CcsTea.user_inputs(source = "Coal Power Plants") \
               + tea_lca_inputs2

    @classmethod
    def sensitivity(cls, lca_pathway=None):
        return [
            SensitivityInput(
                'gt',
                minimizing='Boiler (~99% of US coal turbines)',
                maximizing='IGCC - Integrated Gasification Combined Cycle',
            ),
            SensitivityInput(
                'gr',
                minimizing='MRO',
                maximizing='NPCC',
            ),
            SensitivityInput(
                'plant_size',
                minimizing=1200,
                maximizing=300,
            ),
            SensitivityInput(
                'transm_loss',
                minimizing=3.3,
                maximizing=6.1,
            ),
            SensitivityInput(
                'user_trans_dist_cost',
                minimizing=14,
                maximizing=1.3*47,
            ),
            SensitivityInput(
                'use_CCS',
                minimizing='No',
                maximizing='Yes',
            ),
            SensitivityInput(
                'interest_rate',
                minimizing=2,
                maximizing=10,
            ),
            SensitivityInput(
                'lifetime',
                minimizing=40,
                maximizing=20,
            ),
            SensitivityInput(
                'user_coalprice',
                minimizing=1.4,
                maximizing=2.6,
            ),
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fuel_costs = pd.read_csv(PATH + "coal_EIA_fuelcost.csv")
        self.heatrate_cf = pd.read_csv(PATH + "coal_heatrate_cf_new.csv")
        self.other_costs = pd.read_csv(PATH + "coal_other_costs.csv")
        self.finance = pd.read_csv(PATH + "coal_finance.csv")

    def prepare(self, input_set):
        super().prepare(input_set)

        if self.lca_pathway is not None:
            process = self.lca_pathway.instance('process')
            self.gr = process.region
            if hasattr(process, 'generator_type'):
                self.gt = 'Boiler (~99% of US coal turbines)'
            else:
                self.gt = process.plant_type

            if process.use_CCS == 'Yes':
                em = process.get_emissions()
                self.ccs_carbon_intensity = process.ccs.elec_carbon_intensity
                self.CO2_captured_dict = {
                    'total': process.ccs.CO2_captured,
                    'plant': process.ccs.CO2_captured_plant,
                    'regen': process.ccs.CO2_captured_regen,
                    'comp': process.ccs.CO2_captured_comp,
                }

            gate_to_enduse = self.lca_pathway.instance('gatetoenduse')
            self.transm_loss = gate_to_enduse.loss

            setattr(self,'use_user_eff','No')

            tea_inputs = self.__class__.user_inputs()
            for input in tea_inputs:
                print(input.name)
                if hasattr(process, input.name):
                    value = getattr(process, input.name)
                    print(value,"yes")
                    setattr(self, input.name, value)
            self.coal_rank = self.lca_pathway.instance('upstream').coal_type

        else:
            setattr(self,'coal_rank','Mix')

    def get_fuel_cost(self):
        return self.user_coalprice 

    def get_generator_type(self):
        return self.gt

    def filtered_data(self):
        return self.heatrate_cf[(self.heatrate_cf["Generator Type"] == self.get_generator_type()) &
                                (self.heatrate_cf["Region"] == self.gr)]

    def get_capacity_factor(self):
        filtered = self.filtered_data()
        return float(statistics.mean(filtered['cf 2018'])) 

    def get_electricity_ci(self):
        if self.lca_pathway is None:
            filtered = self.filtered_data()
            elec_ci = float((filtered['co2emissions (kg/kWh)']))
        else:
            elec_ci = self.ccs_carbon_intensity
        return elec_ci

    def get_heat_rate(self):
        if self.use_user_eff == 'Yes':
            heat_rate = 100 / self.user_eff / 0.29307107
        else:
            filtered = self.filtered_data()
            heat_rate = float((filtered['heat rate (mmBtu/MWh)']))

        return heat_rate  

    def get_boiler_weight(self):
        filtered = self.filtered_data()
        return float((filtered['Boiler in mix']))  

    def get_igcc_weight(self):
        filtered = self.filtered_data()
        return float((filtered['IGCC in mix']))  

    def get_other_costs(self):
        turb = self.get_generator_type()
        if "Mix" in turb:
            filtered1 = self.other_costs[(self.other_costs["Turbine"] == "Boiler (~99% of US coal turbines)")]
            turbine_capital1 = float(statistics.mean(filtered1[filtered1['Cost Type'] == "OCC"].value))  
            ref_plant_size1 = float(statistics.mean(filtered1[filtered1['Cost Type'] == "OCC"].refsize))  
            adj_turbine_capital1 = ref_plant_size1/self.plant_size * turbine_capital1 * (
                    self.plant_size / ref_plant_size1) ** self.economies_of_scale_factor  
            turbine_vom1 = float(statistics.mean(filtered1[filtered1['Cost Type'] == "VOM"].value))  
            turbine_fom1 = float(statistics.mean(filtered1[filtered1['Cost Type'] == "FOM"].value))  

            filtered2 = self.other_costs[(self.other_costs["Turbine"] == "IGCC - Integrated Gasification Combined Cycle")]
            turbine_capital2 = float(statistics.mean(filtered2[filtered2['Cost Type'] == "OCC"].value))  
            ref_plant_size2 = float(statistics.mean(filtered2[filtered2['Cost Type'] == "OCC"].refsize))  
            adj_turbine_capital2 = ref_plant_size2/self.plant_size *turbine_capital2 * (
                    self.plant_size / ref_plant_size2) ** self.economies_of_scale_factor  
            turbine_vom2 = float(statistics.mean(filtered2[filtered2['Cost Type'] == "VOM"].value))  
            turbine_fom2 = float(statistics.mean(filtered2[filtered2['Cost Type'] == "FOM"].value))  


            adj_turbine_capital = (
                                              self.get_boiler_weight() * adj_turbine_capital1 + self.get_igcc_weight() * adj_turbine_capital2) / (
                                              self.get_boiler_weight() + self.get_igcc_weight())  

            turbine_vom = (self.get_boiler_weight() * turbine_vom1 + self.get_igcc_weight() * turbine_vom2) / (
                                      self.get_boiler_weight() + self.get_igcc_weight() )  

            turbine_fom = (self.get_boiler_weight() * turbine_fom1 + self.get_igcc_weight() * turbine_fom2 ) / (
                                      self.get_boiler_weight() + self.get_igcc_weight() )  

        else:
            filtered = self.other_costs[(self.other_costs["Turbine"] == self.get_generator_type())]
            turbine_capital = float(statistics.mean(filtered[filtered['Cost Type'] == "OCC"].value)) 
            ref_plant_size = float(statistics.mean(filtered[filtered['Cost Type'] == "OCC"].refsize))  
            adj_turbine_capital = ref_plant_size/self.plant_size *turbine_capital * (
                    self.plant_size / ref_plant_size) ** self.economies_of_scale_factor  
            turbine_vom = float(statistics.mean(self.other_costs[self.other_costs['Cost Type'] == "VOM"].value)) 
            turbine_fom = float(statistics.mean(self.other_costs[self.other_costs['Cost Type'] == "FOM"].value)) 

        return adj_turbine_capital, turbine_fom, turbine_vom

    def get_eqvlt_coal_rank_in_table(self):
        if 'Mix' in self.coal_rank:
            return 'Mix'
        return self.coal_rank

    def get_finance_values(self):
        finance_costs = {}
        filtered = self.finance[self.finance['Source'] == 'ATB']
        for row in filtered.to_dict(orient='records'):
            finance_costs[row['Abbr']] = float(row['Value'])
        finance_costs["i"]=self.interest_rate/100
        return finance_costs

    def get_cost_breakdown(self):
        global capture_capital, capture_fom, capture_vom, capture_transp, capture_storage, comp_choice, user_elec_price,regen_choice, parasitic_loadccs, parasitic_load_ccs
        adj_turbine_capital, turbine_fom, turbine_vom = self.get_other_costs()



        if self.interest_rate_or_crf == 'Capital Recovery Factor':
            CRF = self.crf / 100
        else:
            finance_values = self.get_finance_values()
            debt_fraction = finance_values['df']
            rate_return_equity = finance_values['rre']
            interest_rate = finance_values['i']
            inflation_rate = finance_values['ir']
            tax_rate = finance_values['tr']  
            WACC = ((1 + ((1 - debt_fraction) * ((1 + rate_return_equity) * (1 + inflation_rate) - 1)) + (
                    debt_fraction * ((1 + interest_rate) * (1 + inflation_rate) - 1) * (1 - tax_rate))) / (
                            1 + inflation_rate)) - 1
            CRF_nom = WACC / (1 - (1 / (1 + WACC) ** self.lifetime))
            PVD = 0
            for year, dep_rate in enumerate(DEPRECIATION):
                PVD += (1 / ((1 + WACC) * (1 + interest_rate)) ** year) * dep_rate
            PFF = (1 - tax_rate * PVD) / (1 - tax_rate)
            CRF=PFF*CRF_nom

        if self.use_CCS == 'Yes':

            comp_choice = 'Yes' 

            if self.storage_cost_source == 'User defined':
                user_storage_cost = self.user_storage_cost
            else:
                user_storage_cost = None

            net_operation = (self.plant_size * self.get_capacity_factor() * 8760 * 1000)

            if self.lca_pathway is None:
                self.CO2_captured_dict = None
            else:
                for key, i in self.CO2_captured_dict.items():
                    self.CO2_captured_dict[key] = self.CO2_captured_dict[
                                                      key] * net_operation / 1000  

            ccs = CcsTea( plant_type = "Coal Power Plants", plant_size = self.plant_size * self.get_capacity_factor(), 
                                 economies_of_scale_factor = self.economies_of_scale_factor,
                                  cap_percent_plant = self.cap_percent_plant,
                                 cap_percent_regen = self.cap_percent_regen,
                                storage_cost_source = self.storage_cost_source, storage_cost = user_storage_cost,
                                 crf = CRF, gr = self.gr, distance = self.pipeline_miles,
                                  electricity_ci = self.get_electricity_ci(),
                                  electricity_price = 0, natural_gas_price = 0,
                                CO2_captured = self.CO2_captured_dict, extra_inputs = {'coal_rank':self.get_eqvlt_coal_rank_in_table()})


            avg_cost_breakdown, emissions, parasitic_load_ccs, overnight_avg_cost, ccs_heat_rate = ccs.get_capture_cost_breakdown()

            capture_capital = overnight_avg_cost / (self.plant_size * 1000)  

            capture_fom = avg_cost_breakdown['Capital & Fixed']['FOM'] / net_operation  

            capture_vom = (avg_cost_breakdown['Operational']['VOM'] + avg_cost_breakdown['Operational']['Tax'])/ net_operation 

            capture_transp = avg_cost_breakdown['Operational']['Transport'] / net_operation  

            capture_storage = avg_cost_breakdown['Operational']['Storage']/ net_operation 



        elif self.use_CCS == 'No':
            capture_capital = 0
            capture_fom = 0
            capture_vom = 0
            capture_transp = 0
            capture_storage = 0
            parasitic_load_ccs = 0
            ccs_heat_rate = 0




        model = SLCOE(
                      interest=0,
                      discount=0,
                      lifetime=0,
                      fuel_cost = (1/(1 - self.transm_loss / 100) + parasitic_load_ccs) * self.get_fuel_cost(),  # USD/MMBtu 
                      CAPEX = (1/(1 - self.transm_loss / 100) + parasitic_load_ccs) * (adj_turbine_capital + capture_capital), 
                      FOM = (1/(1 - self.transm_loss / 100) + parasitic_load_ccs) * (turbine_fom + capture_fom), 
                      VOM = 1000*(1/(1 - self.transm_loss / 100) + parasitic_load_ccs) * (turbine_vom / 1000 + capture_transp + capture_storage),  
                      CF = self.get_capacity_factor(),
                      HR = self.get_heat_rate() + ccs_heat_rate, 
                      TD_cost=(1 / (1 - self.transm_loss / 100) + parasitic_load_ccs) * self.user_trans_dist_cost,  
                      CRF=CRF,
                      sale_tax_rate=self.sale_tax_rate) 


        costs = model.get_cost_breakdown()
        return {key: val for key, val in costs.items()}
