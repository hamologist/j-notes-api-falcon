from bson.json_util import dumps

import falcon

from j_notes_api.db import NOTES_COLLECTION


class NotesResource:

    @staticmethod
    def on_get(_: falcon.Request, resp: falcon.Response):
        notes = NOTES_COLLECTION.find({})
        resp.body = dumps(notes)
