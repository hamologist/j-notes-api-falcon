from j_notes_api.db import NOTES_DB


def create_database():
    NOTES_DB.create_collection('notes', validator={
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['user', 'dateCreated', 'dateModified'],
            'properties': {
                'user': {
                    'bsonType': 'objectId',
                    'description': 'The _id value of the user who owns this note.'
                },
                'text': {
                    'bsonType': 'string',
                    'maxLength': 5000,
                    'description': 'The contents of the note.'
                },
                'dateCreated': {
                    'bsonType': 'date',
                    'description': 'The date the note was created.'
                },
                'dateModified': {
                    'bsonType': 'date',
                    'description': 'The date the note was last modified.'
                }
            }
        }
    })

    NOTES_DB.create_collection('users', validator={
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['sub', 'dateCreated'],
            'properties': {
                'sub': {
                    'bsonType': 'string',
                    'description': 'The subject value provided by Google.'
                },
                'dateCreated': {
                    'bsonType': 'date',
                    'description': 'The date the user was created.'
                }
            }
        }
    })


if __name__ == '__main__':
    create_database()
