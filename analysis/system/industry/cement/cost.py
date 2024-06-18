"""the total capital cost of cement plant is calculated based on data points from source 1. Powerlaw data fit was used. scale factor used for different capacity of plant
source: 1. Economies of Scale in the Cement Industry: https://www.jstor.org/stable/2097956?seq=20#metadata_info_tab_contents
Total capital cost is calculated in capex.xslx.
"""

#calculate the capex based on the reference cost, the capacity of the reference and the plant to be calculated, and the CEPCI value
def capexs(capacity,cepci2,ppp2):
    # assume six tenth rule for the capacity expansion. source: Warren D. Seider et al. - Product and Process Design Principles_ Synthesis, Analysis and Evaluation
    #capacity: capacity of the units. million tonne/yr
    #sf: shap factor, usualy around 0.727.
    #cepci1,2: chemical engineering plant cost index
    #ppp1,2: purchasing power parity.
    #database
    sf = 0.727 #shap factors
    ppp1 = 0.955 #the source base cost is based on 1971 German. Deutsche Mark. https://data.worldbank.org/indicator/PA.NUS.PRVT.PP?locations=DE
    cepci1 = 132.3 # source. https://pdfcoffee.com/cepci-index-1950-2015-pdf-free.html
    t_cost = 5860.1 * capacity ** sf * cepci2 / cepci1 * ppp2 / ppp1  #  local current unit (e.g. Rupee).total capital cost equation is get from data fitting with powerlow equation: cost = 5860.1*capacity**0.727 Deutsche Mark. capacity is in tonne/yr.
    return t_cost

"""capacity = [100,200,600,600,10]
#print(caps[0:2],caps[1])
#print(cepci2,ppp2)
a = capexs(capacity,cepci2,ppp2)
print(a)"""