import os

from pymongo import MongoClient
from pymongo.database import Database

MONGO_HOST:   str = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT:   int = int(os.getenv('MONGO_PORT', '27017'))
MONGO_CLIENT: MongoClient = MongoClient(MONGO_HOST, MONGO_PORT)
NOTES_DB:     Database = MONGO_CLIENT.jNotesDB
