""" Envelopes to wrap around our normal responses and convert Tickets into JSON """

from ticket_api.models import Ticket
from flask import jsonify


class ApiError(Exception):
    """ Custom exception that can work with Flask's errorhandler() """

    def __init__(self, code: str, status: int, detail: str | None = None):

        # Flask expects specific values for "code"
        #   ex: "not_found" "internal" "validation_failed"

        super().__init__(detail or code)
        self.code = code
        self.status = status
        self.detail = detail


def list_envelope(tickets: list[Ticket]):
    # creates a JSON object with two properties: a count of the number of items and list of the actual items
    # could instead just do jsonify([t.model_dump(mode="json") for t in tickets]) if you only want a list returned
    return jsonify(count=len(tickets), items=[t.model_dump(mode="json") for t in tickets])

def single_envelope(ticket: Ticket):
    return jsonify(ticket.model_dump(mode="json"))


def error_response(code: str, status: int, detail: str | None = None):
    return jsonify(error=code, detail=detail), status