import hashlib
import os
from typing import Mapping

import jwt

from j_notes_api.models import User


def generate_token():
    crypto = hashlib.sha256()
    crypto.update(os.urandom(1024))

    return crypto.hexdigest()


def generate_jwt(user: User, secret: str):
    return jwt.encode({
        'sub': str(user.uuid),
        'token': user.auth_token
    }, secret, algorithm='HS256')


def decode_jwt(payload: str, secret: str) -> Mapping:
    return jwt.decode(payload, secret, algorithms=['HS256'])
