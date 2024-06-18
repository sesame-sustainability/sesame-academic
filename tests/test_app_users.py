import pytest
from sqlalchemy import event

import app
import core.db as db
import core.users as users


@pytest.fixture
def client():
    db.test_mode_enable()

    flask_app = app.app
    testing_client = flask_app.test_client()
    ctx = flask_app.app_context()
    ctx.push()
    yield testing_client
    ctx.pop()

    db.test_mode_disable()


def test_current_user_authorized(client):
    user = users.create('test+1@example.com', 'supersecret')
    token = users.encode_token(user)
    res = client.get(
        '/users/current',
        headers={
            'Authorization': f'Bearer {token}',
        },
    )
    assert res.status_code == 200


def test_current_user_unauthorized(client):
    res = client.get(
        '/users/current',
        content_type='application/json'
    )
    assert res.status_code == 401


def test_update_current_user_valid(client):
    user = users.create('test+2@example.com', 'supersecret')
    token = users.encode_token(user)
    body = {
        'name': 'foo',
        'institution': 'bar',
    }
    res = client.put(
        '/users/current',
        json=body,
        headers={
            'Authorization': f'Bearer {token}',
        },
    )
    assert res.status_code == 200

    user = users.find(user.id)
    assert user.email == 'test+2@example.com'
    assert user.name == 'foo'
    assert user.institution == 'bar'


def test_update_current_user_invalid(client):
    user = users.create('test+3@example.com', 'supersecret')
    token = users.encode_token(user)
    body = {
        'name': 'foo',
    }
    res = client.put(
        '/users/current',
        json=body,
        headers={
            'Authorization': f'Bearer {token}',
        },
    )
    assert res.status_code == 422


def test_update_current_unauthorizd(client):
    res = client.put(
        '/users/current',
        json={},
    )
    assert res.status_code == 401
