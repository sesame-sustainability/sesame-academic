from app.common import metadata_response, create_model, input_info
from analysis.system.pps.power_plus_storage import PPS
from flask import Blueprint, request

app = Blueprint('pps', __name__)

@app.route('/metadata', methods=['GET'])
@metadata_response
def _metadata():
    return {
        'user_inputs': [
            input.serialize()
            for input in PPS.inputs()
        ],
        'version': PPS.version,
    }

@app.route('/user_inputs/<input_name>', methods=['GET'])
def _user_input(input_name):
    return input_info(PPS, input_name, request.args)

@app.route('/analysis', methods=['POST'])
def _analysis():
    model = create_model(PPS, request.json)
    results = model.run()
    return results
