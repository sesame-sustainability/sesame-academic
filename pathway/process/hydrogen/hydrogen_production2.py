from core.pathway import ActivitySource
from core.inputs import CategoricalInput, ContinuousInput, OptionsInput, Default, Tooltip
from tea.chemical.hydrogen.hydrogen_tea import HydrogenTEA
from analysis.lca import compute_input_flows, compute_emission_flows, adjust_emissions_electricity, compute_grid_intensity, compute_elec_input_flows
import core.validators as validators
import core.conditionals as conditionals
import os
import pandas as pd
import numpy as np
from analysis.sensitivity import SensitivityInput

import pathway.process.hydrogen.ccs as ccs

PATH = os.getcwd() + "/pathway/process/hydrogen/"


class HydrogenProduction(ActivitySource):

    @classmethod
    def base_inputs(cls, co_produce_steam_default='Yes'):
        return [
            CategoricalInput(
                'plant_type', 'Plant Type',
                defaults=[Default('Central Plants')],
            ),
            CategoricalInput(
                'h2_phase', 'Hydrogen Phase',
                defaults=[Default('Gas')],
            ),
            CategoricalInput(
                'co_produce_steam', 'Co-produce Steam',
                defaults=[Default(co_produce_steam_default)],
            ),
            CategoricalInput(
                'model_source', 'Basis of H2 Production Assumptions',
                defaults=[Default('Industry data')],
            ),
        ]

    def prepare(self, input_set):
        self.use_CCS = 'No'
        super().prepare(input_set)

    def get_inputs(self, input_flow):
        flow_dict = compute_input_flows(
            self.filtered_data_frame(),
            flow_output=self.output
        )
        if input_flow == 'natural gas':
            flow_dict['natural gas']['value'] += flow_dict['natural gas: process fuel']['value']

        if self.use_CCS == 'Yes':
            self.get_emissions(CCS_input = False)
            CCS_inputs = pd.read_csv(PATH + "hydrogen_ccs_lcidata.csv")
            filtered = CCS_inputs[CCS_inputs['technology'] == self.ccs.technology]
            nat_gas_ccs = float(filtered[filtered['flows'] == "natural gas"].iloc[0].value)
            electricity_ccs = float(filtered[filtered['flows'] == "electricity"].iloc[0].value)

            mj_in_kwh = 3.6

            flow_dict['natural gas']['value'] += self.ccs.CO2_captured * nat_gas_ccs
            flow_dict['electricity']['value'] += self.ccs.CO2_captured * electricity_ccs

        return {
            'primary': flow_dict[input_flow],
            'secondary': {key : flow_dict[key] for key in flow_dict if key != input_flow}
        }

    def get_emissions(self, CCS_input = True):
        if self.use_CCS != 'Yes':
            df = self.filtered_data_frame()
            emissions = compute_emission_flows(
                df,
                flow_output=self.output)
        else:
            emissions = compute_emission_flows(
                self.filtered_data_frame(),
                flow_output=self.output,
            )
            print(emissions)
            grid_intensity = compute_grid_intensity(
                self.filtered_data_frame(),
                flow_output=self.output,
            )

            self.ccs = ccs.CCS(self.input_set, self.filtered_data_frame(), emissions)
            self.ccs.run(grid_intensity)

        return emissions



class HydrogenProductionSMR(HydrogenProduction):
    filters = [
        ('Feedstock Source', 'North American Natural Gas')
    ]

    pt = 'SMR'

    @classmethod
    def user_inputs(cls):
        tea_inputs = HydrogenTEA.user_inputs(tea_lca=True, prod_type='SMR')

        for input in tea_inputs:
            if input.name == 'Gas_Cost':
                input.conditionals.pop(0)
                input.conditionals.pop(0)
            input.conditionals.append(conditionals.context_equal_to('compute_cost', True))

        return cls.base_inputs() + ccs.user_inputs(user_ci_default=460)  + tea_inputs

    def get_inputs(self):
        return super().get_inputs('natural gas')


class HydrogenProductionElec(HydrogenProduction):
    filters = [
        ('Feedstock Source', 'Electrolysis')
    ]

    pt = 'Electrolysis'

    @classmethod
    def user_inputs(cls):
        cls.use_CCS = 'No'
        tea_inputs = HydrogenTEA.user_inputs(tea_lca=True, prod_type='Electrolysis')

        for input in tea_inputs:
            input.conditionals.append(conditionals.context_equal_to('compute_cost', True))


        return cls.base_inputs(co_produce_steam_default='No') + [
            OptionsInput(
                'power_source', 'Power Source (for Carbon Intensity)',
                options=['Renewable / Nuclear Electricity', 'US Grid Average', 'Coal', 'Custom'],
                defaults=[Default('US Grid Average')],
                tooltip=Tooltip(
                    'The carbon intensity reflects the amount of CO\u2082 released per unit of electricity produced. It widely differs with the electricity production type - renewables have a very low carbon intensity, contrary to coal. Choose Custom to input your value',
                ),
            ),
            ContinuousInput(
                'custom_power_source_ci', 'Input a Custom Power Source Carbon Intensity',
                unit='gCO\u2082/kWh',
                defaults=[Default(480)],
                conditionals=[conditionals.input_equal_to('power_source', 'Custom')],
                validators=[validators.numeric(), validators.gte(0), validators.lte(1500)],
                tooltip=Tooltip(
                    'Insert your own electricity carbon intensity',
                ),
            )
        ] + tea_inputs

    def get_inputs(self):
        return super().get_inputs('electricity')

    def get_emissions(self):
        emissions = super().get_emissions()

        if self.use_CCS != 'Yes':
            if self.power_source != 'US Grid Average':
                    if self.power_source == 'Custom':
                        for activity in emissions:
                            for flow in emissions[activity]:
                                emissions[activity][flow]['value'] *= self.custom_power_source_ci/480
                                
                                
                    else:    
                        power_source_carbon_intensity = {
                            'Renewable / Nuclear Electricity': 22/480,
                            'Coal'                           : 1097/480
                        }
                        for activity in emissions:
                            for flow in emissions[activity]:
                                emissions[activity][flow]['value'] *= power_source_carbon_intensity[self.power_source]

        return emissions


class HydrogenProductionCoal(HydrogenProduction):
    filters = [
        ('Feedstock Source', 'Coal')
    ]

    @classmethod
    def user_inputs(cls):
        return cls.base_inputs()

    def get_inputs(self):
        return super().get_inputs('coal')
