"""Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
The functional unit is 1 ton of steel"""

"""================================================================================================================"""
#Calculate concentrate fines and hearth required for sinter process
from fe_sinter_upstream import fe_sinter_upstream as fes

def m_cfine_hearth(m_sinter2,f_cfine,fe_cfine,fe_hearth):
    # m_sinter2: Fe in sinter.  default: 786.5 kg Fe in sinter/kg
    #f_cfine: Fe fraction from concentrate fine. kg Fe from cfine/kg Fe in cfine+hearth, default: 0.9015
    #fe_cfine: Fe content in cfine. kg Fe/kg concentrate fine, default: 0.64
    #fe_hearth: Fe content in hearth. kg Fe/kg hearth, default: 0.64
    t_fe_sinter=fes(m_sinter2)   #total Fe from upstream of sinter plant, i.e. from concentrate fines and hearth,
    m_cfine=t_fe_sinter*f_cfine/fe_cfine    # required concentrate fines kg
    m_hearth=t_fe_sinter*(1-f_cfine)/fe_hearth # required hearth kg
    return {"Concentrate fines":m_cfine,"Hearth":m_hearth}

#a=m_cfine_hearth(786.5,0.9015,0.64,0.64)   #with default value
#print(a)

