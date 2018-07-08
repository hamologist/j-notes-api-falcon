import datetime
import logging
import os
import hashlib
from typing import Tuple

import falcon

from google.oauth2 import id_token
from google.auth.transport import requests
from pymongo.collection import Collection

from j_notes_api.models import AuthProvider, IdInfo, User
from j_notes_api.models.mongo_model import EmptyMongoModelException


class SessionsResource:

    def __init__(self, client_id: str, auth_providers: Collection, users: Collection):
        self._client_id:     str = client_id
        self._auth_providers: Collection = auth_providers
        self._users:          Collection = users
        self._logger:         logging.Logger = logging.getLogger(__name__)

    def on_post(self, req: falcon.Request, resp: falcon.Response):
        data = req.bounded_stream.read().strip(b'\n')
        try:
            id_info = IdInfo(id_token.verify_oauth2_token(data, requests.Request(), self._client_id))
            user, _ = self.process_id_info(id_info)
            resp.data = str.encode(user.auth_token)
        except ValueError as error:
            self._logger.debug('Failed to validate an id token: %s', error)
            resp.status = falcon.HTTP_UNAUTHORIZED
        except AuthProviderMissingUserException as error:
            self._logger.debug(error.message)
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
        except Exception as error:
            self._logger.debug('Something went wrong while processing the session post request: %s', error)
            resp.status = falcon.HTTP_INTERNAL_SERVER_ERROR
            raise error

    def process_id_info(self, id_info: IdInfo, info_source: str = 'google') -> Tuple[User, AuthProvider]:
        """Processes the id info extracted from a valid id token.

            Note: This API oly supports "Google Sign-In" for the time being.
        """
        user = None
        try:
            auth_provider = AuthProvider(
                self._auth_providers.find_one({'type': info_source, 'userIdentifier': id_info.sub}))
        except EmptyMongoModelException:
            user, auth_provider = self.create_new_user(id_info, info_source)

        if not user:
            try:
                user = User(self._users.find_one({'_id': auth_provider.user}))
            except EmptyMongoModelException:
                raise AuthProviderMissingUserException(auth_provider.uuid)

        if user.auth_token_expiry <= datetime.datetime.now():
            self.update_auth_token(user)

        return user, auth_provider

    def create_new_user(self, id_info: IdInfo, info_source: str = 'google') -> Tuple[User, AuthProvider]:
        """Creates a new user given a IdInfo model from a valid id token."""
        now = datetime.datetime.now()

        user_data = {
            'authToken': self.generate_token(),
            'authTokenExpiry': now + datetime.timedelta(hours=1),
            'dateCreated': now
        }
        user_id = self._users.insert_one(user_data).inserted_id

        auth_provider_data = {
            'type': info_source,
            'userIdentifier': id_info.sub,
            'user': user_id,
            'dateCreated': now
        }
        auth_provider_id = self._auth_providers.insert_one(auth_provider_data).inserted_id

        return User({'_id': user_id, **user_data}), AuthProvider({'_id': auth_provider_id, **auth_provider_data})

    def update_auth_token(self, user: User):
        now = datetime.datetime.now()
        auth_token = self.generate_token()
        expiry = now + datetime.timedelta(hours=1)

        self._users.update_one(filter={'_id': user.uuid},
                               update={'authToken': auth_token, 'authTokenExpiry': expiry})

        user.auth_token = auth_token
        user.auth_token_expiry = expiry

    @staticmethod
    def generate_token():
        crypto = hashlib.sha256()
        crypto.update(os.urandom(1024))

        return crypto.hexdigest()


class AuthProviderMissingUserException(Exception):

    def __init__(self, auth_provider_uuid: str):
        super().__init__()
        self.message = ('Failed to find a user for the provided auth provider '
                        '(Auth provider id: "{}").'.format(auth_provider_uuid))
