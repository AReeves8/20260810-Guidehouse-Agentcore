"""One error shape for the whole API, registered in one place.

Every failure -- validation, not found, an unexpected exception -- leaves as
the same JSON object. That consistency is the "uniform interface" REST idea
applied to failures, and it is what lets a client write one error handler
instead of one per endpoint.

Registering handlers centrally rather than wrapping each route in try/except
also means a route added next month gets correct error behaviour without its
author having to remember anything.
"""

from flask import jsonify
from pydantic import ValidationError


class ApiError(Exception):
    """Raised by any layer that wants to produce a specific HTTP failure."""

    def __init__(self, code: str, status: int, detail: str | None = None):
        super().__init__(detail or code)
        self.code = code
        self.status = status
        self.detail = detail


def error_response(code: str, status: int, detail: str | None = None):
    return jsonify(error=code, detail=detail), status


def register_error_handlers(app) -> None:
    @app.errorhandler(ApiError)
    def _api_error(exc: ApiError):
        return error_response(exc.code, exc.status, exc.detail)

    @app.errorhandler(ValidationError)
    def _validation_error(exc: ValidationError):
        # Report every failure, not only the first. With extra="forbid" a
        # single typo produces two errors -- "body: Field required" and
        # "bdy: Extra inputs are not permitted" -- and only the second names
        # the actual mistake.
        details = [
            f"{'.'.join(str(p) for p in e['loc']) or 'body'}: {e['msg']}"
            for e in exc.errors()
        ]
        return error_response("validation_failed", 422, "; ".join(details))

    @app.errorhandler(404)
    def _not_found(_exc):
        return error_response("not_found", 404, "no route for this path")

    @app.errorhandler(Exception)
    def _unexpected(exc: Exception):
        # Logged in full, reported vaguely. The stack trace goes to
        # CloudWatch; the client gets a code it can branch on and nothing
        # that describes our internals.
        app.logger.exception("unhandled error")
        return error_response("internal", 500, "an unexpected error occurred")
