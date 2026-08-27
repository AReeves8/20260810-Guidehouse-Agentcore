""" Envelopes to wrap around our normal responses and convert Tickets into JSON """

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


def list_envelope(items: list):
    return jsonify(count=len(items), **{"items": items})

def single_envelope(payload: dict):
    return jsonify(**payload)


def error_response(code: str, status: int, detail: str | None = None):
    return jsonify(error=code, detail=detail), status