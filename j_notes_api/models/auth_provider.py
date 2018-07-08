from datetime import datetime
from typing import Dict, Union

from bson import ObjectId

from j_notes_api.models.mongo_model import MongoModel


class AuthProvider(MongoModel):

    def __init__(self, client_data: Union[Dict, None], uuid: ObjectId = None):
        super().__init__(client_data, uuid)
        self.type:            str = client_data.get('type')
        self.user_identifier: str = client_data.get('userIdentifier')
        self.user:            str = client_data.get('user')
        self.date_created:    datetime = client_data.get('dateCreated')
