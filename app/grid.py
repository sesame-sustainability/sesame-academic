from app.common import metadata_response, create_model
import analysis.system.grid.grid as grid
from flask import Blueprint, request
import pandas as pd
import numpy as np

from core.inputs import InputSet

app = Blueprint('grid', __name__)

@app.route('/metadata', methods=['GET'])
@metadata_response
def _metadata():
    user_inputs = grid.Grid.user_inputs()
    return {
        'user_inputs': [user_input.serialize() for user_input in user_inputs],
        'version': grid.Grid.version,
    }

@app.route('/analysis', methods=['POST'])
def _analysis():
    model = create_model(grid.Grid, request.json)
    results = model.run()

    def round_down(value):
        if value < 0.001:
            return 0
        else:
            return value

    def dataset(df, **kwargs):
        data = df.replace({ np.nan: None }).applymap(round_down)
        data = data.reset_index().rename(columns={'index': 'year'})
        dataset = {
            'data': data,
            'columns': list(data.columns),
        }
        dataset.update(kwargs)
        return dataset

    generation_by_enduse = pd.DataFrame(index=results['DnEV'].index)
    generation_by_enduse['EV'] = results['DEV']
    generation_by_enduse['non-EV'] = results['DnEV']

    colors = {
        'blue': '#5B9BD5',
        'green': '#62993E',
        'yellow': '#FFC000',
        'orange': '#ED7D31',
        'gray': '#929292',
        'black': '#000000',
        'red': '#FF0000',
        'purple': 'purple',
    }

    power_sources = [
        { 'key': 'Solar', 'label': 'Solar', 'color': colors['yellow'] },
        { 'key': 'Wind', 'label': 'Wind', 'color': colors['green'] },
        { 'key': 'Other', 'label': 'Other', 'color': colors['purple'] },
        { 'key': 'Hydro', 'label': 'Hydro', 'color': colors['blue'] },
        { 'key': 'Coal', 'label': 'Coal', 'color': colors['black'] },
        { 'key': 'Natural gas', 'label': 'Gas', 'color': colors['gray'] },
        { 'key': 'Nuclear', 'label': 'Nuc', 'color': colors['orange'] },
    ]

    return {
        'figures': {
            'demand': {
                'title': 'Demand (GW) vs. hour',
                'type': 'area',
                'datasets': [
                    dataset(results['DEV_h_y'], label='EV', color=colors['orange']),
                    dataset(results['DnEV_h_y'], label='non-EV', color=colors['blue']),
                ],
            },
            'generation_stacked': {
                'title': 'Generation (GW) vs. hour',
                'type': 'area',
                'datasets': [
                    dataset(results['S_p_h'][source['key']], label=source['label'], color=source['color'])
                    for source in power_sources
                ] + [
                    dataset(results['D_h_y'], label='Demand', type='line', color=colors['red']),
                ],
            },
            'generation_line': {
                'title': 'Generation (GW) vs. hour',
                'type': 'line',
                'datasets': [
                    dataset(results['S_p_h'][source['key']], label=source['label'], color=source['color'])
                    for source in power_sources
                ] + [
                    dataset(results['from_storage'], label='from S', type='line', color=colors['red']),
                    dataset(results['to_storage'], label='to S', type='line', color=colors['red'], style='dashed'),
                ],
            },
            'multi': [
                dataset(results['G_p'], label='Generation by power type', unit='TWh', axis=0),
                dataset(generation_by_enduse, label='Generation by end use', unit='TWh', axis=0),
                dataset(results['e_powertype'], label='Emissions by power type', unit='MMT', axis=0),
                dataset(results['e_enduse'], label='Emissions by end use', unit='MMT', axis=0),
                dataset(results['e_stage'].drop(columns=['e_tot']), label='Emissions by stage', unit='MMT', axis=0),

                dataset(results['S'], label='Emission intensity, smokestack', unit='g/kWh', axis=1),
                dataset(results['L'], label='Emission intensity, lifecycle', unit='g/kWh', axis=1),
                dataset(results['e_cumulative_ss'], label='Emissions since 2019, smokestack', unit='MMT', axis=1),
                dataset(results['e_cumulative_lc'], label='Emissions since 2019, lifecycle', unit='MMT', axis=1),
                dataset(results['fraction_gen_stored'], label='% generation stored', unit='%', axis=1),
            ]
        },
    }
