from core.pathway import Metadata
from core.utils import load_class

metadata = Metadata()

# enduse
enduse = metadata.register_stage('Enduse')


# electricity category enduse
electricity = enduse.register_activity('Electricity', category='Electricity')
electricity.register_source(
    'Default',
    load_class('pathway.enduse.electricity.electricity', 'Electricity')
)


# Chemical category enduse
dme = enduse.register_activity('DME - Dimethyl Ether', category='Chemical')
dme.register_source(
    'Default',
    load_class('pathway.enduse.chemical.dme', 'DME')
)
hydrogen = enduse.register_activity('Hydrogen', category='Chemical')
hydrogen.register_source(
    'Default',
    load_class('pathway.enduse.chemical.hydrogen', 'Hydrogen')
)
methanol = enduse.register_activity('Methanol', category='Chemical')
methanol.register_source(
    'Default',
    load_class('pathway.enduse.chemical.methanol', 'Methanol')
)
lng = enduse.register_activity('LNG - Liquid Natural Gas', category='Chemical')
lng.register_source(
    'Default',
    load_class('pathway.enduse.chemical.lng', 'LNG')
)


# Fuel category enduse

gasoline = enduse.register_activity('Gasoline', category='Fuel')
gasoline.register_source(
    'Default',
    load_class('pathway.enduse.fuel.gasoline', 'Gasoline'),
    table='pathway/enduse/fuel/gasoline_lcidata.csv'
)
diesel = enduse.register_activity('Diesel', category='Fuel')
diesel.register_source(
    'Default',
    load_class('pathway.enduse.fuel.diesel', 'Diesel'),
    table='pathway/enduse/fuel/diesel_lcidata.csv'
)
lpg = enduse.register_activity('LPG - Liquid Petroleum Gas', category='Fuel')
lpg.register_source(
    'Default',
    load_class('pathway.enduse.fuel.lpg', 'LPG'),
    table='pathway/enduse/fuel/lpg_lcidata.csv'
)

cng = enduse.register_activity('CNG - Compressed Natural Gas', category='Fuel')
cng.register_source(
    'Default',
    load_class('pathway.enduse.fuel.cng', 'CNG'),
    table='pathway/enduse/fuel/cng_lcidata.csv'
)

steam = enduse.register_activity('Steam', category='Fuel')
steam.register_source(
    'Default',
    load_class('pathway.enduse.fuel.steam', 'Steam')
)

corn_ethanol_nobiogen = enduse.register_activity('Corn ethanol', category='Fuel')
corn_ethanol_nobiogen.register_source(
    'Default',
    load_class('pathway.enduse.fuel.corn_ethanol_nobiogen', 'Corn_ethanol_nobiogen'),
    table = 'pathway/enduse/fuel/ethanol_nobiogen_lcidata.csv'
)

corn_stover_ethanol = enduse.register_activity('Corn stover ethanol', category='Fuel')
corn_stover_ethanol.register_source(
    'Default',
    load_class('pathway.enduse.fuel.corn_stover_ethanol', 'Corn_stover_ethanol'),
    table = 'pathway/enduse/fuel/ethanol_withbiogen_lcidata.csv'
)

#  Materials category enduse
concrete = enduse.register_activity('Concrete', category='Material')
concrete.register_source(
    'GREET',
    load_class('pathway.enduse.materials.concrete_eu', 'Concrete')
)

iron = enduse.register_activity('Iron', category='Material')
iron.register_source(
    'GREET',
    load_class('pathway.enduse.materials.iron', 'Iron')
)

steel = enduse.register_activity('Steel', category='Material')
steel.register_source(
    'GREET',
    load_class('pathway.enduse.materials.steel', 'Steel')
)

cement = enduse.register_activity('Cement', category='Material')
cement.register_source(
    'GREET',
    load_class('pathway.enduse.materials.cement', 'Cement')
)

libat = enduse.register_activity('Li-ion battery', category='Other Technology')
libat.register_source(
    'GREET',
    load_class('pathway.enduse.other.libattery', 'LiBattery')
)

jetfuel = enduse.register_activity('Jet Fuel', category='Fuel')
jetfuel.register_source(
    'GREET',
    load_class('pathway.enduse.fuel.jetfuel', 'Jetfuel'),
    table='pathway/enduse/fuel/convjetfuelenduse.csv'
)

