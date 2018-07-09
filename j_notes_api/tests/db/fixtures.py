from typing import Dict
from unittest.mock import MagicMock

import pytest
from bson import ObjectId


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
