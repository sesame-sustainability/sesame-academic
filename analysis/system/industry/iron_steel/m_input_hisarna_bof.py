"""HIsarna steelmaking route. source: 1. Keys, A., M. Van Hout, and B. Daniels. "Decarbonisation options for the Dutch steel industry." PBL Netherlands Environmental Assessment Agency (2019).
2.He, Huachun, et al. "Assessment on the energy flow and carbon emissions of integrated steelmaking plants." Energy Reports 3 (2017): 29-36."""

# Linear correlation of material & energy input in HIsarna Reactor based pig iron for BOF. source 1.

def m_input_hisarna_bof(m_steel,f_pig_iron, f_scrap, fe_pig_iron, fe_scrap, fe_pellet):
    #m_steel: Amount of crude steel to be produced. kg. default 1000 kg.
    #fe_scrap: Fe content in scrap, default = 0.99. source 2.
    #fe_pellet: Fe content in pellet, default = 0.635. source 2.
    #f_pig_iron: Fraction of Fe from pig iron.   Default f_pig_iron = 0.88*.965053/(0.88*0.965053+0.0000156*0.635+0.17*0.99) =0.88/1.017557=0.834594.
    #f_scrap: fraciton of Fe from scrap. default: f_scrap = 0.17*.99/(0.88*0.965053+0.0000156*0.635+0.17*0.99)=0.17*.99/1.017557=0.165396
    #fe_pig_iron, fe_scrap, fe_pellets: Fe content in them. default:0.965053. source 2.
    n_bof = 0.982746 #n_bof: Fe conversion rate in bof. Default n_bof= 1/ (0.88*0.965053+0.0000156*0.635+0.17*0.99) = 1/1.017557 =0.982746
    m_pig_iron = m_steel / n_bof * f_pig_iron / fe_pig_iron  # kg of pig iron input in bof
    m_scrap = m_steel / n_bof * f_scrap / fe_scrap  # kg of scrap input in bof
    m_pellet = m_steel / n_bof * (1 - f_scrap - f_pig_iron) /fe_pellet  # kg of pellet input in bof

    cr_lime_bof = 0.02411 # Assume linear consumpiton of burnt lime in bof. default: cr_lime_bof = 24.11 kton/Mton = 0.02411 kg lime/kg steel
    m_lime_bof = cr_lime_bof * m_steel # kg of burnt lime

    cr_dolomite_bof = 0.00854 # Assume linear consumpiton of dolomite in bof. default: cr_dolomite_bof = 8.51 kton/Mton = 0.00851 kg lime/kg steel
    m_dolomite_bof = cr_dolomite_bof * m_steel # kg of dolomite

    #energy input from steam is assumed to be recovered/reused via CHP heat production or steam produced in BOF. there is net steam+heat output in bof
    pr_steam_bof = 0.145  # Assume linear net production of steam in bof. default: pr_steam_bof = (0.225-0.08) PJ/ Mton = 0.145 MJ/kg steel. range = [0.11, 0.18] MJ/kg steel
    q_steam_bof = pr_steam_bof * m_steel  # MJ of steam input in bof

    cr_elec_bof = 0.09787 # Assume linear consumtion of electricity in bof. default: cr_elec_bof = 97.87 TJ/1 Mton = 0.09787 MJ/kg steel.
    q_elec_bof = cr_elec_bof * m_steel # MJ of electricity per 1 kg steel

    cr_o2_bof = 53 # Assume linear consumption rate of oxygen in bof. default: 53 Nm3/ kg steel.
    v_o2_bof = cr_o2_bof * m_steel # Nm3 of oxygen

    inputs = {'pig iron':m_pig_iron,'scrap':m_scrap, 'pellet':m_pellet,'limestone':m_lime_bof,'dolomite':m_dolomite_bof,'steam produced':q_steam_bof,'elec':q_elec_bof,'oxygen':v_o2_bof}
    return inputs

#a=m_input_hisarna_bof(1000,0.834594,0.165396,0.965053,0.99,0.635) #default values
#print(a)





