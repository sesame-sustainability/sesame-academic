"""Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
The functional unit is 1 ton of steel"""

"""================================================================================================================"""
#Calculate total Fe needed from upstreams for sinter process, mainly from concentrate fine and hearth
def fe_sinter_upstream(m_sinter1):        #m_sinter1: Fe in sinter kg.
    n_sinter_fe= "1" #input("Sinter converison rate (0,1), 1. default: 0.991/2.User:")
    if n_sinter_fe=="1":
        n_sinter_fe=0.991  # default sinter Fe conversion rate
        fe_sint_upstream=m_sinter1/n_sinter_fe #Total Fe needed from sinter process upstream: concentrate fine and hearth
    elif n_sinter_fe=="2":
        n_sinter_fe=float(input("Sinter conversion rate, input value between (0,1]:"))
        fe_sint_upstream = m_sinter1 / n_sinter_fe  # Total Fe needed from sinter process upstream: concentrate fine and hearth
    else:
        n_sinter_fe=float(input("Wrong value.\nPut a BF iron conversion efficiency in (0,1):"))
        fe_sint_upstream = m_sinter1 / n_sinter_fe  # Total Fe needed from sinter process upstream: concentrate fine and hearth
    return fe_sint_upstream  #mount of Fe from concentrate fine and hearth

#a=fe_sinter_upstream(786.5) # use default sinter conversion efficiency
#print(a)