dac = enduse.register_activity('Direct air capture', category='Other Technology')
dac.register_source(
    'Default',
    load_class('pathway.enduse.other.dac', 'DAC_EU')
)

# # Light-Duty Vehicle enduse
# gas_ldv = enduse.register_activity('Gasoline Light-Duty Vehicle', category='Light-Duty Vehicle')
# gas_ldv.register_source(
#     'Default',
#     load_class('pathway.enduse.light_duty_vehicle.gas_ldv', 'Gasoline_LDV')
# )

# GateToEnduse
gate_to_enduse = metadata.register_stage('GateToEnduse')

transmission = gate_to_enduse.register_activity('Transmission')
transmission.register_source(
    'Literature review',
    load_class('pathway.gate_to_enduse.transmission', 'Transmission')
)

transportation_methanol = gate_to_enduse.register_activity('MethanolTransportation')
transportation_methanol.register_source(
    'GREET',
    load_class('pathway.gate_to_enduse.transportation', 'MethanolTransportation'),
    table='pathway/gate_to_enduse/transportation_lcidata.csv'
)

transportation_gasoline = gate_to_enduse.register_activity('GasolineTransportation')
transportation_gasoline.register_source(
    'GREET',
    load_class('pathway.gate_to_enduse.transportation', 'GasolineTransportation'),
    table='pathway/gate_to_enduse/transportation_lcidata.csv'
)

transportation_diesel = gate_to_enduse.register_activity('DieselTransportation')
transportation_diesel.register_source(
    'GREET',
    load_class('pathway.gate_to_enduse.transportation', 'DieselTransportation'),
    table='pathway/gate_to_enduse/transportation_lcidata.csv'
)

transportation_dme = gate_to_enduse.register_activity('DMETransportation')
transportation_dme.register_source(
    'GREET',
    load_class('pathway.gate_to_enduse.transportation', 'DMETransportation'),
    table='pathway/gate_to_enduse/transportation_lcidata.csv'
)

transportation_lng = gate_to_enduse.register_activity('LNGTransportation')
transportation_lng.register_source(
    'GREET',
    load_class('pathway.gate_to_enduse.transportation', 'LNGTransportation'),
    table='pathway/gate_to_enduse/transportation_lcidata.csv'
)

transportation_lpg = gate_to_enduse.register_activity('LPGTransportation')
transportation_lpg.register_source(
    'GREET',
    load_class('pathway.gate_to_enduse.transportation', 'LPGTransportation'),
    table='pathway/gate_to_enduse/transportation_lcidata.csv'
)

transportation_hydrogen = gate_to_enduse.register_activity('HydrogenGasTransportation')
transportation_hydrogen.register_source(
    'GREET',
    load_class('pathway.gate_to_enduse.transportation', 'HydrogenGasTransportation'),
    table='pathway/gate_to_enduse/transportation_lcidata.csv'
)

transportation_concrete = gate_to_enduse.register_activity('ConcreteTransportation')
transportation_concrete.register_source(
    'Default',
    load_class('pathway.gate_to_enduse.transportation', 'ConcreteTransportation'),
    table='pathway/gate_to_enduse/transportation_lcidata.csv'
)

transportation_iron = gate_to_enduse.register_activity('IronTransportation')
transportation_iron.register_source(
    'Default',
    load_class('pathway.gate_to_enduse.transportation', 'IronTransportation'),
    table='pathway/gate_to_enduse/transportation_lcidata.csv'
)

transportation_steel = gate_to_enduse.register_activity('SteelTransportation')
transportation_steel.register_source(
    'Default',
    load_class('pathway.gate_to_enduse.transportation', 'SteelTransportation'),
    table='pathway/gate_to_enduse/transportation_lcidata.csv'
)

transportation_cement = gate_to_enduse.register_activity('CementTransportation')
transportation_cement.register_source(
    'Default',
    load_class('pathway.gate_to_enduse.transportation', 'CementTransportation'),
    table='pathway/gate_to_enduse/transportation_lcidata.csv'
)

transportation_jetfuel = gate_to_enduse.register_activity('JetFuelTransportation')
transportation_jetfuel.register_source(
    'GREET',
    load_class('pathway.gate_to_enduse.transportation', 'JetFuelTransportation'),
    table='pathway/gate_to_enduse/transportation_lcidata.csv'
)

