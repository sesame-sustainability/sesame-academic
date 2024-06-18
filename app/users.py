from flask import Blueprint, request
from schematics.exceptions import DataError
from schematics.models import Model
from schematics.types import StringType, IntType, FloatType, ListType, ModelType, UnionType, DictType, BaseType

from app.common import auth_required, HTTPException
import core.users as users


app = Blueprint('users', __name__)


class Profile(Model):
    email = StringType(required=True)
    name = StringType(required=True)
    institution = StringType(required=True)


def serialize_user(user):
    return {
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'institution': user.institution,
    }


def show_current_user():
    return serialize_user(request.current_user)


def update_current_user():
    user = request.current_user

    profile = Profile({
        'email': user.email,
        'name': user.name,
        'institution': user.institution,
        **request.json,
    })

    try:
        profile.validate()
    except DataError as e:
        raise HTTPException({ 'errors': e.to_primitive() }, 422)

    user_id = request.current_user.id
    user = users.update(user_id, {
        'email': profile.email,
        'name': profile.name,
        'institution': profile.institution,
    })

    return serialize_user(user)


@app.route('/current', methods=['GET', 'PUT', 'PATCH'])
@auth_required
def _current():
    if request.method == 'GET':
        return show_current_user()
    elif request.method == 'PUT' or request.method == 'PATCH':
        return update_current_user()
