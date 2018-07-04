import falcon

import j_notes_api.resources as resources


def _create_notes_resource() -> resources.NotesResource:
    return resources.NotesResource()


def _create_users_resource() -> resources.UsersResource:
    return resources.UsersResource()


def get_app() -> falcon.API:
    app = falcon.API()
    app.add_route('/notes', _create_notes_resource())
    app.add_route('/users', _create_users_resource())

    return app
