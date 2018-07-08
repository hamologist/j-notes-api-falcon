import datetime
from typing import Dict

import pytest
from bson import ObjectId

from j_notes_api import models


@pytest.fixture(name='auth_provider_data')
def auth_provider_data_fixture() -> Dict:
    return {
        '_id': ObjectId(),
        'type': 'mock-type',
        'userIdentifier': 'mock-user-identifier',
        'user': ObjectId(),
        'dateCreated': datetime.datetime.now()
    }


@pytest.fixture(name='auth_provider')
def auth_provider_fixture(auth_provider_data: Dict) -> models.AuthProvider:
    return models.AuthProvider(auth_provider_data)


@pytest.fixture(name='id_info_data')
def id_info_data_fixture() -> Dict:
    return {
        '_id': ObjectId(),
        'iss': 'mock-iss',
        'sub': 'mock-sub',
        'aud': 'mock-aud',
        'iat': 'mock-iat',
        'exp': 'mock-exp'
    }


@pytest.fixture(name='id_info')
def id_info_fixture(id_info_data: Dict) -> models.IdInfo:
    return models.IdInfo(id_info_data)


@pytest.fixture(name='user_data')
def user_data_fixture() -> Dict:
    now = datetime.datetime.now()
    return {
        '_id': ObjectId(),
        'authToken': 'mock-auth-token',
        'authTokenExpiry': now + datetime.timedelta(hours=1),
        'dateCreated': now
    }


@pytest.fixture(name='user')
def user_fixture(user_data: Dict) -> models.User:
    return models.User(user_data)
