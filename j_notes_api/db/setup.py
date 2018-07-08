from j_notes_api.db import NOTES_DB


def create_database():
    NOTES_DB.create_collection('notes', validator={
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['user', 'dateCreated', 'dateModified'],
            'properties': {
                'user': {
                    'bsonType': 'objectId',
                    'description': 'The _id value of the user who owns this note.',
                },
                'text': {
                    'bsonType': 'string',
                    'maxLength': 5000,
                    'description': 'The contents of the note.',
                },
                'dateCreated': {
                    'bsonType': 'date',
                    'description': 'The date the note was created.',
                },
                'dateModified': {
                    'bsonType': 'date',
                    'description': 'The date the note was last modified.',
                }
            }
        }
    })

    NOTES_DB.create_collection('users', validator={
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['dateCreated'],
            'properties': {
                'authToken': {
                    'bsonType': 'string',
                    'description': 'Stores a secure hash used for API resource call validation.',
                    'maxLength': 64,
                },
                'authTokenExpiry': {
                    'bsonType': 'date',
                    'description': 'The time the token is set to expire. Token usage attempts past this date will be '
                                   'revoked'
                },
                'dateCreated': {
                    'bsonType': 'date',
                    'description': 'The date the user was created.',
                }
            }
        }
    })

    NOTES_DB.create_collection('authProvider', validator={
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['userIdentifier', 'user', 'dateCreated'],
            'properties': {
                'type': {
                    'bsonType': 'string',
                    'description': 'A key denoting the type of the auth provider (i.e. "google" for "Google Sign-In").',
                },
                'userIdentifier': {
                    'bsonType': 'objectId',
                    'description': 'A unique user identifier provided by the authentication provider.',
                },
                'user': {
                    'bsonType': 'string',
                    'description': 'The _id value of the user associated to this client.',
                },
                'dateCreated': {
                    'bsonType': 'date',
                    'description': 'The date the user was created.',
                }
            }
        }
    })


if __name__ == '__main__':
    create_database()
