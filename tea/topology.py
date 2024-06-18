from core.tea import TeaRegistry
from core.utils import load_class
import pathway.topology as pathway_topology
# from tea.electricity.power_and_storage import PowerAndStorageTEA
# from tea.electricity.power_and_storage_v2 import PowerAndStorageTEA
import pandas as pd

tea_registry = TeaRegistry()

# registry IDs are triples of (enduse, process, upstream) activity IDs

wind = tea_registry.register_tea_analysis(
    'Wind',
    load_class('tea.electricity.wind.wind_tea', 'WindTEA'),
    table='tea/electricity/wind/region_speed_new.csv',
    pathway_id=(
        pathway_topology.electricity.id,
        pathway_topology.wind_power_production.id,
        pathway_topology.wind_power_plant.id
    ),
)

# wind_old = tea_registry.register_tea_analysis(
#     'Wind (old)',
#     load_class('tea.electricity.wind_old.wind_tea', 'WindTEA'),
#     table='tea/electricity/wind_old/region_speed_new.csv',
# )

solar = tea_registry.register_tea_analysis(
    'Solar',
    load_class('tea.electricity.solar.solar_TEA', 'SolarTEA'),
    table='pathway/process/solar/solar_cat_inputs.csv',
    pathway_id=(
        pathway_topology.electricity.id,
        pathway_topology.solar_power_production.id,
        pathway_topology.solar_power_plant.id
    ),
)

# As modified, solar_TEA_PS doesn't work as normal TEA pathway
# solar_PS = tea_registry.register_tea_analysis(
#     'Solar_PS',
#     load_class('tea.electricity.solar.solar_TEA_PS', 'SolarTEA'),
# )

ng = tea_registry.register_tea_analysis(
    'Natural gas',
    load_class('tea.electricity.ng.ng_tea', 'NaturalGasTEA'),
    table='tea/electricity/ng/ng_heatrate_cf_new.csv',
    pathway_id=(
        pathway_topology.electricity.id,
        pathway_topology.ng_power_production.id,
        pathway_topology.natural_gas.id
    ),
)


coal = tea_registry.register_tea_analysis(
    'Coal',
    load_class('tea.electricity.coal.coal_tea', 'CoalTEA'),
    table='tea/electricity/coal/coal_heatrate_cf_new.csv',
    pathway_id=(
        pathway_topology.electricity.id,
        pathway_topology.coal_power_production.id,
        pathway_topology.coal.id
    ),
)

hydropower = tea_registry.register_tea_analysis(
    'Hydropower',
    load_class('tea.electricity.hydropower.hydropower_tea','HydropowerTEA'),
)

csethanol = tea_registry.register_tea_analysis(
    'Corn stover ethanol',
    load_class('tea.chemical.corn_stover_ethanol.corn_stover_ethanol_tea', 'corn_stover_EthanolTEA'),
    table='tea/chemical/corn_stover_ethanol/corn_sotver_ethanol_production_tech.csv',
)

ethanol = tea_registry.register_tea_analysis(
    'Corn ethanol',
    load_class('tea.chemical.corn_ethanol.corn_ethanol_tea', 'corn_EthanolTEA'),
    table='tea/chemical/corn_ethanol/corn_ethanol_production_tech.csv',
)

jetfuel = tea_registry.register_tea_analysis(
    'Jet fuel',
    load_class('tea.chemical.jetfuel.jetfuel_tea', 'JetFuelTEA'),
    table='tea/chemical/jetfuel/jetfuel_input_fractions.csv',
)

diesel = tea_registry.register_tea_analysis(
    'Diesel',
    load_class('tea.chemical.diesel.diesel_tea', 'DieselTEA'),
    table='tea/chemical/diesel/diesel_input_fractions.csv',
)

lpg = tea_registry.register_tea_analysis(
    'LPG - Liquid Petroleum Gas',
    load_class('tea.chemical.lpg.lpg_tea', 'LPGTEA'),
    table='tea/chemical/lpg/lpg_input_fractions.csv',
)

gasoline = tea_registry.register_tea_analysis(
    'Gasoline',
    load_class('tea.chemical.gasoline.gasoline_tea', 'GasolineTEA'),
    table='tea/chemical/gasoline/gasoline_input_fractions.csv',
)

nuclear = tea_registry.register_tea_analysis(
    'Nuclear',
    load_class('tea.electricity.nuclear.nuclear_tea', 'NuclearTEA'),
)

steam = tea_registry.register_tea_analysis(
    'Steam',
    load_class('tea.electricity.steam.steam_tea', 'SteamTEA'),
)

storage = tea_registry.register_tea_analysis(
    'Energy storage',
    load_class('tea.electricity.storage.Storage_v3','StorageTEA'),
)

# power_and_storage = tea_registry.register(PowerAndStorageTEA('Power and storage'))
power_and_storage = tea_registry.register_tea_analysis(
    'Power and storage',
    load_class('tea.electricity.power_and_storage.power_and_storage_v3','StorageCombination'),
)

hydrogen = tea_registry.register_tea_analysis(
    'Hydrogen',
    load_class('tea.chemical.hydrogen.hydrogen_tea', 'HydrogenTEA'),
    table='tea/chemical/hydrogen/hydrogen_production_tech.csv',
    pathway_id=[(
        pathway_topology.hydrogen.id,
        pathway_topology.hydrogen_production_SMR.id,
        pathway_topology.natural_gas.id
    ),(
        pathway_topology.hydrogen.id,
        pathway_topology.hydrogen_production_electrolysis.id,
        pathway_topology.dummy.id
    )]
)

cng = tea_registry.register_tea_analysis(
    'CNG - Compressed Natural Gas',
    load_class('tea.chemical.CNG.CNG_tea', 'CNGTEA'),
)
lng = tea_registry.register_tea_analysis(
    'LNG - Liquid Natural Gas',
    load_class('tea.chemical.LNG.LNG_tea', 'LNGTEA'),
    table='tea/chemical/LNG/shipping.csv',
)

dac = tea_registry.register_tea_analysis(
    'Direct Air Capture',
   load_class('tea.electricity.ccs.dac.ccs_dac_tea', 'CcsDacTea'),
   table='tea/electricity/ccs/dac/plant_ref_data_dac.csv',
)
