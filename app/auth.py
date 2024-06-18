from app.common import auth_required, HTTPException
import app.validation as validation
import core.users as users
from flask import Blueprint, request
from schematics.exceptions import DataError

app = Blueprint('auth', __name__)

@app.route('/login', methods=['POST'])
def _login():
    body = validation.Auth(request.json)

    try:
        body.validate()
    except DataError as e:
        raise HTTPException({ 'errors': e.to_primitive() }, 422)

    user = users.authenticate(body.email, body.password)
    if user is None:
        raise HTTPException({ 'errors': 'invalid email or password' }, 401)

    token = users.encode_token(user)
    return {
        'token': token,
    }

@app.route('/user', methods=['GET'])
@auth_required
def _current_user():
    user = request.current_user
    return {
        'email': user.email,
    }
