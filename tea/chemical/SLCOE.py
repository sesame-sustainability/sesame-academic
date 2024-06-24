"""
Created on Thursday Dec 27 15:36:50 2019

Simplified levelized cost of electricity

@author: MITEI-SESAME NS Goteti
"""


class SLCOE:
    """
    Attributes:
        interest - interest rate (no units)
        Discount - discount rate (no units)
        lifetime- lifetime of power plants in years
        CAPEX- Capital cost in $/kW
        FOM - Fixed O &M in $/KW-yr
        VOM - Variable operating cost in $/kWh
        CF - Capacity Factor (No units)
        HR - Heat Rate in MMBtu/kWh
        Fuel - Fuel cost in $/MMBtu
    """

    def __init__(self, fuel_cost, CAPEX, FOM, VOM, CF, taxes, transportation):
        self.fuel_cost = fuel_cost
        self.CAPEX = CAPEX
        self.FOM = FOM
        self.VOM = VOM
        self.CF = CF
        self.taxes = taxes
        self.transportation = transportation

    def get_cost_breakdown(self):
        capital_fixed = self.CAPEX
        maintenance = self.VOM
        operational = self.fuel_cost
        taxes = self.taxes
        transportation = self.transportation

        SLCOE = capital_fixed + maintenance + operational + taxes + transportation

        profit_margin = SLCOE * .2273559 

        cost_breakdown = {
                          "Capital": capital_fixed,
                          "Other Operating and Maintenance": maintenance,
                          "Operational": operational,
                          "Taxes": taxes,
                          "Transportation": transportation
                          }
        return cost_breakdown
