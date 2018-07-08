from datetime import datetime
from typing import Dict, Union

from bson import ObjectId

from j_notes_api.models.mongo_model import MongoModel


class Note(MongoModel):
    def __init__(self, note_data: Union[Dict, None], uuid: ObjectId = None):
        super().__init__(note_data, uuid)
        self.user: str = note_data.get('user')
        self.text: str = note_data.get('text')
        self.date_created: datetime = note_data.get('dateCreated')
        self.date_modified: datetime = note_data.get('dateModified')