# Process
process = metadata.register_stage('Process')

coal_steam_production = process.register_activity('Coal steam production')
coal_steam_production.register_source(
    'GREET',
    load_class('pathway.process.coal.coal_steam_production', 'SteamProductionCoal'),
    table='pathway/process/coal/coal_steam_lcidata.csv'
)

ng_steam_production = process.register_activity('Natural gas steam production')
ng_steam_production.register_source(
    'GREET',
    load_class('pathway.process.natural_gas.ng_steam_production', 'SteamProductionNG'),
    table='pathway/process/natural_gas/ng_steam_lcidata.csv'
)

solar_power_production = process.register_activity('SolarPowerProduction')
solar_power_production.register_source(
    'Default',
    load_class('pathway.process.solar.solar_power_production', 'SolarPowerProduction'),
    table='pathway/process/solar/solar_cat_inputs.csv'
)

wind_power_production = process.register_activity('WindPowerProduction')
wind_power_production.register_source(
    'Default',
    load_class('pathway.process.wind.wind_power_production', 'WindPowerProduction'),
    table='pathway/process/wind/wind_cat_inputs.csv'
)

ng_power_production = process.register_activity('NGPowerProduction')
ng_power_production.register_source(
    'GREET',
    load_class('pathway.process.natural_gas.ng_power_greet', 'NGPowerGREET'),
    table='pathway/process/natural_gas/ng_power_greet_lcidata.csv'
)
ng_power_production.register_source(
    'ASPEN',
    load_class('pathway.process.natural_gas.ng_power_aspen', 'NGPowerASPEN'),
    table='pathway/process/natural_gas/ng_power_aspen_lcidata.csv'
)

coal_power_production = process.register_activity('CoalPowerProduction')
coal_power_production.register_source(
    'GREET',
    load_class('pathway.process.coal.coal_power_greet', 'CoalPowerGREET'),
    table='pathway/process/coal/coal_power_greet_lcidata.csv'
)
coal_power_production.register_source(
    'ASPEN',
    load_class('pathway.process.coal.coal_power_aspen', 'CoalPowerASPEN'),
    table='pathway/process/coal/coal_power_aspen_lcidata.csv'
)

methanol_production = process.register_activity('MethanolProduction')
methanol_production.register_source(
    'GREET',
    load_class('pathway.process.methanol.methanol_production', 'MethanolProduction'),
    table='pathway/process/methanol/methanol_production.csv'
)

gasoline_refining = process.register_activity('GasolineProduction')
gasoline_refining.register_source(
    'GREET',
    load_class('pathway.process.gasoline_production', 'GasolineProduction'),
    table='pathway/process/gasoline_greet_lcidata.csv'
)

diesel_production = process.register_activity('DieselProduction')
diesel_production.register_source(
    'GREET',
    load_class('pathway.process.diesel_production', 'DieselProduction'),
    table='pathway/process/diesel_greet_lcidata.csv'
)

lng_production = process.register_activity('LNGProduction')
lng_production.register_source(
    'GREET',
    load_class('pathway.process.lng.lng_production', 'LNGProduction'),
    table='pathway/process/lng/lng_production.csv'
)

cng_production = process.register_activity('CNGProduction')
cng_production.register_source(
    'GREET',
    load_class('pathway.process.cng.cng_production', 'CNGProduction'),
    table='pathway/process/cng/cng_production.csv'
)

lpg_production = process.register_activity('LPGProduction')
lpg_production.register_source(
    'GREET',
    load_class('pathway.process.lpg_production', 'LPGProduction'),
    table='pathway/process/lpg_greet_lcidata.csv'
)

dme_production = process.register_activity('DMEProduction')
dme_production.register_source(
    'GREET',
    load_class('pathway.process.dme.dme_production', 'DMEProduction'),
    table='pathway/process/dme/dme_production.csv'
)

hydrogen_production_SMR = process.register_activity('Production using SMR')
hydrogen_production_SMR.register_source(
    'GREET',
    load_class('pathway.process.hydrogen.hydrogen_production2', 'HydrogenProductionSMR'),
    table='pathway/process/hydrogen/hydrogen_production.csv'
)

