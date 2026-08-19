
from flask import Blueprint, jsonify
from ticket_api.health_store import ping

health_bp = Blueprint("health", __name__)


@health_bp.get("")      # empty string means this endpoint will default to the given url_prefix defined in app.py
def health():
    if ping():
        return jsonify(status="ok")
    return jsonify(status="down"), 500