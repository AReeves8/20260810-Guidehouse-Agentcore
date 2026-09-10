"""Business logic: what the application *does*, independent of how it is called.

LAYER RULE, and the one worth testing yourself on: **there is no Flask import
in this file, and there never should be.** No `request`, no `jsonify`, no
status codes. Everything this layer needs arrives as an argument and leaves as
a return value or an exception.

That constraint is not decoration. It means every function here can be called
from a route, a CLI command, a scheduled job, or a test with no application
context and no HTTP at all -- and it is what makes the service layer worth
having rather than a folder that forwards calls.

The rule downward is the mirror image: services call the repository, never the
ORM. If `Note.query` ever appears in this file, the data layer has leaked.
"""

import socket

from fieldnotes.config import DEPLOY_TARGET
from fieldnotes.data import notes_repository

# Resolved once at import, not per call. On ECS this is the task id; on EC2
# the instance hostname. It identifies the process and cannot change while
# that process is alive, so recomputing it per request would be work for a
# constant.
HOSTNAME = socket.gethostname()


def record_note(body: str) -> dict:
    """Record a note, stamped with where this process is running.

    The stamping happens here rather than in the route because it is a
    decision about *what a note is*, not about HTTP. A second caller -- a
    seeding script, a bulk importer -- gets the same behaviour for free
    instead of having to remember to set two fields.
    """
    note = notes_repository.add(
        body=body, deploy_target=DEPLOY_TARGET, host=HOSTNAME
    )
    return _as_dict(note)


def recent_notes(limit: int = 50) -> list[dict]:
    return [_as_dict(note) for note in notes_repository.list_recent(limit)]


def database_is_reachable() -> bool:
    """True if the database answered; False if it did not.

    Converts an exception into a boolean because the caller -- a readiness
    check -- has exactly two behaviours and does not care which exception
    occurred. The bare `except` is appropriate precisely here and almost
    nowhere else: a readiness probe must return a definitive answer rather
    than propagate a failure it cannot act on.
    """
    try:
        notes_repository.ping()
    except Exception:
        return False
    return True


def runtime_identity() -> dict:
    """Where this code is running. Used by /whoami and the health endpoints."""
    return {"deploy_target": DEPLOY_TARGET, "host": HOSTNAME}


def _as_dict(note) -> dict:
    """Convert an ORM object into a plain dictionary at the layer boundary.

    Services return dictionaries, not ORM instances. Handing a live `Note` up
    to the API layer would let a route trigger lazy loads and further queries
    long after the service thought it was finished -- coupling the HTTP layer
    to the session lifecycle in a way that only fails under load.
    """
    return {
        "id": note.id,
        "body": note.body,
        "deploy_target": note.deploy_target,
        "host": note.host,
        "created_at": note.created_at.isoformat(),
    }
