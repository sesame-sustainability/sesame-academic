from app.common import metadata_response, create_model
import analysis.system.fleet.fleet as fleet
from flask import Blueprint, request
import pandas as pd
import numpy as np

from core.inputs import InputSet

app = Blueprint('fleet', __name__)

@app.route('/metadata', methods=['GET'])
@metadata_response
def _metadata():
    user_inputs = fleet.FleetModel.user_inputs()
    return {
        'user_inputs': [
            user_input.serialize()
            for user_input in user_inputs
        ],
        'version': fleet.FleetModel.version,
    }

@app.route('/analysis', methods=['POST'])
def _analysis():
    model = create_model(fleet.FleetModel, request.json)
    outputs = model.run()

    plots = [
        {
            'label': 'Sales',
            'unit': 'million',
            'data': outputs['sales'],
            'axis': 0,
        },
        {
            'label': 'Sales Spend',
            'unit': 'billion $',
            'data': outputs['sales_spend_by_pt'],
            'axis': 0,
        },
        {
            'label': 'Stock',
            'unit': 'million',
            'data': outputs['stock'],
            'axis': 0,
        },
        {
            'label': 'Fuel Use by Car Type',
            'unit': 'TWh',
            'data': outputs['fuel'],
            'axis': 0,
        },
        {
            'label': 'Fuel Use by Fuel',
            'unit': 'TWh',
            'data': outputs['fuel_use_by_fuel'],
            'axis': 0,
        },
        {
            'label': 'Fuel Spend by Car Type',
            'unit': 'billion $',
            'data': outputs['fuel_spend_by_pt'],
            'axis': 0,
        },
        {
            'label': 'Fuel Spend by Fuel',
            'unit': 'billion $',
            'data': outputs['fuel_spend_by_fuel'],
            'axis': 0,
        },
        {
            'label': 'Total Spend by Car Type',
            'unit': 'billion $',
            'data': outputs['total_spend_by_pt'],
            'axis': 0,
        },
        {
            'label': 'Total Spend by Spend Type',
            'unit': 'billion $',
            'data': outputs['total_spend_by_spend_type'],
            'axis': 0,
        },
        {
            'label': 'Operating Emissions',
            'unit': 'MMT',
            'data': outputs['emissions'],
            'axis': 0,
        },
        {
            'label': 'Lifecycle Emissions (Car Op & Prod)',
            'unit': 'MMT',
            'data': outputs['cpe_and_oe'],
            'axis': 1,
        },
        {
            'label': 'Lifecycle Emissions since 2019',
            'unit': 'MMT',
            'data': outputs['cpe_and_oe_cumu'],
            'axis': 1,
        },
        {
            'label': 'Cost',
            'unit': 'billion $',
            'data': outputs['cost'],
            'axis': 1,
        },
        {
            'label': 'Cost since 2019',
            'unit': 'trillion $',
            'data': outputs['cost_since2019'],
            'axis': 1,
        },
        {
            'label': 'Operating Emissions since 2019',
            'unit': 'MMT',
            'data': outputs['e_cum_op'],
            'axis': 1,
        },
        {
            'label': 'Population',
            'unit': 'million',
            'data': outputs['population'],
            'axis': 1,
        },
        {
            'label': 'Sales/Person',
            'unit': 'sales/person',
            'data': outputs['sales_per_pop'],
            'axis': 1,
        },
        {
            'label': 'Light Truck Sales Share',
            'unit': '%',
            'data': outputs['f_lt'],
            'axis': 1,
        },
        {
            'label': 'Fuel/Distance (Avg Fuel Intensity)',
            'unit': 'kWh/mi',
            'data': outputs['fuel_per_dist'],
            'axis': 1,
        },
        {
            'label': 'Emissions/Distance',
            'unit': 'g/mi',
            'data': outputs['emissions_per_dist'],
            'axis': 1,
        },
        {
            'label': 'LIBs in Sales',
            'unit': 'GWh',
            'data': outputs['lib']['Sold'],
            'axis': 1,
        },
        {
            'label': 'LIBs in Fleet',
            'unit': 'GWh',
            'data': outputs['lib']['In_Use'],
            'axis': 1,
        },
        {
            'label': 'LIBs Retired, Annual',
            'unit': 'GWh',
            'data': outputs['lib']['Retired'],
            'axis': 1,
        },
        {
            'label': 'LIBs Retired since 2019',
            'unit': 'GWh',
            'data': outputs['lib']['Retired_2019'],
            'axis': 1,
        },
        {
            'label': 'Fuel/Car',
            'unit': 'MWh/car',
            'data': outputs['fuel_per_car'],
            'axis': 1,
        },

        {
            'label': 'Emissions/Car',
            'unit': 'MT/car',
            'data': outputs['emissions_per_car'],
            'axis': 1,
        },
        {
            'label': 'Distance/Car',
            'unit': 'thousand mi/car',
            'data': outputs['dist_per_car'],
            'axis': 1,
        },
        {
            'label': 'Car Production Emissions',
            'unit': 'MMT',
            'data': outputs['cpe'],
            'axis': 1,
        },
        {
            'label': 'Car Prod. GHGs / Op. GHGs',
            'unit': '%',
            'data': outputs['cpe_oe'],
            'axis': 1,
        },
        {
            'label': 'Grid emission intensity',
            'unit': 'g/kWh',
            'data': outputs['i_grid'],
            'axis': 1,
        },
        {
            'label': 'Gasoline Price',
            'unit': '$/gal',
            'data': outputs['fuel_prices']['gasoline'],
            'axis': 1,
        },
        {
            'label': 'Biofuel Price',
            'unit': '$/gal',
            'data': outputs['fuel_prices']['biofuel'],
            'axis': 1,
        },
        {
            'label': 'Gasoline + Biofuel Price',
            'unit': '$/gal',
            'data': outputs['fuel_prices']['gas_bio'],
            'axis': 1,
        },
        {
            'label': 'Diesel Price',
            'unit': '$/gal',
            'data': outputs['fuel_prices']['diesel'],
            'axis': 1,
        },
        {
            'label': 'Electricity Price',
            'unit': '$/kWh',
            'data': outputs['fuel_prices']['electricity'],
            'axis': 1,
        },
        {
            'label': 'Hydrogen Price',
            'unit': '$/kg',
            'data': outputs['fuel_prices']['hydrogen'],
            'axis': 1,
        },
    ]

    for plot in plots:
        df = plot['data']
        df = df.replace({ np.nan: None })
        df = df.loc[model.initial_year:model.final_year]
        df = df.reset_index().rename(columns={'index': 'year'})

        plot['data'] = df
        plot['columns'] = list(df.columns)

    figures = [
        {
            'name': 'fuel_dist_sales',
            'data': outputs['fuel_dist_sales'].reset_index().rename(columns={'index': 'year'}),
        },
        {
            'name': 'emission_dist_sales',
            'data': outputs['emission_dist_sales'].reset_index().rename(columns={'index': 'year'}),
        },
        {
            'name': 'fuel_dist_stock',
            'data': outputs['fuel_dist_stock'].reset_index().rename(columns={'index': 'year'}),
        },
        {
            'name': 'emission_dist_stock',
            'data': outputs['emission_dist_stock'].reset_index().rename(columns={'index': 'year'}),
        },
        {
            'name': 'fuel_spend_dist_sales',
            'data': outputs['fuel_spend_dist_sales'].reset_index().rename(columns={'index': 'year'}),
        },
        {
            'name': 'fuel_spend_dist_stock',
            'data': outputs['fuel_spend_dist_stock'].reset_index().rename(columns={'index': 'year'}),
        },
    ]

    def map_column(col):
        if type(col) != str:
            col = ' '.join(col)
        return col.strip().replace(' ', '/').replace('_', '/')

    for figure in figures:
        figure['data'].columns = [map_column(col) for col in figure['data'].columns.values]

    def onecar_data(df):
        return df.transpose().reset_index().rename(columns={'index': 'powertrain'})
    figures += [
        {
            'name': 'onecar_sedan_2020',
            'data': onecar_data(outputs['e_sedan_2020']),
        },
        {
            'name': 'onecar_LT_2020',
            'data': onecar_data(outputs['e_LT_2020']),
        },
        {
            'name': 'onecar_sedan_2030',
            'data': onecar_data(outputs['e_sedan_2030']),
        },
        {
            'name': 'onecar_LT_2030',
            'data': onecar_data(outputs['e_LT_2030']),
        },
        {
            'name': 'costs_sedan_2020',
            'data': onecar_data(outputs['costs_sedan_2020']),
        },
        {
            'name': 'costs_LT_2020',
            'data': onecar_data(outputs['costs_LT_2020']),
        },
        {
            'name': 'costs_sedan_2030',
            'data': onecar_data(outputs['costs_sedan_2030']),
        },
        {
            'name': 'costs_LT_2030',
            'data': onecar_data(outputs['costs_LT_2030']),
        },
    ]

    for figure in figures:
        df = figure['data']
        figure['data'] = df.replace({ np.nan: None })
        figure['columns'] = list(df.columns)

    power_figures = [
        {
            'name': 'power_demand_2020',
            'data': outputs.get('D_2020'),
        },
        {
            'name': 'power_demand_2035',
            'data': outputs.get('D_2035'),
        },
        {
            'name': 'power_demand_2050',
            'data': outputs.get('D_2050'),
        },
        {
            'name': 'power_generation_2020',
            'data': outputs.get('S_h_2020'),
        },
        {
            'name': 'power_generation_2035',
            'data': outputs.get('S_h_2035'),
        },
        {
            'name': 'power_generation_2050',
            'data': outputs.get('S_h_2050'),
        },
    ]

    for figure in power_figures:
        df = figure['data']
        if df is not None:
            df = df.replace({ np.nan: None })
            figure['data'] = df
            figure['columns'] = list(df.columns)
        else:
            figure['data'] = []
            figure['columns'] = []

    return {
        'plots': plots,
        'figures': figures,
        'power_figures': power_figures,
    }
