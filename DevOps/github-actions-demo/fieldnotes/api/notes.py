"""The /notes resource. HTTP in, HTTP out, nothing else.

LAYER RULE: this file may import Flask and the service layer. It may NOT
import the repository or the ORM models. If a database query ever appears
here, the layering has stopped being real -- and the test for that is
mechanical: grep this directory for "db.session" and expect nothing.

Each handler is three lines because that is all an HTTP boundary should be:
parse the request, delegate, format the reply.
"""

from flask import Blueprint, jsonify, request

from fieldnotes.api.schemas import NoteCreate
from fieldnotes.services import notes as notes_service

notes_bp = Blueprint("notes", __name__)


@notes_bp.post("/notes")
def create_note():
    # silent=True so malformed JSON and missing fields both reach the same
    # Pydantic error path, producing one error shape instead of two depending
    # on how the client got it wrong.
    data = NoteCreate.model_validate(request.get_json(silent=True) or {})
    return jsonify(notes_service.record_note(data.body)), 201


@notes_bp.get("/notes")
def list_notes():
    items = notes_service.recent_notes()
    return jsonify(count=len(items), items=items)
