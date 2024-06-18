import os

import pandas as pd

PATH = os.getcwd() + "/pathway/enduse/"


class Substance:
    def __init__(self, state, substance):
        self.state = state
        self.substance = substance
        self.heat_values = pd.read_csv(PATH + "heat_values.csv")

    def filter_data(self):
        filtered_row = self.heat_values[
            (self.heat_values['State'] == self.state) &
            (self.heat_values['Substance'] == self.substance)].iloc[0]
        return filtered_row

    def convert_units(self, heat_value, density):
        """
        :param heat_value: in Btu/gal for liquid, Btu/ft3 for gas and Btu/tonne for solid
        :param density: in g/gal for liquid, g/ft3 for gas
        :return heat_value: in MJ/kg for all states
        """
        btu_to_mj = 0.001055
        tonne_to_kg = 1000
        g_to_kg = 1.0/1000

        if self.state == "Solid":
            heat_value = (heat_value*btu_to_mj)/tonne_to_kg

        if self.state == "Liquid":
            density_kg_over_gal = density * g_to_kg
            heat_value = (heat_value * btu_to_mj) / density_kg_over_gal

        if self.state == "Gas":
            density_kg_over_ft3 = density * g_to_kg
            heat_value = (heat_value * btu_to_mj) / density_kg_over_ft3

        return heat_value

    def get_lower_heat_value(self):
        """
        :return: low heat_value in MJ/kg
        """
        row = self.filter_data()
        return self.convert_units(row['LHV'], row['Density'])

    def get_higher_heat_value(self):
        """
        :return: high heat_value in MJ/kg
        """
        row = self.filter_data()
        return self.convert_units(row['HHV'], row['Density'])
