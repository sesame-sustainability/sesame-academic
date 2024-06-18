"""Calculate CO2 emission intensity based on the user input for 2020 and 2050 using a linear approximation"""
import numpy as np

def linproj(ec_y1,ec_y2,y1,y2):
    #slope of line
    slope = (ec_y2-ec_y1)/(y2-y1)
    #assume years 2020 to 2050 with 5 yr increments
    y = np.arange(y1,y2+1,5).tolist()
    i_elec_co2 = [(k-y1)*slope + (ec_y1) for k in y]
    #i_elec_co2 = [n/3600 for n in i] # convert to tCo2/GJ

    return i_elec_co2

# a = linproj(700,150,2020,2050)
# print(a)
