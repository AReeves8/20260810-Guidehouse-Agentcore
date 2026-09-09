"""Application factory -- the composition root.

This is the only file that knows about every layer at once, and that is its
job: wiring is a responsibility, and giving it one home keeps it out of the
layers themselves. Nothing here contains business logic; it connects things
that do.

Read the import list as a dependency diagram. `app.py` sees config, the
extensions, the API blueprints, and the error handlers. It does not import the
service or repository modules directly -- those are reached through the API
layer, which is what "layered" means when it is real rather than aspirational.
"""

from flask import Flask

from fieldnotes.api.errors import register_error_handlers
from fieldnotes.api.notes import notes_bp
from fieldnotes.api.ops import ops_bp
from fieldnotes.config import DATABASE_URL
from fieldnotes.extensions import db, migrate


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL

    # Recycle connections before the database decides they are idle and drops
    # them. Without this, an app that sits quiet overnight serves its first
    # morning request over a dead socket and returns a 500 that vanishes on
    # retry -- a textbook "works on my machine" bug, because a local Postgres
    # never idles a connection out and a managed one does.
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    db.init_app(app)
    migrate.init_app(app, db)

    # Imported for its side effect only: Flask-Migrate can autogenerate a
    # migration only for models it has actually seen. Without this import the
    # models are never registered and `flask db migrate` writes an EMPTY
    # migration -- among the most confusing failures in this stack, because
    # nothing raises.
    from fieldnotes.data import models  # noqa: F401

    app.register_blueprint(ops_bp)
    app.register_blueprint(notes_bp)
    register_error_handlers(app)

    return app


# A module-level app for WSGI servers to import. gunicorn is pointed at
# `fieldnotes.app:app`; Elastic Beanstalk looks for a callable named
# `application`. Both names refer to one object rather than each platform
# needing its own entry-point file.
app = create_app()
application = app
