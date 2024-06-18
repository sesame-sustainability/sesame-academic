"""Get cement production prediction data
source: 1. https://www.usgs.gov/centers/nmic/cement-statistics-and-information
2. https://iea.blob.core.windows.net/assets/cbaa3da1-fd61-4c2a-8719-31538f59b54f/TechnologyRoadmapLowCarbonTransitionintheCementIndustry.pdf"""

import os
import pandas as pd

csv_path = os.path.join(os.path.dirname(__file__), 'cement_prediction.csv')

def cements(country='India'):
    cement = pd.read_csv(csv_path, usecols=['Year']+[f'{country}']) #read and save cement production information
    year = cement['Year'] #get the year value
    cement_p = cement[country] #get the cement production value
    product = {'year':year,'production':cement_p}
    return product

#a = cements()
#print(a)
