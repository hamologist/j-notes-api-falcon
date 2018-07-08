#  pylint: disable-msg=C0103
import pytest
from bson import ObjectId

from j_notes_api.models.mongo_model import EmptyMongoModelException, MongoModel


@pytest.fixture(name='mock_uuid')
def mock_uuid_fixture() -> ObjectId:
    return ObjectId()


@pytest.fixture(name='mock_uuid_override')
def mock_uuid_override_fixture() -> ObjectId:
    return ObjectId()


def test_mongo_model_with_data(mock_uuid: ObjectId):
    mongo_model = MongoModel({'_id': mock_uuid})

    assert mongo_model.uuid == mock_uuid


def test_mongo_model_with_data_and_uuid_override(mock_uuid: ObjectId, mock_uuid_override: ObjectId):
    mongo_model = MongoModel({'_id': mock_uuid}, mock_uuid_override)

    assert mongo_model.uuid == mock_uuid_override


def test_mongo_model_with_no_data():
    with pytest.raises(EmptyMongoModelException):
        MongoModel(None)
