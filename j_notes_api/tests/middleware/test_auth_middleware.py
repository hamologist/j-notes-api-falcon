#  pylint: disable-msg=C0103,R0913
import datetime
from typing import Dict
from unittest.mock import patch, MagicMock

import pytest
from falcon import API, testing, HTTP_UNAUTHORIZED, HTTP_OK
from pymongo.collection import Collection

from j_notes_api.middleware.auth import AuthMiddleware
from j_notes_api.services import crypto


@pytest.fixture(name='auth_middleware')
def auth_middleware_fixture(client_id: str,
                            mock_users: Collection) -> AuthMiddleware:
    return AuthMiddleware(client_id, mock_users)


@pytest.fixture(name='client')
def client_fixture(auth_middleware) -> testing.TestClient:
    api = API(middleware=auth_middleware)
    api.add_route('/', testing.SimpleTestResource())

    return testing.TestClient(api)


def test_process_resource_when_authorization_header_is_empty(client: testing.TestClient):
    resp: testing.Result = client.simulate_post('/')
    assert resp.status == HTTP_UNAUTHORIZED


def test_process_resource_when_resource_is_disabled(client: testing.TestClient, auth_middleware: AuthMiddleware):
    with patch.object(auth_middleware, '_disabled_resources', (testing.SimpleTestResource,)) as _:
        resp: testing.Result = client.simulate_post('/')
        assert resp.status == HTTP_OK


def test_process_resource_when_auth_token_is_expired(client: testing.TestClient,
                                                     mock_users: MagicMock,
                                                     user_data: Dict):
    with patch.object(crypto, 'decode_jwt') as _:
        user_data['authTokenExpiry'] = datetime.datetime.now() - datetime.timedelta(hours=1)
        mock_users.find_one.return_value = user_data
        resp: testing.Result = client.simulate_post('/', headers={'Authorization': 'expired-token'})
        assert resp.status == HTTP_UNAUTHORIZED


def test_process_resource_when_user_does_not_exist(client: testing.TestClient, mock_users: MagicMock):
    with patch.object(crypto, 'decode_jwt') as _:
        mock_users.find_one.return_value = None
        resp: testing.Result = client.simulate_post('/', headers={'Authorization': 'expired-token'})
        assert resp.status == HTTP_UNAUTHORIZED


def test_process_resource_when_auth_token_is_valid(client: testing.TestClient):
    with patch.object(crypto, 'decode_jwt') as _:
        resp: testing.Result = client.simulate_post('/', headers={'Authorization': 'expired-token'})
        assert resp.status == HTTP_OK
