from app.services.chat_session_service import ChatSessionService


def test_history_for_prompt_excludes_pending_user_message():
    session = ChatSessionService()
    session.record_exchange(
        "ilk soru",
        {
            "message": {"id": "a1", "role": "assistant", "content": "ilk cevap"},
            "sources": [],
        },
    )
    session._messages.append(
        {"id": "u2", "role": "user", "content": "ikinci soru henüz işlenmedi"}
    )
    history = session.history_for_prompt(max_turns=5)
    assert len(history) == 2
    assert history[0]["content"] == "ilk soru"
    assert history[1]["content"] == "ilk cevap"


def test_clear_removes_messages_and_sources():
    session = ChatSessionService()
    session.record_exchange(
        "soru",
        {"message": {"id": "a", "role": "assistant", "content": "cevap"}, "sources": [{"x": 1}]},
    )
    session.clear()
    assert session.list_messages() == []
    assert session.last_sources() == []
