import datetime
from typing import Tuple

from pymongo.collection import Collection

from j_notes_api.models import IdInfo, User, AuthProvider
from j_notes_api.services import crypto


class UserService:

    def __init__(self, users: Collection, auth_providers: Collection):
        self._users: Collection = users
        self._auth_providers: Collection = auth_providers

    def create_new_user(self, id_info: IdInfo, info_source: str = 'google') -> Tuple[User, AuthProvider]:
        """Creates a new user given a IdInfo model from a valid id token."""
        now = datetime.datetime.now()

        user_data = {
            'authToken': crypto.generate_token(),
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
        auth_token = crypto.generate_token()
        expiry = now + datetime.timedelta(hours=1)

        self._users.update_one(filter={'_id': user.uuid},
                               update={'authToken': auth_token, 'authTokenExpiry': expiry})

        user.auth_token = auth_token
        user.auth_token_expiry = expiry
