"""
function unit: 1 tonne of cement.
Co2 emission assoicated with clinker alternatives for different types of cement.
source 1. García-Segura, Tatiana, Víctor Yepes, and Julián Alcalá. "Life cycle greenhouse gas
emissions of blended cement concrete including carbonation and durability." The International Journal of Life Cycle Assessment 19.1 (2014): 3-12.
2. Shen, Weiguo, et al. "Quantifying CO2 emissions from China’s cement industry." Renewable and Sustainable Energy Reviews 50 (2015): 1004-1012.
"""

def clinker_alternative(m_fly_ash = 25,  m_slag = 50, m_gypsum =5,ash_dis = 250,slag_dis = 130,gyp_dis = 100):
    #ash_dis, slag_dis,gyp_dis: transportation distance (km) for slag, fly ash, and gypsum
    co2_fly_ash = (4 + 0.03*ash_dis)/1000 # assume fly ash emission factor is: 4 kg CO2/tonne fly ash + lorry transportation 0.03 kgCO2/km-tonne * ash_dis km transportation. source 1. (tonne co2/tonne fly_ash)
    co2_slag = (52 + 0.03*slag_dis)/1000 # assume slag emission factor is: 52 kg CO2/tonne slag + lorry transportation 0.03 kgCO2/km-tonne * slag_dis km transportation.  source 1.(tonne co2/tonne slag)
    co2_gypsum = 2.764*6.03*gyp_dis/1000 # assume gypsum emission factor is 2.764*6.03 kg CO2/km-tonne transportation. only transportation considered. source 2.(tonne co2/tonne gypsum)
    m_fly_ash_co2 = m_fly_ash * co2_fly_ash  #  CO2 emission due to fly ash use (tonne CO2)
    m_slag_co2 = m_slag * co2_slag #  CO2 emission due to slag use (tonne CO2)
    m_gypsum_co2 = m_gypsum * co2_gypsum  #  CO2 emission due to gypsum use (tonne CO2)

    co2_alternative = {'fly ash':m_fly_ash_co2,'slag': m_slag_co2,'gypsum':m_gypsum_co2}
    return co2_alternative