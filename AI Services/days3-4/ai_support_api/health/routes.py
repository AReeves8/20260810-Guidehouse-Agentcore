from flask import Blueprint, jsonify

from ai_support_api.health import service
from ai_support_api.responses import error_response


health_bp = Blueprint("health", __name__)


@health_bp.get("")
def health():
    try:
        identity = service.whoami()
    except Exception:
        return error_response("unhealthy", 503, "Cannot Authenticate to AWS.")

    return jsonify(staus="ok", aws=identity)
