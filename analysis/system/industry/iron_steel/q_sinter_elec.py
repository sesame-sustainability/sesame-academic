"""Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
The functional unit is 1 ton of steel"""

"""================================================================================================================"""
#Calculate electricity needed in sintering.
#amount of electricity is flexible, depends on the amount of energy from other source
def q_sinter_elec(q_sinter0,q_sinter_cog,q_sinter_coke,q_sinter_fwater,q_sinter_steam):
    #q_sinter0: amount of energy requried for sinter plant, calculated in q_sinter.py
    q_sinter_elec0 = q_sinter0 - q_sinter_cog - q_sinter_coke - q_sinter_fwater -q_sinter_steam
    return q_sinter_elec0


#a=q_sinter_elec(2065.3, 67.6, 1811.8, 0.3, 5.2)     #default value
#print(a)

