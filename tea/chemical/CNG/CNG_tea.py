


import os
import pandas as pd
import us, statistics


from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from core.tea import TeaBase
from core import validators, conditionals

PATH = os.getcwd() + "/tea/chemical/CNG/"

class CNGTEA(TeaBase):
    unit = '$/MMBtu'

    @classmethod
    def user_inputs(cls):
        return [
            ContinuousInput('CNG_size', 'CNG Compression Station Size',
                            unit='GGE/hr',
                            defaults=[Default(2.5)],
                            validators=[validators.numeric(), validators.gte(0)],
                            tooltip=Tooltip(
                            'Capital cost accounted for in the model includes only compressor cost. Reliable non-compressor cost data have not been found; the only paper we found quoted that cost but was not clear on the corresponding facility size. See more details in the back end code. CNG facility size influences the capital cost due to economy of scale: Capital cost for Capacity X = capital cost for base capacity*(X/base capacity)^0.6. Average of the high (4 GGE/hr) and low (1 GGE/hr) capacity from the NREL source. GGE=Gasoline Gallon Equivalent. Also note CNG transportation cost is not included, assuming compression and end use are closely located. GREET model includes transportation distance and modes for all the major fuel products, except CNG transportation likely for the same reason.',
                            source='NREL',
                            source_link='https://www.nrel.gov/docs/fy14osti/62421.pdf',
                        )
                            ),
            ContinuousInput('power_price', 'Electricity Price',
                            unit='$/MWh',
                            defaults=[Default(80)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(1000)],
                            tooltip=Tooltip(
                                'Power is used in CNG production. This includes power generation (66) and distribution cost (14 $/MWh)',
                                source='Statistica',
                                source_link='https://www.statista.com/statistics/190680/us-industrial-consumer-price-estimates-for-retail-electricity-since-1970/; https://www.eia.gov/outlooks/aeo/data/browser/
                            )
                            ),
            ContinuousInput('discount_rate', 'Discount Rate',
                            unit='%',
                            defaults=[Default(10)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                            tooltip=Tooltip(
                                'Amortized capital cost per year ($/yr) = capital recovery factor * total capital cost ($); crf = (discount_rate * ((1 + discount_rate)**lifetime)) / ((1 + discount_rate)**(lifetime) - 1). Havent found CNG-specific discount rate - using NREL biofuel project discount factor as a proxy for the default value.',
                                source='NREL 2011 biofuel as a proxy',
                                source_link='https://www.nrel.gov/docs/fy11osti/47764.pdf',
                            )
                            ),

            ContinuousInput('capacity_factor', 'Capacity Factor',
                            unit='%',
                            defaults=[Default(56)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                            tooltip=Tooltip(
                                'Percent of the facility design capacity is used to produce product, e.g., mathematically the number of hours in a year the facility runs, divided by 24*365 hours. No CNG-specific capacity factor has been found, so the natural gas to power capacity factor is used as a proxy here.',
                                source='EIA',
                                source_link='https://www.eia.gov/todayinenergy/detail.php?id=25652
                            )
                            ),

            ContinuousInput('lifetime', 'Lifetime',
                            unit='year',
                            defaults=[Default(30)],
                            validators=[validators.integer(), validators.gte(0)],
                            tooltip=Tooltip(
                                'Assumed the same 30 years by default as LNG given similarity of facilities. 30-year lifetime is also consistent with NREL ATB model defaults for most technologies, such as natural gas power plant',
                                source='OIES',
                                source_link='https://www.oxfordenergy.org/wpcms/wp-content/uploads/2018/02/The-LNG-Shipping-Forecast-costs-rebounding-outlook-uncertain-Insight-27.pdf',
                            )
                            ),

            ContinuousInput('ng_price', 'Natural Gas Price',
                            unit='$/MMBtu',
                            defaults=[Default(3.9)],
                            validators=[validators.integer(), validators.gte(0)],
                            tooltip=Tooltip(
                                'Cost of the natural gas used as feedstock and energy source in the LNG production process. Note: this default represents price of natural gas sold to industrial users, which is different from the price sold to electric power producers (2.99 $/MMBTU, a 23% difference from the Industrial Price)',
                                source='EIA US 2019 value',
                                source_link='https://www.eia.gov/dnav/ng/ng_pri_sum_a_EPG0_PIN_DMcf_a.htm',
                            )
                            ),
            ContinuousInput(
                'tax_rate', 'Tax',
                unit='%',
                defaults=[Default(6.35)],
                validators=[validators.numeric(), validators.gt(0), validators.lt(100)],
                tooltip=Tooltip(
                    "The default value represents sales tax, which varies by states and specific use cases. 6.35% represents US averegae sales tax.",
                ),
            ),
            
                ]


    def __init__(self, lca_pathway=None):
        self.lca_pathway = lca_pathway
        super().__init__()
        
    def get_cost_breakdown(self):

        MMBtu_per_GGE = 0.114 # LHV conversion based on 983 Btu/scf (LHV for natural gas) and 1 GGE = 126 scf from: https://www.nat-g.com/why-cng/cng-units-explained/
        o_m = .01 
        non_compressor_CapEx = 0 
        power_consumption_factor = 0.8 
        power_consumption = power_consumption_factor * self.CNG_size
        base_CapEx = 13000 
        base_CNG_size = (1 + 4) / 2 
        scaling_factor = 0.75 
        
        
        self.capacity_factor = self.capacity_factor/100
        self.discount_rate = self.discount_rate/100
        hours_operation = 8760 * self.capacity_factor 
        CNG_Output = hours_operation * self.CNG_size * MMBtu_per_GGE
        CNG_input = CNG_Output 
        
        
        crf = (self.discount_rate * ((1 + self.discount_rate)**self.lifetime)) / ((1 + self.discount_rate)**(self.lifetime) - 1) 
        
        Overnight_CapEx = base_CapEx * (self.CNG_size / base_CNG_size) ** scaling_factor 
        annual_CapEx = (Overnight_CapEx + non_compressor_CapEx) * crf
        
        FOM = (Overnight_CapEx + non_compressor_CapEx) * o_m 
        
        Power_cost = (self.power_price/1000) * power_consumption * self.capacity_factor * 8760

        Fuel_cost = CNG_input*self.ng_price
        Unit_fuel_cost = Fuel_cost/CNG_Output

        shipping_cost = 0
        total_charge = annual_CapEx + FOM + Power_cost + Fuel_cost + shipping_cost 
        unit_cost = total_charge / (CNG_Output) 

        tax = self.tax_rate*unit_cost/100 


        capital = {'Capital Cost': annual_CapEx / CNG_Output} 
        fixed = {'FOM: Fixed Operation and Maintenance': FOM / CNG_Output}
        vom = {'VOM: Power & transport': Power_cost / CNG_Output + shipping_cost }



        cost_breakdown = {"Capital": capital,
                          "Fixed": fixed,
                          "Variable": vom,
                          "Fuel": Unit_fuel_cost,
                          "tax": tax
                              }

        return cost_breakdown