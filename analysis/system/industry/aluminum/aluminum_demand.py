"""
Calculate Aluminum furuture demand
"""
import numpy as np

#assume linear increasing
def aluminum_demand(m_aluminum_0, m_aluminum_n, y0, yn):
    # m_aluminum_0: amount of aluminum produced in reference year
    # m_aluminum_n: aluminum demand in future year n
    # y0, yn: year of reference, future, current
    #slop of line
    k = (m_aluminum_n - m_aluminum_0)/(yn - y0)
    ys = np.arange(y0,yn+1,5).tolist()
    m_aluminum = []
    for y in ys:
        m_aluminum_y = k * (y - y0) + m_aluminum_0 
        m_aluminum.append(m_aluminum_y)

    return m_aluminum