hydrogen_production_gasification = process.register_activity('Production using Coal')
hydrogen_production_gasification.register_source(
    'GREET',
    load_class('pathway.process.hydrogen.hydrogen_production2', 'HydrogenProductionCoal'),
    table='pathway/process/hydrogen/hydrogen_production.csv'
)

hydrogen_production_electrolysis = process.register_activity('Production using Electrolysis')
hydrogen_production_electrolysis.register_source(
    'GREET',
    load_class('pathway.process.hydrogen.hydrogen_production2', 'HydrogenProductionElec'),
    table='pathway/process/hydrogen/hydrogen_production.csv'
)

hydro_power_production = process.register_activity('Hydro power production')
hydro_power_production.register_source(
    'GREET',
    load_class('pathway.process.hydro_power_greet', 'HydroPowerGREET'),
    table='pathway/process/hydro_power_greet_lcidata.csv'
)

hydro_power_production = process.register_activity('Hydro power production')
hydro_power_production.register_source(
    'GREET',
    load_class('pathway.process.hydro_power_greet', 'HydroPowerGREET'),
    table='pathway/process/hydro_power_greet_lcidata.csv'
)

lwr_nuclear_power_production = process.register_activity('LWR Nuclear power production')
lwr_nuclear_power_production.register_source(
    'GREET',
    load_class('pathway.process.nuclear_power_greet', 'LWRNuclearPowerGREET'),
    table='pathway/process/nuclear_power_greet_lcidata.csv'
)

htgr_nuclear_power_production = process.register_activity('HTGR Nuclear power production')
htgr_nuclear_power_production.register_source(
    'GREET',
    load_class('pathway.process.nuclear_power_greet', 'HTGRNuclearPowerGREET'),
    table='pathway/process/nuclear_power_greet_lcidata.csv'
)

corn_ethanol_production_nobiogen = process.register_activity('Corn ethanol production')
corn_ethanol_production_nobiogen.register_source(
    'Mixed sources',
    load_class('pathway.process.biofuel.corn_ethanol_production_nobiogen', 'CornEthanolProduction'),
    table='pathway/process/biofuel/corn_ethanol_nobiogen_lcidata.csv'
)

stover_ethanol_production_withbiogen = process.register_activity('Corn stover ethanol production')
stover_ethanol_production_withbiogen.register_source(
    'Mixed sources',
    load_class('pathway.process.biofuel.stover_ethanol_production_withbiogen', 'StoverEthanolProduction'),
    table='pathway/process/biofuel/stover_ethanol_withbiogen_lcidata.csv'
)

concrete_production = process.register_activity('Concrete production')
concrete_production.register_source(
    'GREET',
    load_class('pathway.process.concrete.concrete_production', 'ConcreteProduction'),
    table='pathway/process/concrete/concrete_process_lcidata.csv'
)

iron_production = process.register_activity('Iron production')
iron_production.register_source(
    'GREET',
    load_class('pathway.process.iron.iron_process', 'IronProduction'),
    table='pathway/process/iron/iron_lcidata.csv'
)

steel_production = process.register_activity('Steel production')
steel_production.register_source(
    'GREET',
    load_class('pathway.process.steel.steel_process', 'SteelProduction'),
    table='pathway/process/steel/steel_lcidata.csv'
)

cement_production = process.register_activity('Cement production')
cement_production.register_source(
    'GREET',
    load_class('pathway.process.cement.cement_process', 'CementProduction'),
    table='pathway/process/cement/cement_lcidata.csv'
)

libattery_production = process.register_activity('Li-ion battery production')
libattery_production.register_source(
    'GREET',
    load_class('pathway.process.li_battery.LiBattery', 'LiBatteryProduction'),
    table='pathway/process/li_battery/li_bat_lcidata.csv'
)

jetfuel_production = process.register_activity('JetFuelProduction')
jetfuel_production.register_source(
    'GREET',
    load_class('pathway.process.jet_fuel.jetfuel_production', 'JetFuelProduction'),
    table='pathway/process/jet_fuel/jetfuelproductionlcidata.csv'
)

dac_process = process.register_activity('Direct Air Capture Process')
dac_process.register_source(
    'Default',
    load_class('pathway.process.ccs.dac.dac', 'CcsDacLca'),
    table='pathway/process/ccs/dac/plant_ref_data_dac.csv'
)

