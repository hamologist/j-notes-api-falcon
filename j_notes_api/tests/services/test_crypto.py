import pytest

from j_notes_api.models import User
from j_notes_api.services import crypto


@pytest.fixture(name='secret')
def secret_fixture() -> str:
    return 'test-secret'


def test_jwt_encode_decode_pipeline(user: User, secret: str):
    payload = crypto.generate_jwt(user, secret)
    result = crypto.decode_jwt(payload, secret)

    assert isinstance(payload, bytes)
    assert isinstance(result, dict)
    assert result.get('sub') is not None
    assert result.get('token') is not None


def test_generate_token():
    token = crypto.generate_token()

    assert isinstance(token, str)
    assert len(token) == 64
