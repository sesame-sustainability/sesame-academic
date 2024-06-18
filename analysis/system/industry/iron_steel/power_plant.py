"""Power Plant for Onsite Electricity Generation
Assuming waste gas use
BF Case Based on He et al: https://reader.elsevier.com/reader/sd/pii/S2352484717300033?token=559979ADCA510CD5D1EE0A658C5AF5696D89DD92F94C1F4468DBBDF499E1A59C7486C497734D9C2A158BD6304AA5478B&originRegion=us-east-1&originCreation=20220208175727
India Power Plant Info: https://cdm.unfccc.int/filestorage/Z/6/H/Z6HFW5FPPRA2BKAUK3CK5XN6EXB98F.1/Kalyani_PDD_28April2006.pdf?t=SWN8cjZ6cmNkfDBVoFiUaj0TOtJw92SytzFm
2009 Verification of Power Plant: https://cdm.unfccc.int/filestorage/3/Q/G/3QGWS91HDFN0YJABIU8ZPV24L6XMTK/Monitoring%20Report%204.pdf?t=OTR8cjcwdHRifDDcct5lxJ1LTnlu1wAUKqoC"""
from analysis.system.industry.iron_steel.exchange_rate import exchange_country as er
import numpy as np
from core.pathway import Pathway
import analysis.lca as lca_analysis
from core.inputs import InputSet
from core.tea import TeaPathway
from tea.topology import tea_registry


