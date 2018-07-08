#  pylint: disable-msg=C0103,R0913
import datetime
from typing import Dict
from unittest.mock import MagicMock, patch

import pytest
from _pytest.monkeypatch import MonkeyPatch
from bson import ObjectId
from falcon import API, HTTP_OK, HTTP_UNAUTHORIZED, HTTP_INTERNAL_SERVER_ERROR
from falcon.testing import TestClient, Result

from j_notes_api.app import RESOURCE_MAP
from j_notes_api.models import User, IdInfo, AuthProvider
from j_notes_api.resources import SessionsResource
from j_notes_api.resources.sessions import AuthProviderMissingUserException


@pytest.fixture(name='session_path')
def session_path_fixture() -> str:
    return RESOURCE_MAP[SessionsResource]


@pytest.fixture(name='mock_client_id')
def mock_client_id_fixture() -> str:
    return 'mock-client-id'


@pytest.fixture(name='mock_insert_one')
def mock_insert_one_result_fixture() -> MagicMock:
    mock = MagicMock()
    mock.inserted_id.return_value = ObjectId()

    return mock


@pytest.fixture(name='mock_auth_providers')
def mock_auth_providers_fixture(mock_insert_one: MagicMock, auth_provider_data: Dict) -> MagicMock:
    mock = MagicMock()
    mock.insert_one.return_value = mock_insert_one
    mock.find_one.return_value = auth_provider_data

    return mock


@pytest.fixture(name='mock_users')
def mock_users_fixture(mock_insert_one: MagicMock, user_data: Dict) -> MagicMock:
    mock = MagicMock()
    mock.insert_one.return_value = mock_insert_one
    mock.find_one.return_value = user_data

    return mock


@pytest.fixture(name='sessions_resource')
def sessions_resource_fixture(mock_client_id: str,
                              mock_auth_providers: MagicMock,
                              mock_users: MagicMock) -> SessionsResource:
    return SessionsResource(mock_client_id, mock_auth_providers, mock_users)


@pytest.fixture(name='client')
def client_fixture(sessions_resource: SessionsResource, session_path: str) -> TestClient:
    api = API()
    api.add_route(session_path, sessions_resource)

    return TestClient(api)


def test_on_post_using_valid_id_token(client: TestClient,
                                      session_path: str,
                                      id_info_data: Dict,
                                      user: User,
                                      auth_provider: AuthProvider,
                                      monkeypatch: MonkeyPatch):
    with patch.object(SessionsResource, 'process_id_info') as mock_process_id_info:
        mock_process_id_info.return_value = user, auth_provider
        monkeypatch.setattr('google.oauth2.id_token.verify_oauth2_token', lambda *_: id_info_data)
        resp: Result = client.simulate_post(session_path)
        assert mock_process_id_info.called
        assert resp.status == HTTP_OK


def test_on_post_using_invalid_id_token(client: TestClient, session_path: str, monkeypatch: MonkeyPatch):
    def raise_value_error(*_):
        raise ValueError('Test Value Error')

    monkeypatch.setattr('google.oauth2.id_token.verify_oauth2_token', raise_value_error)
    resp: Result = client.simulate_post(session_path)
    assert resp.status == HTTP_UNAUTHORIZED


def test_on_post_when_auth_provider_missing_exception_is_raised(client: TestClient,
                                                                session_path: str,
                                                                id_info_data: Dict,
                                                                monkeypatch: MonkeyPatch):
    with patch.object(SessionsResource, 'process_id_info') as mock_process_id_info:
        mock_process_id_info.side_effect = AuthProviderMissingUserException('mock-uuid')
        monkeypatch.setattr('google.oauth2.id_token.verify_oauth2_token', lambda *_: id_info_data)
        resp: Result = client.simulate_post(session_path)
        assert mock_process_id_info.called
        assert resp.status == HTTP_INTERNAL_SERVER_ERROR


def test_on_post_when_an_unhandled_exception_is_raised(client: TestClient,
                                                       session_path: str,
                                                       id_info_data: Dict,
                                                       monkeypatch: MonkeyPatch):
    with patch.object(SessionsResource, 'process_id_info') as mock_process_id_info:
        mock_process_id_info.side_effect = Exception('This was unexpected.')
        monkeypatch.setattr('google.oauth2.id_token.verify_oauth2_token', lambda *_: id_info_data)
        with pytest.raises(Exception):
            resp: Result = client.simulate_post(session_path)
            assert mock_process_id_info.called
            assert resp.status == HTTP_INTERNAL_SERVER_ERROR


def test_process_id_info_when_auth_token_is_expired(sessions_resource: SessionsResource,
                                                    id_info: IdInfo,
                                                    mock_users: MagicMock,
                                                    mock_auth_providers: MagicMock,
                                                    auth_provider_data: Dict,
                                                    user_data: Dict):
    with patch.object(SessionsResource, 'update_auth_token') as mock_update_auth_token:
        user_data['authTokenExpiry'] = datetime.datetime.now() - datetime.timedelta(hours=1)
        mock_auth_providers.find_one.return_value = auth_provider_data
        mock_users.find_one.return_value = user_data
        sessions_resource.process_id_info(id_info)
        assert mock_update_auth_token.called


def test_process_id_info_when_auth_token_is_valid(sessions_resource: SessionsResource,
                                                  id_info: IdInfo,
                                                  mock_users: MagicMock,
                                                  mock_auth_providers: MagicMock,
                                                  auth_provider_data: Dict,
                                                  user_data: Dict):
    with patch.object(SessionsResource, 'update_auth_token') as mock_update_auth_token:
        mock_auth_providers.find_one.return_value = auth_provider_data
        mock_users.find_one.return_value = user_data
        sessions_resource.process_id_info(id_info)
        assert not mock_update_auth_token.called


def test_process_id_info_when_auth_provider_does_not_exist(sessions_resource: SessionsResource,
                                                           id_info: IdInfo,
                                                           mock_auth_providers: MagicMock):
    mock_auth_providers.find_one.return_value = None
    user, auth_provider = sessions_resource.process_id_info(id_info)

    assert isinstance(user, User)
    assert isinstance(auth_provider, AuthProvider)


def test_process_id_info_when_auth_provider_exists_but_user_does_not(sessions_resource: SessionsResource,
                                                                     id_info: IdInfo,
                                                                     mock_users: MagicMock):
    mock_users.find_one.return_value = None
    with pytest.raises(AuthProviderMissingUserException):
        sessions_resource.process_id_info(id_info)


def test_create_new_user(sessions_resource: SessionsResource, id_info: IdInfo):
    user, auth_provider = sessions_resource.create_new_user(id_info)

    assert isinstance(user, User)
    assert isinstance(auth_provider, AuthProvider)


def test_update_auth_token(sessions_resource: SessionsResource, user: User):
    old_auth_token = user.auth_token
    old_auth_token_expiry = user.auth_token_expiry
    sessions_resource.update_auth_token(user)
    new_auth_token = user.auth_token
    new_auth_token_expiry = user.auth_token_expiry

    assert isinstance(new_auth_token, str)
    assert isinstance(new_auth_token_expiry, datetime.datetime)
    assert old_auth_token != new_auth_token
    assert old_auth_token_expiry < new_auth_token_expiry


def test_generate_token(sessions_resource: SessionsResource):
    token = sessions_resource.generate_token()

    assert isinstance(token, str)
    assert len(token) == 64