compressed_air_energy_storage = process.register_activity('CAES')
compressed_air_energy_storage.register_source(
    '',
    load_class('pathway.process.caes.CAES', 'CAES'),
    table='pathway/process/caes/CAES_Data.csv'
)

# Midstream
midstream = metadata.register_stage('Midstream')

transportation_uranium = midstream.register_activity('Uranium transportation')
transportation_uranium.register_source(
    'GREET',
    load_class('pathway.midstream.transportation', 'UraniumTransportation'),
    table='pathway/midstream/transportation_lcidata.csv'
)

transportation_corn = midstream.register_activity('Corn transportation')
transportation_corn.register_source(
    'GREET',
    load_class('pathway.midstream.transportation', 'CornTransportation'),
    table='pathway/midstream/transportation_lcidata.csv'
)

transportation_stover = midstream.register_activity('Corn stover transportation')
transportation_stover.register_source(
    'GREET',
    load_class('pathway.midstream.transportation', 'StoverTransportation'),
    table='pathway/midstream/transportation_lcidata.csv'
)

transportation_ethanol_nobiogen = gate_to_enduse.register_activity('Ethanol transportation')
transportation_ethanol_nobiogen.register_source(
    'GREET',
    load_class('pathway.gate_to_enduse.transportation', 'EthanolTransportationNoBiogen'),
    table='pathway/gate_to_enduse/transportation_lcidata.csv'
)
#Dummy modes for ethanol to ensure modules for "with biogenic carbon" and "without biogenic carbon" are not mixed up to generate
#inconsistent results unexpectedly
transportation_ethanol_withbiogen = gate_to_enduse.register_activity('Ethanol transportation')
transportation_ethanol_withbiogen.register_source(
    'GREET',
    load_class('pathway.gate_to_enduse.transportation', 'EthanolTransportationWithBiogen'),
    table='pathway/gate_to_enduse/transportation_lcidata.csv'
)
transportation_ng_electricity = midstream.register_activity('NGElectricityTransportation')
transportation_ng_electricity.register_source(
    'GREET',
    load_class('pathway.midstream.transportation', 'NGElectricityTransportation'),
    table='pathway/midstream/transportation_lcidata.csv'
)

transportation_ng_non_electricity = midstream.register_activity('NGNonElectricityTransportation')
transportation_ng_non_electricity.register_source(
    'GREET',
    load_class('pathway.midstream.transportation', 'NGNonElectricityTransportation'),
    table='pathway/midstream/transportation_lcidata.csv'
)

transportation_coal = midstream.register_activity('CoalTransportation')
transportation_coal.register_source(
    'GREET',
    load_class('pathway.midstream.transportation', 'CoalTransportation'),
    table='pathway/midstream/transportation_lcidata.csv'
)

transportation_crude = midstream.register_activity('CrudeTransportation')
transportation_crude.register_source(
    'GREET',
    load_class('pathway.midstream.transportation', 'CrudeTransportation'),
    table='pathway/midstream/transportation_lcidata.csv'
)

transportation_concrete_mid = midstream.register_activity('ConcreteTransportation')
transportation_concrete_mid.register_source(
    'GREET',
    load_class('pathway.midstream.transportation', 'ConcreteTransportation'),
    table='pathway/midstream/transportation_lcidata.csv'
)
# TEA
tea = metadata.register_stage('TEA')

wind_tea = tea.register_activity('WindTEA')
wind_tea.register_source(
    'Default',
    load_class('pathway.tea.wind', 'Wind'),
    table='tea/electricity/wind/region_speed_new.csv',
)

# Upstream
upstream = metadata.register_stage('Upstream')

solar_power_plant = upstream.register_activity('Solar')
solar_power_plant.register_source(
    'Default',
    load_class('pathway.upstream.solar', 'Solar'),
)

wind_power_plant = upstream.register_activity('Wind')
wind_power_plant.register_source(
    'Default',
    load_class('pathway.upstream.wind', 'Wind'),
)

hydro_power_plant = upstream.register_activity('Hydropower')
hydro_power_plant.register_source(
    'Default',
    load_class('pathway.upstream.hydro', 'Hydro'),
)

dummy = upstream.register_activity('Electricity')
dummy.register_source(
    'Default',
    load_class('pathway.upstream.dummy', 'Dummy'),
)

