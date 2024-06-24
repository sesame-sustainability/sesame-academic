from core.pathway import ActivitySource
from core.inputs import CategoricalInput, ContinuousInput, OptionsInput, Default, Tooltip
import core.conditionals as conditionals
import core.validators as validators
from tea.electricity.solar.solar_TEA import SolarTEA
from analysis.sensitivity import SensitivityInput

import pandas as pd
import os
import numpy as np

PATH = os.path.dirname(__file__)
DATA = {
    'master': pd.read_csv(os.path.join(PATH, 'solar_master_sheet.csv')),
    'ef': pd.read_csv(os.path.join(PATH, 'solar_ef.csv')),
    'param': pd.read_csv(os.path.join(PATH, 'solar_parameters.csv')),
    'cf': pd.read_csv(os.path.join(PATH, 'solar_cf_table.csv')),
}

class SolarPowerProduction(ActivitySource):

    @classmethod
    def user_inputs(cls):
        tea_inputs = SolarTEA.user_inputs(tea_only=True)
        for input in tea_inputs:
            input.conditionals.append(conditionals.context_equal_to('compute_cost', True))

        return [
            CategoricalInput(
                'location', 'Location',
                defaults=[Default('location with approximate average irradiance of US PV sites (2019)')],
                tooltip=Tooltip(
                    'Location of installed solar panels. Factors impacted by location include: sunshine, snow, optimal tilt, generation per panel, and capacity factor.',
                ),
            ),
            CategoricalInput(
                'install_type', 'Installation Type',
                defaults=[Default('utility, 1-axis tracking')],
                tooltip=Tooltip(
                    'Cumulative PV capacity in the US in 2019 was: ~40% utility-scale with panels tracking east to west, ~20% utility-scale with panels at fixed tilt, ~20% residential, and <15% commercial.',
                    source='2020 Utility-Scale Solar Data Update by Lawrence Berkeley National Laboratory, pages 8 & 14',
                    source_link='https://emp.lbl.gov/sites/default/files/2020_utility-scale_solar_data_update.pdf',
                ),
            ),
            OptionsInput(
                'cell_type', 'Cell Type',
                defaults=[Default('single Si')],
                options=['multi Si', 'single Si', 'CdTe', 'CIGS'],
                tooltip=Tooltip(
                    'Solar panels are made of cells. Different cell types have different manufacturing processes. The 3 most common cell types are single-crystal silicon (>40% of cumulative panel capacity in 2020), multi-crystal silicon (>40%), and cadmium telluride (>4%). Of the 3, single Si requires the most GHG emissions to produce, and cadmium telluride (CdTe) the least.',
                    source='2020 Photovoltaics Report by Fraunhofer Institute for Solar Energy Systems, page 21',
                    source_link='https://www.ise.fraunhofer.de/content/dam/ise/de/documents/publications/studies/Photovoltaics-Report.pdf',
                ),
            ),
            ContinuousInput(
                'efficiency', 'Rated Efficiency',
                unit='%',
                validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                defaults=[Default(20)],
                tooltip=Tooltip(
                    'Efficiency = % of sunshine (irradiance) converted to electricity by solar panel. As measured (rated) under industry standard test conditions. In 2020, efficiency of average new panels was ~20% for silicon (up from ~14% in 2010) and ~19% for CdTe (up from ~9%). In other words, efficiency changes with both time and cell type. SESAME allows the user to change efficiency independent of cell type, to explore how future rises in efficiency may impact average emissions & costs. Over time, rising efficiency reduces solar cost, because higher efficiency means less panel, less BOS, and less footprint, for the same capacity. Raising SESAME\'s efficiency input does NOT estimate the price premium of panels with above average efficiency.',
                    source='2020 Photovoltaics Report by Fraunhofer Institute for Solar Energy Systems, page 7',
                    source_link='https://www.ise.fraunhofer.de/content/dam/ise/de/documents/publications/studies/Photovoltaics-Report.pdf',
                ),
            ),
            ContinuousInput(
                'lifetime', 'Lifetime',
                unit='years',
                validators=[validators.numeric(), validators.gte(0)],
                defaults=[Default(30)],
                tooltip=Tooltip(
                    'Factors impacted by lifetime include: lifetime generation, and amortization of capital costs & emissions over that generation. 30 year lifetime is a common asumption, but uncertainty is significant because most PV systems are younger than 10 years.',
                ),
            ),
            ContinuousInput(
                'degradation', 'Degradation Rate',
                unit='%/year',
                validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                defaults=[Default(0.8)],
                tooltip=Tooltip(
                    'Reduction in efficiency, i.e. in power generation per irradiance.',
                ),
            ),
            OptionsInput(
                'shading', 'Shading Loss',
                unit='%',
                options=[0, 2.5, 5, 7.5, 10],
                defaults=[Default(2.5)],
                tooltip=Tooltip('Generation decrease due to shading.'),
            ),
            ContinuousInput(
                'ilr', 'Inverter Loading Ratio',
                validators=[validators.numeric(), validators.gte(0)],
                defaults=[Default(1.3)],
                tooltip=Tooltip(
                    "Inverters convert panels' DC power into AC power for use. Inverter loading ratio (ILR) is the ratio of [rated DC panel capacity] to [rated AC inverter capacity]. Approximately, the ratio of [panel power ouput given irradiance of 1 kW/m2] to [max inverter output]. By design, ILR is usually >1. This is called 'inverter overloading'. Because most panels in most locations only reach their rated DC capacity a small % of the year, it is usually not cost effective to size an inverter to capture this peak output. Average ILR has risen over time and slightly exceeded 1.3 for US projects built since 2014.",
                    source='2020 Utility-Scale Solar Data Update by Lawrence Berkeley National Laboratory, page 16',
                    source_link='https://emp.lbl.gov/sites/default/files/2020_utility-scale_solar_data_update.pdf',
                ),
            ),
            OptionsInput(
                'production_region', 'Production Region',
                options=['Europe', 'China'],
                conditionals=[conditionals.input_equal_to('cell_type', 'multi Si')],
                defaults=[Default('China')],
                tooltip=Tooltip(
                    'Region of panel production. Factors impacted by production region include: emissions of electricity used in production.',
                ),
            ),
            ContinuousInput(
                'panel_ghg', 'Power Emissions in Panel Production',
                unit='gCO\u2082e/kWh',
                validators=[validators.numeric(), validators.gte(0)],
                defaults=[Default(500)],
                tooltip=Tooltip(
                    'Life cycle emissions of electricity used in solar panel production. In 2020, world average lifecycle emissions of electricity were ~500 gCO2e/kWh.',
                    source='IEA Electricity Market Report - December 2020',
                    source_link='https://www.iea.org/data-and-statistics/charts/composition-of-co2-emissions-and-emission-intensity-in-2020',
                ),
            ),
            ContinuousInput(
                'bos_ghg', 'Power Emissions in BOS Production',
                unit='gCO\u2082e/kWh',
                validators=[validators.numeric(), validators.gte(0)],
                defaults=[Default(500)],
                tooltip=Tooltip(
                    'Life cycle emissions of electricity used in BOS (balance of system) production. BOS = all PV system parts except panels, e.g. mounting, inverter, wiring, etc. In 2020, world average lifecycle emissions of electricity were ~500 gCO2e/kWh.',
                    source='IEA Electricity Market Report - December 2020',
                    source_link='https://www.iea.org/data-and-statistics/charts/composition-of-co2-emissions-and-emission-intensity-in-2020',
                ),
            ),
            ContinuousInput(
                'shipping_dist', 'Shipping Distance from Panel Production to Installation',
                unit='km',
                validators=[validators.numeric(), validators.gte(0)],
                defaults=[Default(10500)],
                tooltip=Tooltip(
                    'Typical shipping distance from asia to US west ~10,500 km.',
                ),
            ),
        ] + tea_inputs

    @classmethod
    def sensitivity(cls):
        return [
            SensitivityInput(
                'location',
                minimizing='US SW (Phoenix)',
                maximizing='US NW (Seattle)',
            ),
            SensitivityInput(
                'install_type',
                minimizing='utility, 1-axis tracking',
                maximizing='residential',
            ),
            SensitivityInput(
                'cell_type',
                minimizing='CdTe',
                maximizing='single Si',
            ),
            SensitivityInput(
                'efficiency',
                minimizing=22,
                maximizing=14,
            ),
            SensitivityInput(
                'lifetime',
                minimizing=40,
                maximizing=20,
            ),
            SensitivityInput(
                'degradation',
                minimizing=0.3,
                maximizing=1.18,
            ),
            SensitivityInput(
                'shading',
                minimizing=0,
                maximizing=7.5,
            ),
            SensitivityInput(
                'ilr',
                minimizing=1.4,
                maximizing=1.0,
            ),
            SensitivityInput(
                'panel_ghg',
                minimizing=270,
                maximizing=950,
            ),
            SensitivityInput(
                'bos_ghg',
                minimizing=270,
                maximizing=950,
            ),
            SensitivityInput(
                'shipping_dist',
                minimizing=10500,
                maximizing=18000,
            ),
        ]

    def prepare(self, input_set):
        super().prepare(input_set)
        if hasattr(self, 'efficiency'):
            self.efficiency /= 100

    def get_inputs(self):
        if not hasattr(self,'results_overall'):
            _, self.results_overall = self.compute_emissions(DATA['master'].copy(), DATA['ef'].copy(), DATA['param'].copy())

        multiplier = self.output['value']
        upstream_emissions = self.get_stage_emissions('Upstream', self.results_overall)

        for name in upstream_emissions.keys():
            upstream_emissions[name] *= multiplier

        return {
            'primary': upstream_emissions,
            'secondary': []
        }

    def get_output(self):
        return self.output

    def get_emissions(self):
        multiplier = self.output['value']

        process_emissions = self.get_stage_emissions('Process', self.results_overall)
        emission_flows = {}
        for substage in process_emissions:
            emission_flows[substage] = {
                'co2': {'name': 'co2', 'unit': 'gCO\u2082e/kWh', 'value': process_emissions[substage] * multiplier}}

        return emission_flows

    def amount_factor(self, amounts, col_index):
        mf = 1
        l = len(amounts.columns)
        for i in range(col_index + 1, l - 5):
            ix_row = np.where(amounts.input == amounts.columns.values[i - 1])[0]
            a = amounts.iloc[ix_row, i].values
            mf = mf * a

        b = amounts.loc[amounts.input == amounts.columns.values[l - 2], amounts.columns.values[l - 1]].values
        c = amounts.loc[amounts.input == amounts.columns.values[l - 6], amounts.columns.values[l - 2]].values

        if col_index < l - 5:
            mf = mf * b * c
        elif col_index < l - 2:
            ix_row = np.where(amounts.input == amounts.columns.values[col_index])[0]
            a = amounts.iloc[ix_row, l - 2].values
            mf = mf * a * b
        elif col_index == l - 2:
            mf = mf * b

        if mf == 1:
            mf = [1]
        return mf[0]

    def panel_install(self, params):
        i = 0 if self.install_type == 'residential' else 1
        a_pi = self.ilr * float(params['Value'][i]) / (float(params['Value'][2]) * self.efficiency) * (
                1 + float(params['Value'][6]) + float(0.02 * self.lifetime / 30))
        return a_pi

    def mount_install(self, a_pi, params):
        a_mi = a_pi / (1 + float(params['Value'][6]) + float(params['Value'][7]) * self.lifetime)
        return a_mi

    def powerplant_operation(self, CF, params):
        i = 0 if self.install_type == 'residential' else 1
        a_ppo = 1 / (CF * float(params['Value'][i]) * self.lifetime)
        return a_ppo

    def transportation(self, a_pi, a0, areal_density):
        a_transport = a0 + a_pi * 0.001 * self.shipping_dist * areal_density
        return a_transport

    def compute_cap_fac(self, cf_table):
        assumed_loss = 0.03
        tec = 0.4223  

        pat = ' Si' if 'Si' in self.cell_type else ' TF'
        column_key = self.install_type + pat
        cf_row = cf_table.loc[cf_table['Location'] == self.location]
        cf_loc = cf_row[column_key].values
        snow_loss = cf_row['snow loss if any (%)'].values
        CF_AC = (cf_loc * (1 - snow_loss) * (1 - self.shading/100) * (1 - self.lifetime * self.degradation / 200) / (
                1 - assumed_loss) - 100 * tec / self.efficiency / 8760) * self.ilr
        CF_DC = CF_AC / self.ilr
        CF_AC_per_cap = CF_AC * 87.6

        cap_fac = np.concatenate((CF_AC, CF_DC, CF_AC_per_cap), axis=None)
        return cap_fac

    def compute_emissions(self, master, ef, params):

        ef.iloc[0, -1] = self.panel_ghg / 1000

        pat1 = ''
        if self.install_type == 'residential':
            pat1 += 'rooftop'
        else:
            pat1 += self.install_type

        pat2 = ''
        if self.cell_type == 'multi Si':
            pat2 += f'multi crystal Si'
        elif self.cell_type == 'single Si':
            pat2 += 'single crystal Si'
        else:
            pat2 += self.cell_type
        pat2 += ' '

        if self.cell_type == 'multi Si':
            pat2 += self.production_region

        columns = master.columns.values

        relevant_install_columns = columns[[i for i, item in enumerate(columns) if pat1 in item]]
        relevant_cell_columns = columns[[i for i, item in enumerate(columns) if pat2 in item]]
        relevant_columns = np.concatenate(('input', relevant_cell_columns, relevant_install_columns), axis=None)
        amounts = master.filter(relevant_columns, axis=1)
        CF = self.compute_cap_fac(DATA['cf'].copy())

        a_pi = self.panel_install(params)
        a_mi = self.mount_install(a_pi, params)
        a_ppo = self.powerplant_operation(CF[2], params)
        a0_transport = amounts.loc[amounts.input == 'transoceanic freight ship', relevant_install_columns[-2]].values
        a_transport = self.transportation(a_pi, a0_transport,
                                          float(params.loc[params['Parameter Abbreviation'] == 'ad', 'Value'].values))

        amounts.loc[amounts.input == relevant_cell_columns[-1], relevant_install_columns[-2]] = a_pi
        amounts.loc[amounts.input == relevant_install_columns[2], relevant_install_columns[-2]] = a_mi
        amounts.loc[amounts.input == relevant_install_columns[-2], relevant_install_columns[-1]] = a_ppo
        amounts.loc[amounts.input == 'transoceanic freight ship', relevant_install_columns[-2]] = a_transport
        ghg = amounts.copy()
        results_index = ['GHG Emissions by stage product (including previous stages)',
                         'GHG Emissions by stage product (excluding previous stages)',
                         'GHG Emissions (including previous stages)', 'GHG Emissions (excluding previous stages)',
                         'Stage']
        results = pd.DataFrame(index=results_index, columns=relevant_columns)

        l = len(amounts.columns)
        results.iloc[4, 1:l - 2] = ['Upstream'] * (l - 3)
        results.iloc[4, l - 2:l] = ['Process'] * (2)

        for (columnName, columnData) in amounts.iteritems():
            if columnName == 'input':
                continue
            col_index = amounts.columns.get_loc(columnName)

            if col_index < l - 5:
                ef.iloc[0, -1] = self.panel_ghg / 1000

            else:
                ef.iloc[0, -1] = self.bos_ghg / 1000

            val = amounts[columnName].mul(ef['values'], 1)
            ghg.loc[:, columnName] = list(val)
            calc_sum = ghg[columnName].sum()

            results.loc['GHG Emissions by stage product (including previous stages)', columnName] = calc_sum
            results.loc['GHG Emissions by stage product (excluding previous stages)', columnName] = calc_sum - ghg.loc[
                                                                                                               39:60,
                                                                                                               columnName].sum()
            mf = self.amount_factor(amounts, col_index)

            results.loc['GHG Emissions (including previous stages)', columnName] = calc_sum * mf
            if col_index == 1 or col_index == l - 3 or col_index == l - 4 or col_index == l - 5:
                results.loc['GHG Emissions (excluding previous stages)', columnName] = calc_sum * mf
            elif col_index == l - 1 or col_index == l - 2:
                results.loc['GHG Emissions (excluding previous stages)', columnName] = calc_sum * mf - results.loc[
                    'GHG Emissions (excluding previous stages)', amounts.columns.values[1: col_index]].sum()
            else:
                results.loc['GHG Emissions (excluding previous stages)', columnName] = calc_sum * mf - results.loc[
                    'GHG Emissions (including previous stages)', amounts.columns.values[col_index - 1]]

            if 'operation' in columnName:
                continue
            else:
                ef.loc[ef.input == columnName, 'values'] = calc_sum
        return ghg, results

    def get_stage_emissions(self, stage, results):
        stage_emissions = {}
        last_two = results.loc[['GHG Emissions (excluding previous stages)', 'Stage']].to_dict()
        for sub_stage, value_dict in last_two.items():
            if sub_stage != 'input':
                if value_dict['Stage'] == stage:
                    stage_emissions[sub_stage] = value_dict['GHG Emissions (excluding previous stages)']
        return stage_emissions
