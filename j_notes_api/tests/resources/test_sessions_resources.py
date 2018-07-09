#  pylint: disable-msg=C0103,R0913
import datetime
from typing import Dict, Union
from unittest.mock import MagicMock, patch

import pytest
from _pytest.monkeypatch import MonkeyPatch
from falcon import API, HTTP_OK, HTTP_UNAUTHORIZED, HTTP_INTERNAL_SERVER_ERROR, testing

from j_notes_api.app import RESOURCE_MAP
from j_notes_api.models import User, IdInfo, AuthProvider
from j_notes_api.resources import SessionsResource
from j_notes_api.resources.sessions import AuthProviderMissingUserException
from j_notes_api.services import UserService


@pytest.fixture(name='session_path')
def session_path_fixture() -> str:
    return RESOURCE_MAP[SessionsResource]


@pytest.fixture(name='mock_user_service')
def mock_user_service_fixture(user: User, auth_provider: AuthProvider) -> Union[UserService, MagicMock]:
    mock = MagicMock()
    mock.create_new_user.return_value = user, auth_provider
    return mock


@pytest.fixture(name='sessions_resource')
def sessions_resource_fixture(client_id: str,
                              mock_auth_providers: MagicMock,
                              mock_users: MagicMock,
                              mock_user_service: Union[UserService, MagicMock]) -> SessionsResource:
    return SessionsResource(client_id, mock_auth_providers, mock_users, mock_user_service)


@pytest.fixture(name='client')
def client_fixture(sessions_resource: SessionsResource, session_path: str) -> testing.TestClient:
    api = API()
    api.add_route(session_path, sessions_resource)

    return testing.TestClient(api)


def test_on_post_using_valid_id_token(client: testing.TestClient,
                                      session_path: str,
                                      id_info_data: Dict,
                                      user: User,
                                      auth_provider: AuthProvider,
                                      monkeypatch: MonkeyPatch):
    with patch.object(SessionsResource, 'process_id_info') as mock_process_id_info:
        mock_process_id_info.return_value = user, auth_provider
        monkeypatch.setattr('google.oauth2.id_token.verify_oauth2_token', lambda *_: id_info_data)
        resp: testing.Result = client.simulate_post(session_path)
        assert mock_process_id_info.called
        assert resp.status == HTTP_OK
        assert resp.headers.get('Authorization', user.auth_token) is not None


def test_on_post_using_invalid_id_token(client: testing.TestClient, session_path: str, monkeypatch: MonkeyPatch):
    def raise_value_error(*_):
        raise ValueError('Test Value Error')

    monkeypatch.setattr('google.oauth2.id_token.verify_oauth2_token', raise_value_error)
    resp: testing.Result = client.simulate_post(session_path)
    assert resp.status == HTTP_UNAUTHORIZED


def test_on_post_when_auth_provider_missing_exception_is_raised(client: testing.TestClient,
                                                                session_path: str,
                                                                id_info_data: Dict,
                                                                monkeypatch: MonkeyPatch):
    with patch.object(SessionsResource, 'process_id_info') as mock_process_id_info:
        mock_process_id_info.side_effect = AuthProviderMissingUserException('mock-uuid')
        monkeypatch.setattr('google.oauth2.id_token.verify_oauth2_token', lambda *_: id_info_data)
        resp: testing.Result = client.simulate_post(session_path)
        assert mock_process_id_info.called
        assert resp.status == HTTP_INTERNAL_SERVER_ERROR


def test_on_post_when_an_unhandled_exception_is_raised(client: testing.TestClient,
                                                       session_path: str,
                                                       id_info_data: Dict,
                                                       monkeypatch: MonkeyPatch):
    with patch.object(SessionsResource, 'process_id_info') as mock_process_id_info:
        mock_process_id_info.side_effect = Exception('This was unexpected.')
        monkeypatch.setattr('google.oauth2.id_token.verify_oauth2_token', lambda *_: id_info_data)
        with pytest.raises(Exception):
            client.simulate_post(session_path)
        assert mock_process_id_info.called


def test_process_id_info_when_auth_token_is_expired(sessions_resource: SessionsResource,
                                                    id_info: IdInfo,
                                                    mock_users: MagicMock,
                                                    mock_auth_providers: MagicMock,
                                                    mock_user_service: MagicMock,
                                                    auth_provider_data: Dict,
                                                    user_data: Dict):
    with patch.object(mock_user_service, 'update_auth_token') as mock_update_auth_token:
        user_data['authTokenExpiry'] = datetime.datetime.now() - datetime.timedelta(hours=1)
        mock_auth_providers.find_one.return_value = auth_provider_data
        mock_users.find_one.return_value = user_data
        sessions_resource.process_id_info(id_info)
        assert mock_update_auth_token.called


def test_process_id_info_when_auth_token_is_valid(sessions_resource: SessionsResource,
                                                  id_info: IdInfo,
                                                  mock_users: MagicMock,
                                                  mock_auth_providers: MagicMock,
                                                  mock_user_service: MagicMock,
                                                  auth_provider_data: Dict,
                                                  user_data: Dict):
    with patch.object(mock_user_service, 'update_auth_token') as mock_update_auth_token:
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