natural_gas = upstream.register_activity('Natural Gas')
natural_gas.register_source(
    'GREET',
    load_class('pathway.upstream.natural_gas', 'NaturalGas'),
    table='pathway/upstream/natural_gas_greet.csv'
)

coal = upstream.register_activity('Coal')
coal.register_source(
    'GREET',
    load_class('pathway.upstream.coal_greet', 'CoalGreet'),
    table='pathway/upstream/coal_greet.csv'
)

crude_oil = upstream.register_activity('Crude Oil')
crude_oil.register_source(
    'GREET',
    load_class('pathway.upstream.crude', 'Crude'),
    table='pathway/upstream/crude_lcidata.csv'
)

corn_no_biogen = upstream.register_activity('Corn (no biogenic carbon accounting)')
corn_no_biogen.register_source(
    'Mixed source',
    load_class('pathway.upstream.corn_nobiogen', 'CornNoBiogen'),
    table='pathway/upstream/corn_nobiogen_lcidata.csv'
)

stover_with_biogen = upstream.register_activity('Corn stover (with biogenic carbon accounting)')
stover_with_biogen.register_source(
    'Mixed source',
    load_class('pathway.upstream.stover_withbiogen', 'StoverWithBiogen'),
    table='pathway/upstream/stover_withbiogen_lcidata.csv'
)

lwr_uranium = upstream.register_activity('Uranium for LWR nuclear power production')
lwr_uranium.register_source(
    'GREET',
    load_class('pathway.upstream.uranium_greet', 'LWRUraniumGREET'),
    table='pathway/upstream/uranium_lcidata.csv'
)

htgr_uranium = upstream.register_activity('Uranium for HTGR nuclear power production')
htgr_uranium.register_source(
    'GREET',
    load_class('pathway.upstream.uranium_greet', 'HTGRUraniumGREET'),
    table='pathway/upstream/uranium_lcidata.csv'
)

concrete_up = upstream.register_activity('Concrete')
concrete_up.register_source(
    'GREET',
    load_class('pathway.upstream.concrete_upstream', 'ConcreteUpstream'),
    table='pathway/upstream/concrete_lcidata.csv'
)

iron_up = upstream.register_activity('Iron')
iron_up.register_source(
    'GREET',
    load_class('pathway.upstream.iron_upstream', 'IronUpstream'),
)

cement_up = upstream.register_activity('Cement')
cement_up.register_source(
    'GREET',
    load_class('pathway.upstream.cement_up', 'CementUpstream'),
)

libat_up = upstream.register_activity('Li-ion battery')
libat_up.register_source(
    'GREET',
    load_class('pathway.upstream.libattery_up', 'LiBatteryUpstream'),
)

steel_up = upstream.register_activity('Steel')
steel_up.register_source(
    'GREET',
    load_class('pathway.upstream.steel_up', 'SteelUpstream'),
    table='pathway/upstream/steel_upmid_lcidata.csv'
)


dac_upstream = upstream.register_activity('DAC')
dac_upstream.register_source(
    'Default',
    load_class('pathway.upstream.dac_up', 'DAC'),
)

caes_up = upstream.register_activity('CAES_Upstream')
caes_up.register_source(
    'Default',
    load_class('pathway.upstream.caes_upstream', 'CAES_Upstream')
)

# Links

