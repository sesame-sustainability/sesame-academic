
import os
import pandas as pd
import us, statistics


from core.inputs import OptionsInput, ContinuousInput, Default, CategoricalInput, Tooltip, PercentInput, Input
from core.tea import TeaBase
from core import validators, conditionals

PATH = os.getcwd() + "/tea/chemical/LNG/"

class LNGTEA(TeaBase):
    unit = '$/MMBtu'

    @classmethod
    def user_inputs(cls):
        return [
            CategoricalInput('dest','Destination',
            defaults=[Default('Shanghai')],
                     tooltip = Tooltip(
            'Default is a representative transportation cost (2.6 $/MMBTU), from US to Shanghai. Minimum cost collected so far: US to Rotterdam (1.2 $/MMBTU); maximum: US to East India (2.9 $/MMBTU)',
            source='OIES',
            source_link='https://www.oxfordenergy.org/wpcms/wp-content/uploads/2019/03/Outlook-for-Competitive-LNG-Supply-NG-142.pdf',
            )
                        ),
            ContinuousInput('Power_Price','Electricity Price',
                            unit='$/MWh',
                            defaults=[Default(88)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(1000)],
                            tooltip=Tooltip(
                                'Power is used in LNG production. This includes 66 for power generation and 14 $/MWh distribution.',
                                source='Statistica',
                                source_link='https://www.statista.com/statistics/190680/us-industrial-consumer-price-estimates-for-retail-electricity-since-1970/; https://www.eia.gov/outlooks/aeo/data/browser/
                            )
                            ),
            ContinuousInput('discount_rate', 'Discount Rate',
                            unit='%',
                            defaults=[Default(10)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                            tooltip=Tooltip(
                                'Amortized capital cost per year ($/yr) = capital recovery factor * total capital cost ($); crf = (discount_rate * ((1 + discount_rate)**lifetime)) / ((1 + discount_rate)**(lifetime) - 1). Havent found LNG-specific discount rate - using NREL biofuel project discount factor as a proxy for the default value.',
                                source='NREL 2011 biofuel as a proxy',
                                source_link='https://www.nrel.gov/docs/fy11osti/47764.pdf',
                            )
                            ),

            ContinuousInput('capacity_factor', 'Capacity Factor',
                            unit='%',
                            defaults=[Default(56)],
                            validators=[validators.numeric(), validators.gte(0), validators.lte(100)],
                            tooltip=Tooltip(
                                'Percent of the facility design capacity is used to produce product, e.g., mathematically the number of hours in a year the facility runs, divided by 24*365 hours. No LNG-specific capacity factor has been found, so the natural gas to power capacity factor is used as a proxy here.',
                                source='EIA',
                                source_link='https://www.eia.gov/todayinenergy/detail.php?id=25652
                            )
                            ),

            ContinuousInput('lifetime', 'Lifetime',
                            unit='year',
                            defaults=[Default(30)],
                            validators=[validators.integer(), validators.gte(0)],
                            tooltip=Tooltip(
                                '30 year average from OIES is also consistent with NREL ATB model defaults for most technologies, such as natural gas power plant',
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
        self.shipping_distance = pd.read_csv(PATH + "shipping.csv")
        super().__init__()


    def get_destination_type(self):
        if self.lca_pathway:
            process_user_inputs = self.lca_pathway['Process']['user_inputs']
            dest_loc = process_user_inputs.get("Destination")
        else:
            dest_loc = self.dest
        return dest_loc
    def get_cost_breakdown(self):
        dest= self.dest
        if dest == 'Rotterdam':
            index = 0
        elif dest == 'West India':
            index = 1
        elif dest == 'East India':
            index = 2
        elif dest == 'Taiwan':
            index = 3
        elif dest == 'Shanghai':
            index = 4
        elif dest == 'Beijing':
            index = 5
        elif dest == 'Osaka':
            index = 6
        elif dest == 'Tokyo':
            index = 7
        

        self.capacity_factor = self.capacity_factor/100
        self.discount_rate = self.discount_rate/100



        MMBtu_per_ton = 48.6 
        o_m = .04 
        CapEx = 660 
        CapEx_MMBtu = CapEx / MMBtu_per_ton  
        plant_size = 10000000 
        plant_size_MMBtu = plant_size * MMBtu_per_ton



    
        shipping_cost = self.shipping_distance.iloc[index,1]



        LNG_output = self.capacity_factor * plant_size_MMBtu
        LNG_input = LNG_output* (10**6+96923)/10**6 
        crf = (self.discount_rate * ((1 + self.discount_rate)**self.lifetime)) / ((1 + self.discount_rate)**(self.lifetime) - 1) 

        Overnight_CapEx = plant_size_MMBtu * CapEx_MMBtu
        annual_CapEx = Overnight_CapEx * crf

        FOM = Overnight_CapEx * o_m 

        Unit_power_cost = 1978 * self.Power_Price * 2.93*10**(-7)  
        Power_cost = Unit_power_cost*LNG_output
        Fuel_cost = LNG_input*self.ng_price
        Unit_fuel_cost = Fuel_cost/LNG_output
        total_charge = annual_CapEx + FOM +  Power_cost + Fuel_cost + shipping_cost 

        unit_cost = total_charge / (LNG_output) 

        tax = self.tax_rate*unit_cost/100 
    



        DES_cost = shipping_cost + unit_cost 

        FOB_cost = unit_cost 


        capital = {'Capital Cost': annual_CapEx / LNG_output} 
        fixed = {'FOM: Fixed Operation and Maintenance': FOM / LNG_output}
        vom = {'VOM: Power & transport': Unit_power_cost + shipping_cost }

        cost_breakdown = {"Capital": capital,
                          "Fixed": fixed,
                          "Variable": vom,
                          "Fuel": Unit_fuel_cost,
                          "tax": tax
                              }

        return cost_breakdown