"""Steel projectory. sources: 1. (internal communication) Sergey Paltsev et al. Economic Analysis of the hard-to-abate sectors in India;
2.  https://www.iea.org/data-and-statistics/charts/production-of-steel-by-route-in-india-in-the-sustainable-development-scenario-2019-2050"""

import os
import pandas as pd

#read total steel production prediction via resource efficiency scenario, and fraction of steel produced from different routes
dirname = os.path.dirname(__file__)
steel_projectory = os.path.join(dirname, 'steel_projectory.csv')
steel_types = pd.read_csv(steel_projectory,usecols=['Year','India_Resource_Efficiency(tonne)','BF_BOF(%)','Innovative_BF_BOF(%)',
                                                       'SR_BOF(%)','Innovative_SR_BOF(%)','DRI_EAF(%)','H_DRI_EAF(%)','Scrap_EAF(%)'])

# Current Scenario set to CCS and Low Carbon Price

def steel_route(steel_type):
    years = steel_types['Year'] #get the year data
    if steel_type=='BF-BOF':
        steel_type = steel_types['BF_BOF(%)']
        m_steel = steel_type * steel_types['India_Resource_Efficiency(tonne)']
    elif steel_type=='Innovative BF-BOF':
        steel_type = steel_types['Innovative_BF_BOF(%)']
        m_steel = steel_type * steel_types['India_Resource_Efficiency(tonne)']
    elif steel_type=='SR_BOF':
        steel_type = steel_types['SR_BOF(%)']
        m_steel = steel_type * steel_types['India_Resource_Efficiency(tonne)']
    elif steel_type=='Innovative_SR_BOF':
        steel_type = steel_types['Innovative_SR_BOF(%)']
        m_steel = steel_type * steel_types['India_Resource_Efficiency(tonne)']
    elif steel_type=='DRI_EAF':
        steel_type = steel_types['DRI_EAF(%)']
        m_steel = steel_type * steel_types['India_Resource_Efficiency(tonne)']
    elif steel_type=='H_DRI_EAF':
        steel_type = steel_types['H_DRI_EAF(%)']
        m_steel = steel_type * steel_types['India_Resource_Efficiency(tonne)']
    else: # steel_type=='Scrap_EAF':
        steel_type = steel_types['Scrap_EAF(%)']
        m_steel = steel_type * steel_types['India_Resource_Efficiency(tonne)']
    return m_steel

#print(steel_route())
