import datetime
from unittest.mock import MagicMock

import pytest

from j_notes_api.models import IdInfo, User, AuthProvider
from j_notes_api.services import UserService


@pytest.fixture(name='user_service')
def user_service_fixture(mock_users: MagicMock, mock_auth_providers: MagicMock) -> UserService:
    return UserService(mock_users, mock_auth_providers)


def test_create_new_user(user_service: UserService, id_info: IdInfo):
    user, auth_provider = user_service.create_new_user(id_info)

    assert isinstance(user, User)
    assert isinstance(auth_provider, AuthProvider)


def test_update_auth_token(user_service: UserService, user: User):
    old_auth_token = user.auth_token
    old_auth_token_expiry = user.auth_token_expiry
    user_service.update_auth_token(user)
    new_auth_token = user.auth_token
    new_auth_token_expiry = user.auth_token_expiry

    assert isinstance(new_auth_token, str)
    assert isinstance(new_auth_token_expiry, datetime.datetime)
    assert old_auth_token != new_auth_token
    assert old_auth_token_expiry < new_auth_token_expiry
