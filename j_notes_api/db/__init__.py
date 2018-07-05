from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

import os


MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', '27017'))
MONGO_CLIENT = MongoClient(MONGO_HOST, MONGO_PORT)
NOTES_DB: Database = MONGO_CLIENT.jNotesDB
NOTES_COLLECTION: Collection = NOTES_DB.notes
USERS_COLLECTION: Collection = NOTES_DB.users
