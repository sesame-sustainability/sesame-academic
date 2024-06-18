import app
import json
import pathway.topology as pathway_topology
import pytest
from core.inputs import InputSet

@pytest.fixture
def client():
    flask_app = app.app
    testing_client = flask_app.test_client()
    ctx = flask_app.app_context()
    ctx.push()
    yield testing_client
    ctx.pop()

def test_pathway_metadata(client):
    res = client.get('/pathway/metadata')
    assert res.status_code == 200
    body = json.loads(res.data)
    assert len(body['stages']) == 6

def test_pathway_input_options(client):
    source = pathway_topology.ng_power_production.sources[1] # ASPEN
    res = client.get(f'/pathway/sources/{source.id}/user_inputs/turbine')
    assert res.status_code == 200
    body = json.loads(res.data)
    assert body == {'options': ['Gas Turbine', 'Combined Cycle']}

def test_pathway_input_options_numerical(client):
    path = f'/pathway/sources/process-solarpowerproduction-default/user_inputs/install_type?location=US NE (Boston)'
    res = client.get(path)
    assert res.status_code == 200
    body = json.loads(res.data)
    assert body == {'options': ['residential', 'utility, fixed tilt', 'utility, 1-axis tracking']}

# LCA

def test_lca_analysis(client):
    source = pathway_topology.electricity.sources[0]
    body = {
        'pathways': [
            {'steps': [{'source_id': source.id, 'user_inputs': []}]}
        ],
        'indicator': 'GWP',
        'context': { 'foo': 'bar' },
    }
    res = client.post(
        '/lca/analysis',
        data=json.dumps(body),
        content_type='application/json'
    )
    assert res.status_code == 200

def test_lca_analysis_input_validation(client):
    source = pathway_topology.transportation_ng_electricity.sources[0]

    body = {
        'pathways': [
            {'steps': [{'source_id': source.id, 'user_inputs': ['pipeline', 500, 123]}]} # must be < 100
        ]
    }
    res = client.post(
        '/lca/analysis',
        data=json.dumps(body),
        content_type='application/json'
    )
    assert res.status_code == 422
    print(res.json)
    assert res.json['errors'] == {'loss_factor': ['must be less than or equal to 100']}

def test_lca_analysis_validation_error(client):
    source = pathway_topology.electricity.sources[0]
    body = {
        'pathways': []
    }
    res = client.post(
        '/lca/analysis',
        data=json.dumps(body),
        content_type='application/json'
    )
    assert res.status_code == 422
    body = json.loads(res.data)
    assert 'pathways' in body['errors']

# TEA

# def test_tea_analysis(client):
#     body = {
#         'analysis_name': 'Wind',
#         'user_inputs': ['State', 'California', 'onshore', 600, 0.7, 'NREL', 3, 47, 'ATB', 1, 6.35],
#     }
#     res = client.post(
#         '/tea/analysis',
#         data=json.dumps(body),
#         content_type='application/json'
#     )
#     assert res.status_code == 200

# def test_tea_analysis_input_validation(client):
#     body = {
#         'analysis_name': 'Wind',
#         'user_inputs': ['State', 'California', 'onshore', 600, 0.7, 'NREL', 3, 47, 'ATB', 1, 'invalid'],
#     }
#     res = client.post(
#         '/tea/analysis',
#         data=json.dumps(body),
#         content_type='application/json'
#     )
#     assert res.status_code == 422
#     assert res.json['errors'] == {
#         'tax_rate': ['must be numeric'],
#     }

# def test_tea_analysis_with_pathway(client):
#     body = {
#         'pathway': {
#             'steps': [
#                 {'source_id': 'enduse-electricity-default', 'user_inputs': []},
#                 {'source_id': 'gatetoenduse-transmission-literaturereview', 'user_inputs': [4.68]},
#                 {'source_id': 'process-windpowerproduction-default', 'user_inputs': ['onshore wind farm > 50MW', 'Wind Speed', 'medium (8 m/s)', 100, '2014-2016', 'Typical Onshore md-spd', 20, 600]},
#                 {'source_id': 'tea-windtea-default', 'user_inputs': ['California', 600, 0.7, 'NREL', 47, 'ATB', 1, 6.35] },
#                 {'source_id': 'upstream-wind-default', 'user_inputs': []},
#             ],
#             'name': 'Wind LCA + TEA pathway',
#         },
#     }
#     res = client.post(
#         '/tea/analysis',
#         data=json.dumps(body),
#         content_type='application/json'
#     )
#     assert res.status_code == 200

# fleet

from analysis.system.fleet.fleet import FleetModel

def test_fleet_metadata(client):
    res = client.get('/fleet/metadata')
    assert res.status_code == 200

def test_fleet_analysis(client):
    input_set = InputSet.build_default(FleetModel)
    res = client.post(
        '/fleet/analysis',
        data=json.dumps(input_set.values),
        content_type='application/json',
    )
    assert res.status_code == 200

# grid

from analysis.system.grid.grid import Grid

def test_grid_metadata(client):
    res = client.get('/grid/metadata')
    assert res.status_code == 200

def test_grid_analysis(client):
    input_set = InputSet.build_default(Grid)
    res = client.post(
        '/grid/analysis',
        data=json.dumps(input_set.values),
        content_type='application/json',
    )
    assert res.status_code == 200

# industry cement

from analysis.system.industry.cement.cement import Cement

def test_cement_metadata(client):
    res = client.get('/industry/cement/metadata')
    assert res.status_code == 200

def test_cement_analysis(client):
    input_set = InputSet.build_default(Cement)
    res = client.post(
        '/industry/cement/analysis',
        data=json.dumps(input_set.values),
        content_type='application/json',
    )
    assert res.status_code == 200

# industry steel

from analysis.system.industry.iron_steel.iron_steel import IronSteel

def test_steel_metadata(client):
    res = client.get('/industry/steel/metadata')
    assert res.status_code == 200

def test_steel_analysis(client):
    for route, _ in IronSteel.routes:
        input_set = InputSet.build_default(IronSteel, values={'route': route})

        res = client.post(
            '/industry/steel/analysis',
            data=json.dumps(input_set.values),
            content_type='application/json',
        )
        assert res.status_code == 200

# industry aluminum

from analysis.system.industry.aluminum.aluminum import Aluminum

def test_aluminum_metadata(client):
    res = client.get('/industry/aluminum/metadata')
    assert res.status_code == 200

def test_aluminum_analysis(client):
    for route, _ in Aluminum.routes:
        input_set = InputSet.build_default(Aluminum, values={'route': route})

        res = client.post(
            '/industry/aluminum/analysis',
            data=json.dumps(input_set.values),
            content_type='application/json',
        )
        assert res.status_code == 200

# industry fleet

from analysis.system.industrial_fleet.industrial_fleet import IndFleetModel

def test_industrial_fleet_metadata(client):
    res = client.get('/industry/fleet/metadata')
    assert res.status_code == 200

def test_industrial_fleet_analysis(client):
    for industry, _ in IndFleetModel.industries:
        input_set = InputSet.build_default(IndFleetModel, values={
            'industry': industry,
            'steel_scen': 'Reference',
        })

        res = client.post(
            '/industry/fleet/analysis',
            data=json.dumps(input_set.values),
            content_type='application/json',
        )
        assert res.status_code == 200
