"""Operational endpoints -- health, readiness, and identity.

Separated from the notes blueprint because they answer to a different
audience. /notes serves users; these serve load balancers, container
orchestrators, and whoever is awake at 3am. Grouping them makes it obvious
which endpoints must keep working when the application's actual feature is
broken.
"""

from flask import Blueprint, jsonify

from fieldnotes.services import notes as notes_service

ops_bp = Blueprint("ops", __name__)


@ops_bp.get("/health")
def health():
    """Liveness: is this process alive and able to answer HTTP?

    Touches nothing external, deliberately. A liveness probe that checks the
    database reports a healthy process as dead during a brief database blip,
    and the orchestrator responds by killing and restarting it -- turning a
    short outage into a restart loop that makes recovery slower.
    """
    return jsonify(status="ok", **notes_service.runtime_identity())


@ops_bp.get("/ready")
def ready():
    """Readiness: can this process serve a real request right now?

    This one does check the database, because a process that cannot reach it
    should be pulled from the load balancer -- but NOT restarted. That
    difference is the entire reason there are two endpoints.
    """
    if not notes_service.database_is_reachable():
        return jsonify(status="unavailable", reason="database unreachable"), 503
    return jsonify(status="ready", **notes_service.runtime_identity())


@ops_bp.get("/whoami")
def whoami():
    """Where is this code running? The most-used endpoint of the session."""
    return jsonify(**notes_service.runtime_identity())
