from app.common import HTTPException, metadata_response
from core.inputs import InputSet
from flask import Blueprint, request
from schematics.exceptions import DataError
from schematics.models import Model
from schematics.types import StringType, IntType, FloatType, ListType, ModelType, UnionType, DictType
from analysis.system.power_historic import analyses as system_analyses
from analysis.system.power_historic import years as system_years

app = Blueprint('power_historic', __name__)

class Analysis(Model):
    analysis_name = StringType(required=True)
    user_inputs = ListType(UnionType((IntType, FloatType, StringType)))

    def validate_analysis_name(self, data, values):
        analysis_name = data['analysis_name']
        if analysis_name not in system_analyses.keys():
            raise ValidationError('unknown analysis')

    def validate_user_inputs(self, data, values):
        analysis = system_analyses[data['analysis_name']]
        input_set = InputSet(analysis.inputs.copy())
        input_set.build(values)
        input_set.validate()

@app.route('/metadata', methods=['GET'])
@metadata_response
def _metadata():
    return {
        'analyses': [
            analysis.serialize()
            for analysis in system_analyses.values()
        ]
    }

@app.route('/analyses/<analysis_name>/user_inputs/<input_name>', methods=['GET'])
def _user_input(analysis_name, input_name):
    analysis = system_analyses[analysis_name]
    options = system_years()
    return {
        'options': options
    }

@app.route('/analysis', methods=['POST'])
def _analysis():
    body = None

    try:
        body = Analysis(request.json)
        body.validate()
    except DataError as e:
        raise HTTPException({ 'errors': e.to_primitive() }, 422)

    analysis = system_analyses[body.analysis_name]
    input_set = InputSet(analysis.inputs.copy())
    input_set.build(body.user_inputs)

    results = analysis.run(input_set)

    return {
        'data': list(results)
    }
