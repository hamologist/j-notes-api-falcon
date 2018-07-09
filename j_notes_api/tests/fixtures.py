import pytest


@pytest.fixture(name='client_id')
def mock_client_id_fixture() -> str:
    return 'mock-client-id'
