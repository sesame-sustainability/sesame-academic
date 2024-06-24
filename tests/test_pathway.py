from core.pathway import Pathway
import pathway.topology


context = {
    'compute_cost': True,
}

def test_solar_pathway():
    pathway = Pathway.build([
        'enduse-electricity-default',
        'gatetoenduse-transmission-literaturereview',
        'process-solarpowerproduction-default',
        'upstream-solar-default',
    ], context=context)
    process = pathway.steps[2]
    assert process.input_set.context['compute_cost']
    assert process.input_set.values['interest_rate'] == 4

    results = pathway.perform()
    assert results is not None

def test_ng_pathway():
    pathway = Pathway.build([
        'enduse-electricity-default',
        'gatetoenduse-transmission-literaturereview',
        'process-ngpowerproduction-greet',
        'upstream-naturalgas-greet',
    ], context=context)

    results = pathway.perform()
    assert results is not None

    pathway = Pathway.build([
        'enduse-electricity-default',
        'gatetoenduse-transmission-literaturereview',
        'process-ngpowerproduction-aspen',
        'upstream-naturalgas-greet',
    ], context=context)

    results = pathway.perform()
    assert results is not None

def test_coal_pathway():
    pathway = Pathway.build([
        'enduse-electricity-default',
        'gatetoenduse-transmission-literaturereview',
        'process-coalpowerproduction-greet',
        'upstream-coal-greet',
    ], context=context)

    results = pathway.perform()
    assert results is not None

    pathway = Pathway.build([
        'enduse-electricity-default',
        'gatetoenduse-transmission-literaturereview',
        'process-coalpowerproduction-aspen',
        'upstream-coal-greet',
    ], context=context)

    results = pathway.perform()
    assert results is not None

def test_h2_pathway():
    pathway = Pathway.build([
        'enduse-hydrogen-default',
        'gatetoenduse-hydrogengastransportation-greet',
        'process-productionusingsmr-greet',
        'midstream-ngnonelectricitytransportation-greet',
        'upstream-naturalgas-greet',
    ], context=context)

    results = pathway.perform()
    assert results is not None
