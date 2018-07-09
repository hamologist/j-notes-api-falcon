import datetime
import logging
from typing import Tuple

import falcon
from google.oauth2 import id_token
from google.auth.transport import requests
from pymongo.collection import Collection

from j_notes_api.models import AuthProvider, IdInfo, User
from j_notes_api.models.mongo_model import EmptyMongoModelException
from j_notes_api.services import crypto, UserService


class SessionsResource:

    def __init__(self, client_id: str, auth_providers: Collection, users: Collection, user_service: UserService):
        self._client_id:     str = client_id
        self._auth_providers: Collection = auth_providers
        self._users:          Collection = users
        self._user_service:   UserService = user_service
        self._logger:         logging.Logger = logging.getLogger(__name__)

    def on_post(self, req: falcon.Request, resp: falcon.Response):
        auth_data = req.get_header('Authorization')
        try:
            id_info = IdInfo(id_token.verify_oauth2_token(auth_data, requests.Request(), self._client_id))
            user, _ = self.process_id_info(id_info)
            resp.append_header('Authorization', crypto.generate_jwt(user, self._client_id))
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
            user, auth_provider = self._user_service.create_new_user(id_info, info_source)

        if not user:
            try:
                user = User(self._users.find_one({'_id': auth_provider.user}))
            except EmptyMongoModelException:
                raise AuthProviderMissingUserException(str(auth_provider.uuid))

        if user.auth_token_expiry <= datetime.datetime.now():
            self._user_service.update_auth_token(user)

        return user, auth_provider


class AuthProviderMissingUserException(Exception):

    def __init__(self, auth_provider_uuid: str):
        super().__init__()
        self.message = ('Failed to find a user for the provided auth provider '
                        '(Auth provider id: "{}").'.format(auth_provider_uuid))
