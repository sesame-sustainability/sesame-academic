

CAPITAL_FRACTION = [0.8, 0.1, 0.1]
DEPRECIATION = [0.2, 0.32, 0.192, 0.1152, 0.1152, 0.0576]


class LCOE:
    """
    Attributes:
       cap_fac - Capacity Factor (No units)
       interest - interest rate (no units)
       Discount - discount rate (no units)
       lifetime- lifetime of power plants in years
       CAPEX- Capital cost in $/kW
       FOM - Fixed O &M in $/kW-yr
       VOM - Variable operating cost in $/MWh
       fuel_cost - Fuel cost in $/MWh

    """

    def __init__(self, cap_fac, cap_reg_mult, OCC, FOM, VOM, finance_values, lifetime, grid_cost, fuel_cost, sale_tax_rate=0):
        self.cap_fac = cap_fac
        self.cap_reg_mult = cap_reg_mult
        self.OCC = OCC
        self.FOM = FOM
        self.VOM = VOM
        self.finance_values = finance_values
        self.lifetime = lifetime
        self.grid_cost = grid_cost
        self.fuel_cost = fuel_cost
        self.sale_tax_rate = sale_tax_rate 

    def get_cost_breakdown(self):
        debt_fraction = self.finance_values['df']
        rate_return_equity = self.finance_values['rre']
        interest_rate = self.finance_values['i']
        inflation_rate = self.finance_values['ir']
        tax_rate = self.finance_values['tr'] 
        WACC = ((1 + ((1 - debt_fraction) * ((1 + rate_return_equity) * (1 + inflation_rate) - 1)) + (
                debt_fraction * ((1 + interest_rate) * (1 + inflation_rate) - 1) * (1 - tax_rate))) / (
                        1 + inflation_rate)) - 1
        CRF = WACC / (1 - (1 / (1 + WACC) ** self.lifetime))
        PVD = 0
        for year, dep_rate in enumerate(DEPRECIATION):
            PVD += (1 / ((1 + WACC) * (1 + interest_rate)) ** year) * dep_rate
        PFF = (1 - tax_rate * PVD) / (1 - tax_rate)
        CFF = 0
        for year, cap_frac in enumerate(CAPITAL_FRACTION):
            CFF += (1 + (1 - tax_rate) * ((1 + inflation_rate) ** (year + 0.5) - 1)) * cap_frac
        CAPEX = CFF * (self.OCC * self.cap_reg_mult + self.grid_cost)
        FCR = CRF * PFF

        capital = FCR * CAPEX * 1000 / (self.cap_fac * 8760)
        fixed = self.FOM * 1000 / (self.cap_fac * 8760)
        tax = self.sale_tax_rate/100*(capital + fixed + self.VOM + self.fuel_cost)
        total = capital + fixed + self.VOM + self.fuel_cost + tax
        cost_breakdown = {"Capital": capital,
                          "Fixed": fixed,
                          "Fuel": self.fuel_cost,
                          "Non-fuel variable": self.VOM,
                          "Tax": tax
                          }

        return cost_breakdown

