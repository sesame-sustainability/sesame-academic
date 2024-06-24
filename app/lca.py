from app.common import HTTPException, metadata_response
from core.pathway import Pathway
from flask import Blueprint, request
from schematics.exceptions import BaseError
import analysis.lca as lca
import app.validation as validation

app = Blueprint('lca', __name__)

@app.route('/metadata', methods=['GET'])
@metadata_response
def _metadata():
    return {
        'indicators': lca.indicators()
    }

@app.route('/analysis', methods=['POST'])
def _analysis():
    body = validation.LcaAnalysis(request.json)

    try:
        body.validate()
    except BaseError as e:
        raise HTTPException({ 'errors': e.to_primitive() }, 422)

    pathways = [
        Pathway.load(item, context=body.context)
        for item in body.pathways
    ]

    results = lca.run(pathways, indicator=body.indicator)
    pathway = pathways[0]

    sensitivity = pathway.sensitivity_analysis()
    if sensitivity.runnable:
        results['sensitivity'] = sensitivity.serialize()

    return results
