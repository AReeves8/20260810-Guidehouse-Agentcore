"""Pydantic models for the HTTP boundary.

Separate from the SQLAlchemy models in data/models.py on purpose, and the
distinction is worth stating: a database model describes what is STORED; a
schema describes what a client may SEND. Letting one class do both is how a
client ends up able to set an `id`, a `created_at`, or a `deploy_target` --
fields the server owns.

Note what NoteCreate does not contain: id, host, deploy_target, created_at.
All four are server-assigned, so none of them is accepted from a caller.
"""

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    """The only shape a client is allowed to POST."""

    # extra="forbid" rejects fields this model does not declare, so a typo
    # like {"bdy": "..."} produces an explicit error naming the offending
    # field rather than being silently dropped.
    model_config = ConfigDict(extra="forbid")

    body: str = Field(min_length=1, max_length=500)
