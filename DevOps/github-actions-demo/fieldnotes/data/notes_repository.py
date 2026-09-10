"""Every query against the notes table lives here. Nowhere else.

WHY A REPOSITORY AT ALL, when SQLAlchemy's session is already an abstraction
over the database? Two reasons that hold even for an app this small:

* **One place to look.** "How do we read notes?" has exactly one answer. When
  a query needs an index, a filter, or pagination, there is a single file to
  change and a single file to review -- rather than a query pattern scattered
  across however many route handlers happened to need it.
* **The service layer stops depending on the ORM.** Services call
  `list_recent()`, not `Note.query.order_by(...)`. Swapping SQLAlchemy for
  something else, or putting a cache in front of reads, becomes a change to
  this file instead of a change everywhere.

The honest counterpoint, worth saying out loud: for a five-endpoint
application this is more structure than the problem strictly requires. It is
here because the *shape* is what transfers -- and because a codebase that
grows into needing layers rarely gets refactored into them afterwards.

LAYER RULE: knows about SQLAlchemy. Does not know about Flask, HTTP, or the
service layer above it.
"""

from fieldnotes.data.models import Note
from fieldnotes.extensions import db


def add(body: str, deploy_target: str, host: str) -> Note:
    """Insert one note and return it, populated with its database-assigned id.

    The commit lives here rather than in the caller because this is the only
    layer that knows a transaction exists. A service that had to remember to
    commit would eventually forget -- and the bug would be silent, since
    everything looks correct until the request ends and the write vanishes.
    """
    note = Note(body=body, deploy_target=deploy_target, host=host)
    db.session.add(note)
    db.session.commit()
    return note


def list_recent(limit: int = 50) -> list[Note]:
    """Most recent notes first.

    `limit` has a default and is a parameter rather than a constant, because
    an unbounded SELECT against a table that grows forever is a production
    incident waiting for enough rows.
    """
    return (
        db.session.query(Note)
        .order_by(Note.id.desc())
        .limit(limit)
        .all()
    )


def ping() -> None:
    """Cheapest possible round trip to the database.

    Raises if the database is unreachable; returns None otherwise. Deliberately
    returns nothing -- callers should care whether it raised, not what it
    selected. Used by the readiness check.
    """
    from sqlalchemy import text

    db.session.execute(text("SELECT 1"))
