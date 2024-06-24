import os
import pandas as pd
import numpy as np
import math

from core import conditionals, validators
from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput
from core.tea import TeaBase
from analysis.sensitivity import SensitivityInput

PATH = os.path.dirname(__file__)
DATA = {
    'cf': pd.read_csv(os.path.join(os.getcwd(), 'pathway', 'process', 'solar', 'solar_cf_table.csv')),
    'ATB' : pd.read_csv(os.path.join(os.getcwd(), 'tea', 'electricity', 'solar', 'ATB.csv'), index_col = 0),
}

class SolarTEA(TeaBase):
    unit = '$/MWh'

    @classmethod
    def user_inputs(cls, tea_only=False):
        tea_only_inputs = [
            ContinuousInput(
                'interest_rate', 'Interest Rate, Nominal',
                unit='%/year',
                defaults=[Default(4)],
                tooltip=Tooltip(
                    "Interest rate determines the cost of financing powerplant construction, in combination with other financial variables. These include inflation rate (assumed at 2.5%), tax rate (26%), debt share of financing (70-80%), and nominal rate of return (7-9%). Exact values of financial variables depend on user inputs (e.g. utility vs. residential) and are sourced from NREL's ATB.",
                    source='2021 Annual Technology Baseline by NREL (National Renewable Energy Laboratory), Solar Tabs',
                    source_link='https://data.openei.org/submissions/4129',
                ),
            ),

            ContinuousInput(
                'size', 'System Capacity DC',
                unit='MW',
                validators=[validators.numeric(), validators.gte(5), validators.lte(2000)],
                defaults=[Default(40)],
                conditionals=[conditionals.input_not_equal_to('install_type', 'residential')],
                tooltip=Tooltip(
                    'DC capacity = DC output of panels given irradiance of 1 kW/m2 and industry standard testing conditions. AC capacity = rated max power output of inverter(s). Average DC capacity of new utility PV projects in 2019 was ~40 MW. Average DC capacity of new residential PV projects in 2018 was 6 kW.',
                    source='2020 Utility-Scale Solar Data Update by Lawrence Berkeley National Laboratory, page 19',
                    source_link='https://emp.lbl.gov/sites/default/files/2020_utility-scale_solar_data_update.pdf',
                ),
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
                'tax_rate', 'Tax',
                unit='%',
                defaults=[Default(6.35)],
                validators=[validators.numeric(), validators.gt(0), validators.lt(100)],
                tooltip=Tooltip(
                    "The default value represents sales tax, which varies by states and specific use cases. 6.35% represents US averegae sales tax. For electricity-specific tax, 7% was found for North Carolina, and 6.25% for Texas non-residential use: https://comptroller.texas.gov/taxes/publications/96-1309.pdf.",
                    source_link='https://www.ncdor.gov/taxes-forms/sales-and-use-tax/electricity
                ),
            ),
        ]

        if tea_only:
            return tea_only_inputs

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
                   CategoricalInput(
                       'cell_type', 'Cell Type',
                       defaults=[Default('single Si')],
                       tooltip=Tooltip(
                           'Solar panels are made of cells. Different cell types have different manufacturing processes. The 3 most common cell types are single-crystal silicon (>40% of cumulative panel capacity in 2020), multi-crystal silicon (>40%), and cadmium telluride (>4%). Of the 3, single Si requires the most GHG emissions to produce, and cadmium telluride (CdTe) the least.',
                           source='2020 Photovoltaics Report by Fraunhofer Institute for Solar Energy Systems, page 21',
                           source_link='https://www.ise.fraunhofer.de/content/dam/ise/de/documents/publications/studies/Photovoltaics-Report.pdf',
                       ),
                   ),
                   PercentInput(
                       'efficiency', 'Rated Efficiency',
                       unit='%',
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
                   ContinuousInput(
                       'transm_loss', 'Power Lost in Transmission',
                       unit='%',
                       defaults=[Default(4.7)],
                       tooltip=Tooltip(' ', source='Average of 2018 EPA & EIA values',
                                       source_link='https://greet.es.anl.gov/files/Update_td_losses_2018'),
                       validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                   ),
               ] + tea_only_inputs

    @classmethod
    def sensitivity(cls, lca_pathway=None):
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
                'size',
                minimizing=100,
                maximizing=5,
            ),
            SensitivityInput(
                'interest_rate',
                minimizing=2,
                maximizing=6,
            ),
            SensitivityInput(
                'transm_loss',
                data_lacking=True,
            ),
        ]

    def prepare(self, input_set):
        super().prepare(input_set)

        if self.lca_pathway is not None:
            gate_to_enduse = self.lca_pathway.instance('gatetoenduse')
            self.transm_loss = gate_to_enduse.loss

            process = self.lca_pathway.instance('process')
            tea_inputs = self.__class__.user_inputs()
            for input in tea_inputs:
                if hasattr(process, input.name):
                    value = getattr(process, input.name)
                    setattr(self, input.name, value)
        else:
            if hasattr(self, 'efficiency'):
                self.efficiency /= 100

    def get_lcoe(self):
        if self.cell_type == 'single Si' or self.cell_type == 'multi Si' or self.cell_type == 'Si':
            self.cell_type = 'Si'
        else:
            self.cell_type = 'TF'

        if self.install_type == 'utility, 1-axis tracking':
            self.install_type = 'util_track'
        elif self.install_type == 'utility, fixed tilt':
            self.install_type = 'util_fixed'
        else:
            self.install_type = 'res'
        tec=0.4223 

        if 'Si' in self.cell_type:
            pat = ' Si'
        else:
            pat = ' TF'

        if self.install_type == 'util_track':
            pat2 = 'utility, 1-axis tracking'
        elif self.install_type == 'res':
            pat2 = 'residential'
        elif self.install_type == 'util_fixed':
            pat2 = 'utility, fixed tilt'

        column_key = pat2 + pat
        cf_row = DATA['cf'].loc[DATA['cf']['Location'] == self.location]

        cf_loc = cf_row[column_key].values
        cf_loc = float(cf_loc)
        snow_loss = cf_row['snow loss if any (%)'].values
        CF_DC_1 = cf_loc * (1 - snow_loss / 100)
        CF_DC_2 = CF_DC_1 * (1 - float(self.shading) / 100)
        CF_DC = CF_DC_2 * (1 - float(self.lifetime) * float(self.degradation) / 100 / 2)

        if self.install_type == 'util_track':
            CF_DC = CF_DC - 100 * tec / self.efficiency / 8760

        CF_DC = CF_DC / 100
        CF_AC = CF_DC * float(self.ilr)
        if self.install_type == 'res':
            CF = CF_DC
        elif self.install_type == 'util_fixed' or self.install_type == 'util_track':
            CF = CF_AC
        column_name = 'PV_' + self.install_type + '_' + self.cell_type + '_2021'
        VOM_non_fuel = float(DATA['ATB'].loc['VOM_non_fuel', column_name])
        VOM_fuel = float(DATA['ATB'].loc['VOM_fuel', column_name])
        LCOE_VOM = VOM_non_fuel + VOM_fuel
        FOM = float(DATA['ATB'].loc['FOM', column_name])
        LCOE_FOM = FOM / (float(CF) * 8760)
        OCC = float(DATA['ATB'].loc['OCC', column_name])

        CapRegMult = float(DATA['ATB'].loc['CapRegMult', 'all'])
        L = self.lifetime
        GF = float(DATA['ATB'].loc['GF', column_name])
        OnSpurCost = float(DATA['ATB'].loc['OnSpurCost', column_name])
        OffSpurCost = float(DATA['ATB'].loc['OffSpurCost', column_name])
        GCC = GF + OnSpurCost + OffSpurCost
        i = float(DATA['ATB'].loc['i', 'all'])
        IR_nom = self.interest_rate/100
        IR = (IR_nom - i) / (1 + i)
        TR = float(DATA['ATB'].loc['TR', 'all'])
        DF = float(DATA['ATB'].loc['DF', column_name])
        RROE_nom = float(DATA['ATB'].loc['RROE_nom', column_name])
        RROE = (RROE_nom - i) / (1 + i)
        WACC = ((1+((1-DF)*((1+RROE)*(1+i)-1)) + (DF*((1+IR)*(1+i)-1)*(1-TR))) / (1+i)) - 1
        CRF = WACC / (1 - (1 / (1 + WACC)**L))
        M = float(DATA['ATB'].loc['M', column_name])
        FD_y1 = float(DATA['ATB'].loc['FD_y.1', column_name])
        FD_y2 = float(DATA['ATB'].loc['FD_y.2', column_name])
        FD_y3 = float(DATA['ATB'].loc['FD_y.3', column_name])
        FD_y4 = float(DATA['ATB'].loc['FD_y.4', column_name])
        FD_y5 = float(DATA['ATB'].loc['FD_y.5', column_name])
        FD_y6 = float(DATA['ATB'].loc['FD_y.6', column_name])

        f_y1 = 1 / ((1 + WACC) * (1 + i))**1
        f_y2 = 1 / ((1 + WACC) * (1 + i))**2
        f_y3 = 1 / ((1 + WACC) * (1 + i))**3
        f_y4 = 1 / ((1 + WACC) * (1 + i))**4
        f_y5 = 1 / ((1 + WACC) * (1 + i))**5
        f_y6 = 1 / ((1 + WACC) * (1 + i))**6

        PVD = FD_y1 * f_y1 + FD_y2 * f_y2 + FD_y3 * f_y3 + FD_y4 * f_y4 + FD_y5 * f_y5 + FD_y6 * f_y6
        ProFinFactor = (1 - TR * PVD) / (1 - TR)

        FRC = CRF * ProFinFactor
        C = float(DATA['ATB'].loc['C', column_name])
        FC = float(DATA['ATB'].loc['FC', column_name])
        LDC = float(DATA['ATB'].loc['LDC', 'all'])

        IDC = float(DATA['ATB'].loc['IDC', column_name])

        AI = 1 + ((1 + IDC) ** (0+0.5) - 1)
        EDC = 1 - LDC

        EPC = DATA['ATB'].loc['EPC', 'all']
        CEC = EPC + RROE_nom
        AEC = 1 + ((1 + CEC) ** (0 + 0.5) - 1)
        ConFinFactor = (FC * AI * LDC) + (FC * AEC * EDC)
        CAPEX = (OCC * CapRegMult + GCC) * ConFinFactor
        LCOE_capex = FRC * CAPEX / (CF * 8760) 
        LCOE = LCOE_capex + LCOE_FOM + LCOE_VOM 
        if self.install_type != 'res':
            LCOE_capex = LCOE_capex * (-0.1 * math.log(self.size / 100) + 1)
            LCOE_FOM = LCOE_FOM * (-0.1 * math.log(self.size / 100) + 1)
            LCOE_VOM = LCOE_VOM * (-0.1 * math.log(self.size / 100) + 1)
        efficiency_ref = 0.20
        LCOE_capex = LCOE_capex * efficiency_ref / self.efficiency
        LCOE_FOM = LCOE_FOM * efficiency_ref / self.efficiency
        LCOE_VOM = LCOE_VOM * efficiency_ref / self.efficiency

        tax = float(self.tax_rate/100 * 1000*(LCOE_capex + LCOE_FOM +LCOE_VOM + self.user_trans_dist_cost/1000))

        cost_breakdown = {"Capital": 1/(1 - self.transm_loss / 100) * float(LCOE_capex) * 1000, 
                          "Fixed": 1/(1 - self.transm_loss / 100) * float(LCOE_FOM) * 1000, 
                          "Fuel": 0,
                          "Non-fuel variable": 1/(1 - self.transm_loss / 100) * float(float(LCOE_VOM) * 1000), 
                          "Delivery": 1/(1 - self.transm_loss / 100) * self.user_trans_dist_cost, 
                          "Tax": 1/(1 - self.transm_loss / 100) * float(tax) 
                          }
        return cost_breakdown

    def get_cost_breakdown(self):
        solar_lcoe = self.get_lcoe()
        return solar_lcoe
