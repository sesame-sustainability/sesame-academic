"""Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
The functional unit is 1 ton of steel"""

"""================================================================================================================"""
#Calculate total Fe needed from upstreams for BF. mainly coming from raw ore and sinter.
def fe_bf_upstream(m_hi_fe):      #m_hi_fe: Fe in hot iron tonne, calculated from m_hi_scrap.py
    n_bf_fe = 0.96485 #input("BF iron conversion efficiency. 1.default:0.96485/2.User:")
    if n_bf_fe== "1":
        n_bf_fe=0.96485 #n_bf: iron ore conversion efficiency in BF, default: 916.8/(786.5+163.7)=0.96485 kg hot iron/kg sinter&raw ore
        fe_hi0_upstream = m_hi_fe / n_bf_fe  # amount of Fe needed from upstream: raw ore and sinter.
    elif n_bf_fe == 0.96485:
        fe_hi0_upstream = m_hi_fe / n_bf_fe  # amount of Fe needed from upstream: raw ore and sinter.
    elif n_bf_fe== "2":
        n_bf_fe=float(input("BF iron conversion efficiency in (0,1):"))
        fe_hi0_upstream = m_hi_fe / n_bf_fe  # amount of Fe needed from upstream: raw ore and sinter.
    else:
        n_bf_fe = float(input("Wrong value.\nPut a BF iron conversion efficiency in (0,1):"))
        fe_hi0_upstream = m_hi_fe / n_bf_fe  # amount of Fe needed from upstream: raw ore and sinter.
    return fe_hi0_upstream

#a=fe_bf_upstream(916.8) #default m_hi_fe
#print(a)
