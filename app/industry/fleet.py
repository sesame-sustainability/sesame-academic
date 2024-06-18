from app.common import metadata_response, create_model
from analysis.system.industrial_fleet.industrial_fleet import IndFleetModel
from core.inputs import InputSet
from flask import Blueprint, request
from schematics.exceptions import BaseError

app = Blueprint('industry/fleet', __name__)

@app.route('/metadata', methods=['GET'])
@metadata_response
def _metadata():
    return {
        'user_inputs': [
            input.serialize()
            for input in IndFleetModel.inputs()
        ],
        'version': IndFleetModel.version,
    }

@app.route('/analysis', methods=['POST'])
def _analysis():
    model = create_model(IndFleetModel, request.json)
    results = model.run()

    return {
        'figures': model.figures(results),
        'years': list(range(2020, 2050 + 1, 5)),
    }
