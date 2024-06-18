"""
functional unit: 1 tonne of steel.
Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
The functional unit is 1 ton of steel"""

"""================================================================================================================"""
#Calculate total Fe element required from upstream for BOF process mainly from hot iron and scrap
def fe_bof_upstream(m_steel):               #n_bof represent iron conversion efficiency in BOF;
    n_bof = 0.938 #float(input('Hot iron conversion efficiency:1. default: /n 2. user input (default 0.938)'))
    if ((n_bof=="1") or (n_bof==0.938)):
        n_bof = 0.938       #iron to steel conversion efficiency calculated from given data 1000*0.99/(916.8+138.6) tonne steel/tonne iron.
        t_fe_bof_upstream = m_steel / n_bof  # total upstream Fe needed for 1 tonne steel production. (tonne)
    elif n_bof=="2":
        n_bof = float(input("Please enter a value between 0 to 1:"))
        t_fe_bof_upstream = m_steel / n_bof  # total upstream Fe needed for 1 tonne steel production. (tonne)
    else:
        print("Please input a value in range")
        n_bof = float(input("Please enter a value between 0 to 1:"))
        if n_bof<0 or n_bof>1:
            n_bof = float(input("Please enter a value between 0 to 1:"))
            t_fe_bof_upstream = m_steel / n_bof  # total upstream Fe needed for 1 tonne steel production. (tonne)
        else:
            t_fe_bof_upstream = m_steel / n_bof  # total upstream Fe needed for 1 tonne steel production. (tonne)
    return t_fe_bof_upstream

#t_fe=fe_upstream(500)

#print(f"The upstream Fe needed is {t_fe} tonne")