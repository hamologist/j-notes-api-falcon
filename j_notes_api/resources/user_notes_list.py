from datetime import datetime
import json

import falcon
from bson import json_util
from bson.objectid import ObjectId
from pymongo.collection import Collection
from pymongo.errors import WriteError

from j_notes_api.models import User


class UserNotesListResource:

    def __init__(self, notes: Collection):
        self._notes: Collection = notes

    def on_get(self, req: falcon.Request, resp: falcon.Response, user_id: str):
        user: User = req.user
        if user_id != str(user.uuid):
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.body = 'Attempting to access another user\'s data'
            return

        user_notes = self._notes.find({'user': ObjectId(user_id)})
        if user_notes.count():
            resp.body = json_util.dumps(user_notes)

    def on_post(self, req: falcon.Request, resp: falcon.Response, user_id: str):
        user: User = req.user
        if user_id != str(user.uuid):
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.body = 'Attempting to create a note as another user'
            return

        try:
            payload = json_util.loads(req.bounded_stream.read())
            now = datetime.now()
            data = {
                'user': ObjectId(user_id),
                'text': payload.get('text', ''),
                'dateCreated': now,
                'dateModified': now,
            }
        except json.JSONDecodeError:
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.body = 'Invalid payload provided'
            return

        try:
            result = self._notes.insert_one(data)
        except WriteError:
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.body = 'The provided payload failed to pass validation'
            return

        resp.body = str(result.inserted_id)
