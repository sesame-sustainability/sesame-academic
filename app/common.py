from core.common import JSONEncoder
from core.inputs import InputSet
import core.users as users
from flask import request, Response
import hashlib
import json
import math
import numbers
import numpy as np
import pandas as pd
from schematics.exceptions import BaseError

class HTTPException(Exception):

    def __init__(self, data, status_code=500):
        super().__init__()
        if isinstance(data, str):
            self.data = {'error': data}
        else:
            self.data = data
        self.status_code = status_code

    def serialize(self):
        return self.data, self.status_code


def auth_required(f):
    def decorator(*args, **kwargs):
        auth = request.headers.get('authorization', None)
        if not auth:
            raise HTTPException({ 'errors': 'unauthorized' }, 401)

        token_type, token = auth.split(' ')
        user = None
        if token_type.lower() == 'bearer':
            user = users.decode_token(token)
        if user is None:
            raise HTTPException({ 'errors': 'unauthorized' }, 401)

        request.current_user = user

        return f(*args, **kwargs)
    return decorator


def metadata_response(f):
    def decorator(*args, **kwargs):
        data = f(*args, **kwargs)
        text = json.dumps(data, cls=JSONEncoder)
        sha = hashlib.sha256()
        sha.update(text.encode('utf-8'))
        data['hash'] = sha.hexdigest()
        return data
    return decorator


def create_model(model_class, input_values):
    input_set = InputSet(model_class.inputs(), input_values)

    try:
        input_set.validate()
    except BaseError as e:
        raise HTTPException({ 'errors': e.to_primitive() }, 422)

    model = model_class()
    model.prepare(input_set)
    return model


def input_info(model_class, input_name, input_values):
    input_set = InputSet(model_class.inputs())

    input = input_set.input(input_name)
    if input is None:
        raise HTTPException('no such user input', 404)
    if input.input_type != 'categorical':
        raise HTTPException('user input is not categorical', 422)

    for input_name, input_value in input_values.items():
        input_set.set_value(input_name, input_value)

    model = model_class()
    model.prepare(input_set)

    return {
        'options': model.categorical_options(input),
    }
