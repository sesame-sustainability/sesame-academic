import pandas as pd
import tests.helper as helper

import analysis.lca as lca
import analysis.tea as tea
from analysis.system.fleet.fleet import FleetModel
from core.tea import TeaPathway
from tea.topology import tea_registry

def test_lca():
    data = lca.run([helper.random_pathway(), helper.random_pathway()])
    assert type(data) == dict
    assert type(data['data']) == pd.DataFrame