links = [
    # EndUse
    (steam, coal_steam_production),
    (steam, ng_steam_production),

    (electricity, transmission),
    (methanol, transportation_methanol),
    (lng, transportation_lng),
    (cng, cng_production),
    (gasoline, transportation_gasoline),
    (diesel, transportation_diesel),
    (lpg, transportation_lpg),
    (dme, transportation_dme),
    (hydrogen, transportation_hydrogen),

    (concrete, transportation_concrete),
    (iron,transportation_iron),
    (steel,transportation_steel),
    (cement,transportation_cement),
    (libat,libattery_production),
    (jetfuel, transportation_jetfuel),
    (dac,dac_process),

    # GateToEnduse
    (transmission, ng_power_production),
    (transmission, coal_power_production),
    (transmission, wind_power_production),
    (transmission, solar_power_production),
    (transportation_methanol, methanol_production),
    (transportation_lng, lng_production),
    (transportation_gasoline, gasoline_refining),
    (transportation_diesel, diesel_production),
    (transportation_lpg, lpg_production),
    (transportation_dme, dme_production),
    (transportation_hydrogen, hydrogen_production_SMR),
    (transportation_hydrogen, hydrogen_production_gasification),
    (transportation_hydrogen, hydrogen_production_electrolysis),
    (transmission, hydro_power_production),
    (transmission, lwr_nuclear_power_production),
    (transmission, htgr_nuclear_power_production),
    (transportation_ethanol_nobiogen, corn_ethanol_production_nobiogen),
    (transportation_ethanol_withbiogen, stover_ethanol_production_withbiogen),
    (transportation_concrete, concrete_production),
    (transportation_iron, iron_production),
    (transportation_steel, steel_production),
    (transportation_cement, cement_production),
    (transportation_jetfuel, jetfuel_production),
    (transmission, compressed_air_energy_storage),

    # Process
    (ng_power_production, transportation_ng_electricity),
    (coal_power_production, transportation_coal),
    (methanol_production, transportation_ng_non_electricity),
    (lng_production, transportation_ng_non_electricity),
    (cng_production, transportation_ng_non_electricity),
    (gasoline_refining, transportation_crude),
    (diesel_production, transportation_crude),
    (lpg_production, transportation_crude),
    (dme_production, transportation_ng_non_electricity),
    (hydrogen_production_SMR, transportation_ng_non_electricity),
    (hydrogen_production_gasification, transportation_coal),
    (coal_steam_production, transportation_coal),
    (ng_steam_production, transportation_ng_non_electricity),
    (corn_ethanol_production_nobiogen, transportation_corn),
    (stover_ethanol_production_withbiogen, transportation_stover),
    (corn_stover_ethanol, transportation_ethanol_withbiogen),
    (corn_ethanol_nobiogen, transportation_ethanol_nobiogen),
    (lwr_nuclear_power_production, transportation_uranium),
    (htgr_nuclear_power_production, transportation_uranium),
    (concrete_production,transportation_concrete_mid),
    (jetfuel_production, transportation_crude),


    # Midstream
    (transportation_ng_electricity, natural_gas),
    (transportation_ng_non_electricity, natural_gas),
    (transportation_coal, coal),
    (transportation_crude, crude_oil),
    (transportation_corn, corn_no_biogen),
    (transportation_stover, stover_with_biogen),
    (transportation_uranium, lwr_uranium),
    (transportation_uranium, htgr_uranium),
    (transportation_concrete_mid, concrete_up),

    # TEA
    (wind_power_production, wind_tea),

    # Upstream
    (hydro_power_production, hydro_power_plant),
    (wind_tea, wind_power_plant),
    (solar_power_production, solar_power_plant),
    (hydrogen_production_electrolysis, dummy),
    (iron_production, iron_up),
    (steel_production, steel_up),
    (cement_production, cement_up),
    (libattery_production, libat_up),
    (dac_process,dac_upstream),
    (compressed_air_energy_storage,caes_up),
]

for (activity_a, activity_b) in links:
    activity_a.link(activity_b)

def tag_products(activity, product, product_type):
    activity.products.add(product)
    activity.product_types.add(product_type)
    next_activities = [b for (a, b) in links if a == activity]
    for next_activity in next_activities:
        tag_products(next_activity, product, product_type)

for activity in enduse.activities:
    tag_products(activity, activity.category, activity.name)

def tag_resources(activity, resource):
    activity.resources.add(resource)
    next_activities = [a for (a, b) in links if b == activity]
    for next_activity in next_activities:
        tag_resources(next_activity, resource)

for activity in upstream.activities:
    tag_resources(activity, activity.name)

if __name__ == '__main__':
    # usage:
    #  pip install graphviz
    #  python -m pathway.topology | dot -Tpdf > pathways.pdf

    import graphviz

    dot = graphviz.Digraph()
    dot.attr('graph', rankdir='LR')

    def label(activity):
        subtext = activity.stage.name
        if activity.category:
            subtext += f' ({activity.category})'

        return f'<<B>{activity.name}</B><BR /><I>{subtext}</I>>'

    for activity_a, activity_b in links:
        dot.node(activity_b.id, label=label(activity_b))
        dot.node(activity_a.id, label=label(activity_a))
        dot.edge(activity_b.id, activity_a.id)

    print(dot.source)
