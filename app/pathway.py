from app.common import HTTPException, metadata_response, input_info
from core.inputs import InputSet
from core.pathway import Step, sources_db
from flask import Blueprint, request
from pathway.topology import metadata, links

app = Blueprint('pathway', __name__)

@app.route('/metadata', methods=['GET'])
@metadata_response
def _metadata():
    res = metadata.serialize()
    res['links'] = [
        (activity_a.id, activity_b.id)
        for (activity_a, activity_b) in links
    ]
    return res

@app.route('/sources/<source_id>/user_inputs/<input_name>', methods=['GET'])
def _input_options(source_id, input_name):
    source = sources_db.find(source_id)
    if source is None:
        raise HTTPException('no such source', 404)
    return input_info(source, input_name, request.args)
