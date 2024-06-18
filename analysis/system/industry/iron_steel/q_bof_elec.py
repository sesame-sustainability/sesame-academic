"""Typical BF-BOF route. Data based on a Chinese plant.
Source: He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants."
Energy Reports 3 (2017): 29-36.
The functional unit is 1 ton of steel"""

"""================================================================================================================"""
#Calculate electricity needed in BOF based on total energy required in BOF.
#amount of electricity is flexible, depends on the amount of energy from other source
# Assuming the total energy needed is linearly related to the sum of all Fe element from hot iron and scrap:
#e.g.: (916.8+138.6)tonne *x=(9195.7+20.7+598.7+270.9+21.7+127.8)GJ. Energy flux X= 9.698 GJ/tonne Fe
def q_bof_elec(t_fe_bof_upstream,q_hot_iron,q_air,q_bof_cog, q_steam): #t_fe_bof_upstream calculated from fe_bof_upstream
    cr_q_bof = 9.69822 #energy consumption rate (916.8+138.6)tonne *x=(9195.7+20.7+598.7+270.9+21.7+127.8)GJ. Energy flux X= 9.698 GJ/tonne Fe
    elec = t_fe_bof_upstream*cr_q_bof - q_hot_iron - q_air - q_bof_cog - q_steam
    #amount of electricity (GJ) equals the difference of energy demand minus input from other sources
    return elec

#a=q_bof_elec(1055.4,9195.7,890.3,21.7) #default values
#print(a)

