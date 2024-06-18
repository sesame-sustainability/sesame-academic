from app.common import metadata_response, create_model
from analysis.system.industry.aluminum.aluminum import Aluminum
from flask import Blueprint, request

app = Blueprint('industry/aluminum', __name__)

@app.route('/metadata', methods=['GET'])
@metadata_response
def _metadata():
    return {
        'user_inputs': [
            input.serialize()
            for input in Aluminum.inputs()
        ],
        'version': Aluminum.version,
    }

@app.route('/analysis', methods=['POST'])
def _analysis():
    model = create_model(Aluminum, request.json)
    results = model.run()
    return {
        'figures': model.figures(results),
        'years': list(range(2020, 2040 + 1, 5)),
    }
