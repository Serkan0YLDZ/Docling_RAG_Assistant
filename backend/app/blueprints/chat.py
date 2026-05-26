from flask import Blueprint, current_app, jsonify, request

from app.domain.errors import ValidationError

chat_bp = Blueprint("chat", __name__)


def _rag():
    return current_app.extensions["rag_engine"]


def _session():
    return current_app.extensions["chat_session"]


@chat_bp.get("/api/chat/messages")
def list_messages():
    """Sohbet geçmişi."""
    return jsonify(_session().list_messages())


@chat_bp.post("/api/chat/reset")
def reset_chat():
    """Sohbet ve son kaynak önizlemesini sıfırlar."""
    _session().clear()
    return "", 204


@chat_bp.post("/api/chat/query")
def query():
    """RAG: retrieval + sohbet geçmişi + LLM."""
    body = request.get_json(silent=True) or {}
    message = body.get("message", "")
    document_ids = body.get("documentIds")
    if document_ids is not None and not isinstance(document_ids, list):
        raise ValidationError("documentIds bir dizi olmalıdır", status_code=400)

    session = _session()
    cfg = current_app.extensions.get("config")
    max_turns = cfg.RAG_MAX_HISTORY_TURNS if cfg else 10
    history = session.history_for_prompt(max_turns=max_turns)
    result = _rag().generate(message, document_ids, history)
    session.record_exchange(message.strip(), result)
    return jsonify(result)
