from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/api/health")
def health():
    """Servis ayakta mı kontrolü."""
    return jsonify({"status": "ok"})
