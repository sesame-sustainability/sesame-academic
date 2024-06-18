import analysis.tea as tea
from app.common import HTTPException, metadata_response, input_info
import app.validation as validation
from core.inputs import InputSet
from core.tea import TeaPathway, pathway_id
from core.pathway import Pathway
from flask import Blueprint, request
from schematics.exceptions import BaseError
from tea.topology import tea_registry

app = Blueprint('tea', __name__)

@app.route('/metadata', methods=['GET'])
@metadata_response
def _tea_metadata():
    return {
        'analyses': tea_registry.serialize()
    }

@app.route('/analyses/<analysis_name>/user_inputs/<input_name>', methods=['GET'])
def _user_input(analysis_name, input_name):
    tea_analysis = tea_registry.lookup_by_name(analysis_name)
    if tea_analysis is None:
        raise HTTPException('no such analysis', 404)

    return input_info(tea_analysis, input_name, request.args)

@app.route('/analysis', methods=['POST'])
def _analysis():
    body = validation.TeaAnalysis(request.json)

    try:
        body.validate()
    except BaseError as e:
        raise HTTPException({ 'errors': e.to_primitive() }, 422)

    analysis_name = body.analysis_name
    tea_pathway = None

    if analysis_name is not None:
        tea_analysis = tea_registry.lookup_by_name(analysis_name)
        tea_pathway = TeaPathway.load(tea_analysis, body.user_inputs)
    else:
        pathway = Pathway.load(body.pathway, context={'compute_cost': True})
        pathway.perform()

        tea_analysis = tea_registry.lookup_by_pathway_id(pathway_id(pathway))
        tea_pathway = TeaPathway(tea_analysis, lca_pathway=pathway)

    results = tea.run(tea_pathway)

    sensitivity = tea_pathway.sensitivity_analysis()
    if sensitivity is not None:
        results['sensitivity'] = sensitivity.serialize()

    return results
