#This should retire due to incorrectness and inconsistency!


class SLCOE:
    """
    Attributes:
        interest - interest rate (no units)
        discount - discount rate (no units)
        lifetime- lifetime of power plants in years
        CAPEX- Capital cost in $/kW
        FOM - Fixed O &M in $/KW-yr
        VOM - non-fuel variable operating cost in $/MWh
        CF - Capacity Factor (No units)
        HR - Heat Rate in MMBtu/MWh
        Fuel - Fuel cost in $/MMBtu
        TD_cost - transmission & distribution cost ($/MWh)
    """

    def __init__(self, interest, discount, lifetime, fuel_cost, CAPEX, FOM, VOM, CF, HR, TD_cost, CRF = None,sale_tax_rate=0):
        self.interest = interest
        self.discount = discount
        self.lifetime = lifetime
        self.fuel_cost = fuel_cost
        self.CAPEX = CAPEX
        self.FOM = FOM
        self.VOM = VOM
        self.CF = CF
        self.HR = HR
        self.TD_cost = TD_cost
        self.CRF = CRF
        self.sale_tax_rate = sale_tax_rate #% This is the electricity sales tax rate, not the one used for levelized capital cost calculation

    def get_cost_breakdown(self):
        real_discount = (self.interest + self.discount)/100
        if self.CRF is not None:
            CRF = self.CRF
        else:
            CRF = real_discount * (1 + real_discount)**self.lifetime/((1 + real_discount) ** self.lifetime-1)

        capital = (CRF * self.CAPEX ) *1000/ (8760 * self.CF) #$/MWh

        fixed_om_cost = self.FOM*1000 / (8760 * self.CF)  # USD/MWh
        var_om_cost = self.VOM  # USD/MWh
        TDcost = self.TD_cost # USD/MWh
        fuel_cost = (self.HR * self.fuel_cost)  #USD/MWh
        tax = self.sale_tax_rate/100*(capital + fixed_om_cost + var_om_cost + fuel_cost + TDcost)
        SLCOE = capital + fixed_om_cost + var_om_cost + fuel_cost #USD/MWh

        cost_breakdown = {"Capital": capital,
                          "Fixed": fixed_om_cost,
                          "Fuel": fuel_cost,
                          "Non-fuel variable": var_om_cost,
                          "Delivery": TDcost,
                          "Tax": tax
                          }

# $/MWh
        return cost_breakdown
