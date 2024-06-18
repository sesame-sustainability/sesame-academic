"""
Function unit: 1 tonne of steel
DRI-EAF. source: 1. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019). page 39
2.Unal Camdali and Murat Tunc. Modelling of electric energy consumption in the AC electric arc furnace. 2002
"""

import numpy as np

# EAF Energy consumpiton
def eaf_elec(m_steel, m_eaf_coal, m_eaf_ng, hhv_coal):
    cr_q = 2.291 # default energy consumption rate. GJ/tonne steel.
    hhv_ng = 49.5 # GJ/tonne ng. default value.
    q_elecs = cr_q * np.array(m_steel) - m_eaf_coal*hhv_coal - m_eaf_ng*hhv_ng
    return q_elecs

#m_steel = [1.0,5.2,3.7,9]
#a=eaf_elec(m_steel,0.03,0.015556,28.7) # default value
#print(a)