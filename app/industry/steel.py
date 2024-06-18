from app.common import metadata_response, create_model
from analysis.system.industry.iron_steel.iron_steel import IronSteel
from flask import Blueprint, request

app = Blueprint('industry/steel', __name__)

@app.route('/metadata', methods=['GET'])
@metadata_response
def _metadata():
    return {
        'user_inputs': [
            input.serialize()
            for input in IronSteel.inputs()
        ],
        'version': IronSteel.version,
    }

@app.route('/analysis', methods=['POST'])
def _analysis():
    model = create_model(IronSteel, request.json)
    results = model.run()

    return {
        'figures': model.figures(results),
        'years': list(range(2020, 2040 + 1, 5)),
    }
