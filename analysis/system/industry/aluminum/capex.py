"""the total capital cost of cement plant is calculated based on data points from source 1. Powerlaw data fit was used. scale factor used for different capacity of plant
source: 1. Garrett, Donald E. Chemical engineering economics. Springer Science & Business Media, 1989. Appendix 1: equipment cost estimates. page 59: https://link.springer.com/content/pdf/bbm%3A978-94-011-6544-0%2F1.pdf 
Total capital cost is calculated in capex.xslx.
2. Investigation of regenerative and recuperative burners for different sizes of reheating furnaces; verified by aspen capital cost estimator v10
"""
import numpy as np
import math


#calculate the capex based on the reference cost, the capacity of the reference and the plant to be calculated, and the CEPCI value
def capexs(capacity=2275000,cepci2=596.2, ppp2=21.99):
    # assume six tenth rule for the capacity expansion. source: Warren D. Seider et al. - Product and Process Design Principles_ Synthesis, Analysis and Evaluation
    #capacity: capacity of the units. tonne/yr
    #sf: shap factor.
    #cepci1,2: chemical engineering plant cost index of the reference year, and year 2020
    #ppp1,2: purchasing power parity of the reference country, and country specified.
    #database
    sf_alumina = 0.54 #shap factors of alumina plant. source 1
    sf_aluminum = 1 # shap factor of aluminum plant. source 1
    capacity1_alumina = 240000 # tonne/year
    capacity1_aluminum = 195000 #tonne/year
    cost1_alumina = 9e7 #$ in year 1987
    cost1_aluminum = 5e8 # $ in year 1987
    ppp1 = 1 #the source base cost is based on 1987 US. 
    cepci1 = 355 # referenced year is 1989. source. https://pdfcoffee.com/cepci-index-1950-2015-pdf-free.html
    t_cost_alumina = cost1_alumina * ((capacity/capacity1_alumina) ** sf_alumina) * \
         (np.array(cepci2) / np.array(cepci1)* np.array(ppp2) /np.array(ppp1))/capacity  #  local current unit (e.g. rupee/tonne alumina).
    t_cost_aluminum = cost1_aluminum * (capacity/np.array(capacity1_aluminum)) ** sf_aluminum * \
         (np.array(cepci2) / np.array(cepci1)* np.array(ppp2) /np.array(ppp1))/capacity  #  local current unit (e.g. rupee/tonne aluminum).
    #print('alumina cost', t_cost_alumina)
    # recuperative burner_remelting_furnace
    ppp2_second = 12.335 # referenced a Thai land plant, source 2. ppp in year 2020
    cepci1_second = 567 # cepci in 2013, source 2.
    cost1_2ndaluminum = 3.88e6 # $ in year 2013
    capacity1_2ndaluminum = 1088400 # tonne/year
    sf_2ndaluminum = 1
    t_cost_2ndaluminum = np.array(cost1_2ndaluminum) * np.array(cepci2) * np.array( ppp2) /(np.array(ppp2_second) * np.array(cepci1_second) * capacity) * (capacity/np.array(capacity1_2ndaluminum)) ** np.array(sf_2ndaluminum) 
          # thailand currency converted to Indian rupee
    print('capex 2nd al', t_cost_2ndaluminum)
    return {
        'capex_alumina':t_cost_alumina,
        'capex_aluminum': t_cost_aluminum,
        'capex_2ndaluminum': t_cost_2ndaluminum,
    }
    



"""capacity = [100,200,600,600,10]
#print(caps[0:2],caps[1])
#print(cepci2,ppp2)
a = capexs(capacity,cepci2,ppp2)
print(a)"""