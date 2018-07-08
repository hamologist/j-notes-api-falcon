from typing import Dict, Union

from bson import ObjectId


class MongoModel:
    def __init__(self, data: Union[Dict, None], uuid: ObjectId = None):
        if not data:
            raise EmptyMongoModelException(
                '"None" was provided to the "{}" Mongo model'.format(self.__class__.__name__))
        self.uuid = uuid if uuid else data.get('_id')


class EmptyMongoModelException(Exception):
    pass
