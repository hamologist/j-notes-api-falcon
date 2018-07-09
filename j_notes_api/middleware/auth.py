import datetime
from typing import Dict, Tuple, Union

import falcon
from pymongo.collection import Collection

from j_notes_api.models import User
from j_notes_api.models.mongo_model import EmptyMongoModelException
from j_notes_api.services import crypto


class AuthMiddleware:

    def __init__(self, client_id: str, users: Collection, disabled_resources: Tuple[type] = None):
        self._client_id:          str = client_id
        self._users:              Collection = users
        self._disabled_resources: Union[Tuple[type], Tuple] = () if disabled_resources is None else disabled_resources

    def process_resource(self, req: falcon.Request, _resp: falcon.Response, resource: object, _params: Dict):
        if isinstance(resource, self._disabled_resources):
            return

        token = req.get_header('Authorization')

        if token is None:
            raise falcon.HTTPUnauthorized(title='Auth token required',
                                          description='Please provide an auth token as part of the request.')

        valid, user = self._validate_token_and_find_user(token)
        if not valid:
            raise falcon.HTTPUnauthorized(title='Authentication required',
                                          description='The provided auth token is not valid. Please request a new '
                                                      'token and try again.')

        req.user = user

    def _validate_token_and_find_user(self, token: str) -> Tuple[bool, Union[User, None]]:
        payload = crypto.decode_jwt(token, self._client_id)
        user_id = payload.get('sub')
        user_token = payload.get('token')
        user = None
        valid = False

        try:
            user = User(self._users.find_one({'_id': user_id, 'authToken': user_token}))
            if user.auth_token_expiry > datetime.datetime.now():
                valid = True
        except EmptyMongoModelException:
            pass

        return valid, user
