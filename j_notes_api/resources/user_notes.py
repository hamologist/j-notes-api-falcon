import json
from datetime import datetime

import falcon
from bson import ObjectId, json_util
from pymongo.collection import Collection
from pymongo.errors import WriteError

from j_notes_api.models import User


class UserNotesResource:

    def __init__(self, notes: Collection):
        self._notes: Collection = notes

    def on_get(self, req: falcon.Request, resp: falcon.Response, user_id: str, note_id: str):
        user: User = req.user
        if user_id != str(user.uuid):
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.body = 'Attempting to access another user\'s data'
            return

        user_notes = self._notes.find({'_id': ObjectId(note_id)})
        resp.body = json_util.dumps(user_notes)

    def on_put(self, req: falcon.Request, resp: falcon.Response, user_id: str, note_id: str):
        user: User = req.user
        if user_id != str(user.uuid):
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.body = 'Attempting to update another user\'s data'
            return

        try:
            payload = json_util.loads(req.bounded_stream.read())
            note_filter = {
                '_id': ObjectId(note_id),
                'user': ObjectId(user_id)
            }
            data = {
                '$set': {
                    'text': payload.get('text', ''),
                    'dateModified': datetime.now()
                }
            }
        except json.JSONDecodeError:
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.body = 'Invalid payload provided'
            return

        try:
            self._notes.update_one(note_filter, data)
        except WriteError:
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.body = 'The provided payload failed to pass validation'
            return
