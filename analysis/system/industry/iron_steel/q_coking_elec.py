"""Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
The functional unit is 1 ton of steel"""

"""================================================================================================================"""
#Calculate energy needed in coke plant. suppose the total energy need in coming from BFG and electricity
#amount of electricity is flexible, depends on the amount of energy from other source
def q_coking_elec(q_coking0,q_bfg): #q_coking0: total energy required for coking plant (not count coke energy);
    #q_bfg: energy from BFG
    q_coking_elec0= q_coking0 - q_bfg
    return q_coking_elec0

#a=q_coking_elec(1410.7, 1368.2)     #default value
#print(a)

