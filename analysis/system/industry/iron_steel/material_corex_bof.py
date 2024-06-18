"""
Functional unit: 1 tonne of hot metal.
model COREX
resources: 1. Song, Jiayuan, et al. "Comparison of energy consumption and CO2 emission for three steel production 
routes—Integrated steel plant equipped with blast furnace, oxygen blast furnace or COREX." Metals 9.3 (2019): 364.
Default values used in this model are from the above resources
"""
import numpy as np
#Amount limestone and dolomite needed in reduction shaft. Assume the mount of limestone and dolomite is only related to (linear relation) amount of hot metal produced
def m_corex_bof(m_steel,f_scrap, fe_hm,fe_ore, fe_scrap, fc_coke, c_coal, hhv_coal, f_energy_corex):
    #m_steel: steel produced. 1 tonne
    #f_scrap: fraction of Fe coming from scrap = (106.5+32.6)*0.99/1005.73=0.137
    #fe_hm,fe_ore, fe_scrap: hot metal, ore, scrap/steel iron content = 0.9485,0.6186,0.99 according to calculation from resource 1. 
    #fc_coke: fraction of c coming form coke = 0.0046 source 1.
    #c_coal: carbon content of coal = 0.71 source 1.
    #hhv_coal, hhv_coke: high heating value of coal, coke = 21.1,29.6 GJ/tonne fuel
    #f_energy_corex = 0.4945 allocation of energy used in corex= 1 - fraction of energy used in power plant = 1- 9.2/18.2
    #Assume scrap, steel Fe content = 99%

    # ore, scrap, steel
    fe_consumption =1.00573 # total Fe needed for 1 tonne of steel. =1403.2*0.6186+(106.5+32.6)*0.99
    m_scrap = fe_consumption * np.array(m_steel) * f_scrap/fe_scrap # scrap consumed. tonne scrap
    m_ore = fe_consumption * np.array(m_steel) * (1-f_scrap)/fe_ore # ore consumed. tonne ore
    n_corex = 0.683 # corex conversion factor = 958.5/1403.2 tonne hot metal/tonne ore
    m_hot_metal = m_ore * n_corex # hot metal produced. tonne hot metal.

    #lime
    r_lim_corex = 0.339 #Assume limestone amount has linear relation to amount of hot metal production. r_lim = 294.3/(958.5*0.9055) (tonne/tonne hm)
    m_lim_corex = m_hot_metal * fe_hm * r_lim_corex # tonne lime used in corex

    r_lim_bof = 0.055 #tonne lime/tonne steel
    m_lim_bof = r_lim_bof * np.array(m_steel) # tonne lime used in bof

    #carbon from coal, coke, energy balance by electricity 
    c_reduciton = 0.7418 # total carbon needed for iron reduction. tonne c/tonne steel
    c_coke = 0.8655 # carbon content of coke = 0.8655 source 1.
    m_coke = fc_coke * np.array(m_steel) * c_reduciton /c_coke # coke consumed. tonne coke
    m_coal = (1-fc_coke) * np.array(m_steel) * c_reduciton/c_coal # coal consumed. tonne coal
    hhv_coke = 29.6 # GJ/tonne
    e_coke = m_coke * hhv_coke # GJ of energy from coke
    e_coal = m_coal * hhv_coal # GJ of energy from coal
    r_energy_corex = 18.2 #source 1, figure 9. energy from coal+coke+electricity = 18.2 GJ
    m_coke_corex = f_energy_corex * m_coke # allocated coke used in corex for iron reduction. tonne coke
    m_coal_corex = f_energy_corex * m_coal # allocated coal used in corex for iron reduction. tonne coal.
    delta_energy = r_energy_corex * np.array(m_steel) - np.array(e_coke) - np.array(e_coal) #check if the fuel inject satisfy energy consumption.
    #print(f"delta energy: {delta_energy}")
    elec_corex = []
    for i,d_energy in enumerate(delta_energy):
        if d_energy <= 0:
            elec_corexi = 0
        else:
            elec_corexi = d_energy
        elec_corex.append(elec_corexi)

    # oxygen comsumption
    v_o2_corex = 542.2 * np.array(m_steel) # Nm3 of oxygen used in COREX
    v_o2_bof = 60 * np.array(m_steel) # Nm3 of oxygen used in BOF
    density_oxygen = 1.43 # (99.5*32+28*0.5)/100/22.4 kg/Nm3. source 1.
    m_o2_corex = v_o2_corex * density_oxygen/1000 # tonne of oxygen needed in corex.
    m_o2_bof = v_o2_bof * density_oxygen/1000 # tonne of oxygen needed in bof.

    # electricity consumptions
    elec_corex += 0.345 * np.array(m_steel) # GJ. figure 8 source 1. Note: add the energy balance for fossil fule
    elec_bof = 0.3178 * np.array(m_steel) #GJ. figure 8 source 1.
    elec_lim_corex = 0.0114 * np.array(m_steel) #GJ. figure 8 source 1. =0.0726*55/349.3
    elec_lim_bof = 0.0612 * np.array(m_steel) #GJ. figure 8 source 1. =0.0726*294.3/349.3
    elec_oxygen_corex = 0.00311 * np.array(v_o2_corex) #GJ. figure 8 source 1. = 519.55*0.0036/(542.2+60)
    elec_oxygen_bof = 0.00311 * np.array(v_o2_bof) #GJ. figure 8 source 1. = 519.55*0.0036/(542.2+60)

    return {
        'm_scrap':m_scrap,
        'm_ore': m_ore,
        'm_hot_metal': m_hot_metal,
        'm_lim_corex':m_lim_corex,
        'm_lim_bof': m_lim_bof,
        'm_coke': m_coke,
        'm_coal': m_coal,
        'm_coke_corex':m_coke_corex,
        'm_coal_corex': m_coal_corex,
        'm_o2_corex': m_o2_corex,
        'm_o2_bof': m_o2_bof,
        'elec_corex': elec_corex,
        'elec_bof': elec_bof,
        'elec_lim_corex': elec_lim_corex,
        'elec_lim_bof': elec_lim_bof,
        'elec_oxygen_corex': elec_oxygen_corex,
        'elec_oxygen_bof': elec_oxygen_bof,
    }

#m_steel = [1,3,5,7,6]
#print(f"elec corex {m_corex_bof(m_steel,0.14,0.94,0.62,0.99,0.005,0.71,17)['elec_corex']}")





