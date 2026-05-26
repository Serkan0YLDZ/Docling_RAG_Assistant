from flask import Blueprint, current_app, jsonify

sources_bp = Blueprint("sources", __name__)


@sources_bp.get("/api/sources")
def list_sources():
    """Son aramadan dönen kaynak kartları."""
    session = current_app.extensions["chat_session"]
    return jsonify(session.last_sources())
