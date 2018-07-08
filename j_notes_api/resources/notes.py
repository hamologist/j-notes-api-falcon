import falcon
from bson.json_util import dumps
from pymongo.collection import Collection


class NotesResource:

    def __init__(self, notes: Collection):
        self.notes: Collection = notes

    def on_get(self, _: falcon.Request, resp: falcon.Response):
        notes = self.notes.find({})
        resp.body = dumps(notes)
