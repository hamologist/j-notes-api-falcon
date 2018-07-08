import os
from typing import Tuple, Type, Dict

import falcon
from pymongo.collection import Collection

from j_notes_api import resources
from j_notes_api.db import NOTES_DB

RESOURCE_MAP: Dict[Type[object], str] = {
    resources.NotesResource: '/notes',
    resources.SessionsResource: '/sessions',
    resources.UsersResource: '/users'
}

__CLIENT_ID:                 str = os.getenv('CLIENT_ID')
__AUTH_PROVIDERS_COLLECTION: Collection = NOTES_DB.authProviders
__NOTES_COLLECTION:          Collection = NOTES_DB.notes
__USERS_COLLECTION:          Collection = NOTES_DB.users


def create_notes_route() -> Tuple[str, resources.NotesResource]:
    return (RESOURCE_MAP[resources.NotesResource],
            resources.NotesResource(__NOTES_COLLECTION))


def create_sessions_route() -> Tuple[str, resources.SessionsResource]:
    return (RESOURCE_MAP[resources.SessionsResource],
            resources.SessionsResource(__CLIENT_ID, __AUTH_PROVIDERS_COLLECTION, __USERS_COLLECTION))


def create_users_route() -> Tuple[str, resources.UsersResource]:
    return (RESOURCE_MAP[resources.UsersResource],
            resources.UsersResource())


@property
def app() -> falcon.API:
    if not __CLIENT_ID:
        raise ValueError('The "CLIENT_ID" environment variable must be defined to start this API.')

    api = falcon.API()
    api.add_route(*create_notes_route())
    api.add_route(*create_sessions_route())
    api.add_route(*create_users_route())

    return api
