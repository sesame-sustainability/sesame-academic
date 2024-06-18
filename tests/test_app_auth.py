import app
import core.db as db
import core.users as users
import json
import pytest


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


def test_login_unauthorized(client):
    body = { 'email': 'test@example.com', 'password': 'supersecret' }
    res = client.post(
        '/auth/login',
        data=json.dumps(body),
        content_type='application/json'
    )
    assert res.status_code == 401


def test_login_missing_params(client):
    body = {}
    res = client.post(
        '/auth/login',
        data=json.dumps(body),
        content_type='application/json'
    )
    assert res.status_code == 422


def test_login_valid(client):
    user = users.create('test@example.com', 'supersecret')
    body = { 'email': 'test@example.com', 'password': 'supersecret' }
    res = client.post(
        '/auth/login',
        data=json.dumps(body),
        content_type='application/json'
    )
    assert res.status_code == 200


def test_user_unauthorized(client):
    res = client.get('/auth/user')
    assert res.status_code == 401


def test_user_authorized(client):
    user = users.create('test@example.com', 'supersecret')
    token = users.encode_token(user)
    res = client.get(
        '/auth/user',
        headers={
            'Authorization': f'Bearer {token}',
        },
    )
    assert res.status_code == 200
