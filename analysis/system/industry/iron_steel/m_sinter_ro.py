"""Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
The functional unit is 1 ton of steel"""

"""================================================================================================================"""
#Calculate raw ore and sinter required to produced required hot iron in BF.
def m_sinter_ro(fe_hio_upstream,f_sinter,fe_sinter,fe_ro):
    #m_hi_fe: hot iron Fe production rate kg
    # f_sinter: Fe fraction from sinter kg Fe in sinter/kg Fe in hot iron, default:0.82772;
    #fe_sinter: Fe content in sinter  kg Fe in sinter/kg sinter, default: 0.63;
    #fe_ro: Fe content in raw ore kg Fe in raw ore/kg raw ore, default: 0.64.
    m_sinter = fe_hio_upstream*f_sinter/fe_sinter  # sinter mass needed in kg
    m_ro = fe_hio_upstream*(1-f_sinter)/fe_ro # raw ore needed in kg
    source_bf={"sinter":m_sinter,"raw ore":m_ro} #sinter, raw ore needed in kg
    return source_bf
#a=m_sinter_ro(916.8,0.8277,0.63,0.64) #default values
#print(a)




