from datetime import datetime
from typing import Dict, Union

from bson import ObjectId

from j_notes_api.models.mongo_model import MongoModel


class User(MongoModel):

    def __init__(self, user_data: Union[Dict, None], uuid: ObjectId = None):
        super().__init__(user_data, uuid)
        self.auth_token:        str = user_data.get('authToken')
        self.auth_token_expiry: datetime = user_data.get('authTokenExpiry')
        self.date_created:      datetime = user_data.get('dateCreated')