def captive_power(fuel,wg,cp_eff,country):
    kwh_to_GJ = 277.78
    Mwh_to_GJ = 3.6
    if fuel == 'Waste Gas':
        [m_COG,m_BFG,m_BOFG] = wg
        #Emission / Energy
        COG_ed = 2458.6/70.8 #source 1  MJ/kg
        BFG_ed = 5238/720.4 #source 1 MJ/kg
        BOFG_ed = 782.3/52.5 #source 1  MJ/kg
        # eff = 0.32 #source 2
        COG_en = m_COG*COG_ed
        BFG_en = m_BFG*BFG_ed
        BOFG_en = m_BOFG*BOFG_ed
        total_en  = COG_en + BFG_en + BOFG_en
        # print(total_en)
        cp_elec = total_en*cp_eff/1000/100#MJ to GJ
        #furnace oil emissions (source 2)
        fo_cons = 0.014337611  #fo consumptio`n kg per kWh generated at plant
        fo_in  = 3.1256  #kg CO2/kg of fo (co2 intensity)
        cp_em = fo_cons*cp_elec*0.0036*fo_in/1000 # convert to t CO2
        cp_em_in = fo_cons*0.0036*fo_in/1000
        # print(cp_elec)
        cp_elec -= cp_elec*0.07 # auxiliary equipment accounts for 7% ( source 2)
        # print(cp_elec)
        #Economics ( #source 2)

        rupee_inflation = 2.79 # 2006 to 2021 Rupee https://www.worlddata.info/asia/india/inflation-rates.php
        cp_sm = 0.4*kwh_to_GJ*rupee_inflation/np.array(er(country))[0] #salary/admin cost (2006 Rupees/Kwh to 2021 USD/GJ),
        # print(rupee_inflation/np.array(er(country))[0])
        # print(np.array(er(country))[0])
        cp_om = 1*kwh_to_GJ*rupee_inflation/np.array(er(country))[0] #maintenance cost,2006 Rupees/Kwh to 2021 USD/GJ),
                # fo_kg_L =  1/0.93 #source 2 (1/density)
        cp_oil_c = fo_cons*kwh_to_GJ*33*np.ones(5)/np.array(er(country))[0] # https://dir.indiamart.com/impcat/furnace-oil.html (2021 rupees)
        # print(fo_cons*kwh_to_GJ*33)
        mat_cost = cp_oil_c
        capex = 0 # see capex file for the information

    else: #pathway code from grid.py
        if fuel == 'Coal':

            pathway = Pathway.build([
                'enduse-electricity-default',
                'gatetoenduse-transmission-literaturereview',
                ('process-coalpowerproduction-greet',{
                    'region':'HICC',
                    'plant_type':'Boiler (~99% of US coal turbines)'
                }),
                'midstream-coaltransportation-greet',
                ('upstream-coal-greet',{
                    'well_infrastructure':'No',
                    'coal_type': 'Bituminous',
                }),
            ])
            data = lca_analysis.run([pathway])
            # print(data)
            data['data'] = data['data'].groupby(['pathway', 'stage']).agg({'value': 'sum'}).reset_index()
            # print(data['data'])
            #incorporate the user input for efficiency by dividing by default efficiency
            process_eci = data['data']['value'][2]
            data_eff = 0.225  # typical for HICC region,boiler
            new_process_eci = process_eci * (data_eff / (cp_eff / 100))
            data_eci = data['data'].sum()[1]
            new_eci = data_eci - process_eci + new_process_eci
            cp_em = new_eci * kwh_to_GJ * 10 ** -6

            # print(cp_em)
            ##ECON (from SESAME frontend output)
            tea_analysis = tea_registry.lookup_by_name('Coal')
            input_set = InputSet.build_default(tea_analysis)
            tea_pathway = TeaPathway(tea_analysis, input_set)
            # input_set.set_value('coal_type','Bituminous')
            # input_set.set_value('well_infrastructure', 'No')
            g = tea_pathway.perform()
            econ = g['cost_breakdown']
            capex = econ['Capital']/Mwh_to_GJ
            mat_cost = econ['Fuel']/Mwh_to_GJ
            cp_om = (econ['Fixed'] + econ['Non-fuel variable'])/Mwh_to_GJ
            cp_sm = 0
            cp_elec = 0
            # capex = 59/Mwh_to_GJ #$/MWh
            # mat_cost = 21/Mwh_to_GJ
            # cp_om = 67/Mwh_to_GJ
            # cp_sm = 0

        elif fuel == 'Solar': # use SESAME LCA to calculate emissions as per kWh, currently set to India
            pathway = Pathway.build([
                'enduse-electricity-default',
                'gatetoenduse-transmission-literaturereview',
                ('process-solarpowerproduction-default', {
                'location': 'India (Mumbai)',
                    'efficiency':cp_eff
                }),
                'upstream-solar-default',
            ])
            data = lca_analysis.run([pathway])
            data['data'] = data['data'].groupby(['pathway', 'stage']).agg({'value': 'sum'}).reset_index()
            # print(data['data'])
            eci = data['data'].sum()[1]
            cp_em = eci*kwh_to_GJ*10**-6


            ##Econ

            tea_analysis = tea_registry.lookup_by_name('Solar')
            input_set = InputSet.build_default(tea_analysis)
            input_set.set_value('location','India (Mumbai)')
            tea_pathway = TeaPathway(tea_analysis, input_set)
            g = tea_pathway.perform()
            econ = g['cost_breakdown']
            capex = econ['Capital'] / Mwh_to_GJ
            mat_cost = econ['Fuel'] / Mwh_to_GJ
            cp_om = (econ['Fixed'] + econ['Non-fuel variable']) / Mwh_to_GJ
            cp_sm = 0
            cp_elec = 0
            # capex = 32 / Mwh_to_GJ  # $/MWh
            # mat_cost = 0 / Mwh_to_GJ
            # cp_om = 62 / Mwh_to_GJ

            # tea_pathway = TeaPathway.load(TeaAnalysis,[
            #     'enduse-electricity-default',
            #     'gatetoenduse-transmission-literaturereview',
            #     ('process-solarpowerproduction-default', {
            #         'location': 'India (Mumbai)',
            #     }),
            #     'upstream-solar-default',])
            # data = tea_pathway.run([pathway])
            # data['data'] = data['data'].groupby(['pathway', 'stage']).agg({'value': 'sum'}).reset_index()

        elif fuel == 'Natural Gas':  # use SESAME LCA to calculate emissions as per kWh, currently set to India
            pathway = Pathway.build([
                'enduse-electricity-default',
                'gatetoenduse-transmission-literaturereview',
                ('process-ngpowerproduction-greet',{
                    'generator_type':'Combined Cycle'
                }),
                'midstream-ngelectricitytransportation-greet',
                'upstream-naturalgas-greet',
            ])
            data = lca_analysis.run([pathway])
            data['data'] = data['data'].groupby(['pathway', 'stage']).agg({'value': 'sum'}).reset_index()

            #adjust process emissions based on efficiency
            process_eci = data['data']['value'][2]
            data_eff = 0.506  # typical for HICC region
            new_process_eci = process_eci*(data_eff / (cp_eff / 100))
            data_eci = data['data'].sum()[1]
            new_eci = data_eci - process_eci + new_process_eci
            # print(new_eci)
            cp_em = new_eci * kwh_to_GJ * 10 ** -6
            cp_elec = 0
            capex = 0
            mat_cost = 0
            cp_om = 0
            cp_sm = 0

        elif fuel == 'Wind':  # use SESAME LCA to calculate emissions as per kWh, currently set to India
            pathway = Pathway.build([
                'enduse-electricity-default',
                'gatetoenduse-transmission-literaturereview',
                'process-windpowerproduction-default',
                'upstream-wind-default',
            ])
            data = lca_analysis.run([pathway])
            data['data'] = data['data'].groupby(['pathway', 'stage']).agg({'value': 'sum'}).reset_index()
            # print(data['data'])
            eci = data['data'].sum()[1]
            cp_em = eci * kwh_to_GJ * 10 ** -6
            cp_elec = 0
            capex = 0
            mat_cost = 0
            cp_om = 0
            cp_sm = 0


    cp_data = {'cp_em': cp_em,'cp_elec': cp_elec, 'cp_capex':capex ,'maintenance': cp_om, 'sal/admin':cp_sm, 'mat_cost': mat_cost}
    # print(cp_data)
    return cp_data

# a = captive_power('Solar',[],20,'India')
# # # # a = captive_power(0,521.96,105)
# print(a)
# #
