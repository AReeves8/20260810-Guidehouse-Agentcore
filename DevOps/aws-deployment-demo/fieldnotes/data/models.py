"""SQLAlchemy models -- the data layer's definition of what a row is.

LAYER RULE: this module knows about SQLAlchemy and nothing else. No Flask, no
request object, no HTTP status codes. That is what makes it usable from a CLI
task, a background worker, or a test with no application context -- and it is
the reason `to_dict()` does NOT live here. Serialising for an HTTP response is
the API layer's job; a model that knows how it will be rendered has taken on a
second responsibility it cannot be reused without.
"""

from datetime import datetime, timezone

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from fieldnotes.extensions import db


class Note(db.Model):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    # Written at insert time from the running process's configuration. By the
    # end of the session there is one row per deployment target in the same
    # database -- the proof that every target is the same application talking
    # to the same data.
    deploy_target: Mapped[str] = mapped_column(String(40), nullable=False)

    # The specific machine or container that served the request: an ECS task
    # id, an EC2 hostname. Makes a scaled service visibly more than one
    # process.
    host: Mapped[str] = mapped_column(String(120), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
