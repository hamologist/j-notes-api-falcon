import os
from typing import Dict

import falcon
from pymongo.collection import Collection

from j_notes_api import resources
from j_notes_api.db import NOTES_DB
from j_notes_api.middleware.auth import AuthMiddleware
from j_notes_api.services import UserService

RESOURCE_MAP: Dict[type, str] = {
    resources.SessionsResource: '/sessions',
    resources.UserNotesResource: '/users/{user_id}/notes/{note_id}',
    resources.UserNotesListResource: '/users/{user_id}/notes',
}

__CLIENT_ID:                 str = os.getenv('CLIENT_ID')
__AUTH_PROVIDERS_COLLECTION: Collection = NOTES_DB.authProviders
__NOTES_COLLECTION:          Collection = NOTES_DB.notes
__USERS_COLLECTION:          Collection = NOTES_DB.users


def create_app() -> falcon.API:
    if not __CLIENT_ID:
        raise ValueError('The "CLIENT_ID" environment variable must be defined to start this API.')

    auth_middleware = AuthMiddleware(__CLIENT_ID, __USERS_COLLECTION, (resources.SessionsResource,))
    user_service = UserService(__USERS_COLLECTION, __AUTH_PROVIDERS_COLLECTION)
    sessions_resource = resources.SessionsResource(
        __CLIENT_ID, __AUTH_PROVIDERS_COLLECTION, __USERS_COLLECTION, user_service)
    user_notes_resource = resources.UserNotesResource(__NOTES_COLLECTION)
    user_notes_list_resource = resources.UserNotesListResource(__NOTES_COLLECTION)

    api = falcon.API(middleware=auth_middleware)
    api.add_route(RESOURCE_MAP[resources.SessionsResource], sessions_resource)
    api.add_route(RESOURCE_MAP[resources.UserNotesResource], user_notes_resource)
    api.add_route(RESOURCE_MAP[resources.UserNotesListResource], user_notes_list_resource)

    return api
