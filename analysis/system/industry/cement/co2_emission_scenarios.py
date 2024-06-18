"""Get allowable co2 emisison amount for specific locations based on scenarios
source: https://iea.blob.core.windows.net/assets/cbaa3da1-fd61-4c2a-8719-31538f59b54f/TechnologyRoadmapLowCarbonTransitionintheCementIndustry.pdf"""

import os
import pandas as pd

from analysis.system.industry.cement.cement_trajectory import cements

file_scenarios = os.path.join(os.path.dirname(__file__), 'predicted_co2_emission_scenarios_cement.csv')
scenarios = ['2ds_process','2ds_energy_related','rts_direct','b2ds_direct']
cement_emissions = pd.read_csv(file_scenarios, usecols = ['Year'] + scenarios)

#get the cement production amount
m_cement = cements()['production']  #use default country: India. million metric tons of cement /year (2000,2040,5)
m_cement_globel = cements('World')['production'] #get the global cements production amount. million metric tons of cement /year (2000,2040,5)

def emission_scenario(scenario='2ds_process'): #set default scenario
    allowable_co2_emission = m_cement/m_cement_globel * cement_emissions[scenario] #calculated the amount of co2 emission allowable for specified location. million metric ton/year
    return allowable_co2_emission

# a=emission_scenario()[0:4]
# print(a)
