import pytest


@pytest.mark.tc_chat
def test_tc_chat_01_reset_clears_messages_and_sources(client):
    client.post(
        "/api/chat/query",
        json={"message": "Bu bir test sorusudur mu?" * 2},
    )
    messages_before = client.get("/api/chat/messages").get_json()
    assert len(messages_before) >= 2

    reset = client.post("/api/chat/reset")
    assert reset.status_code == 204

    assert client.get("/api/chat/messages").get_json() == []
    assert client.get("/api/sources").get_json() == []


def test_chat_reset_then_query_starts_fresh(client):
    client.post("/api/chat/reset")
    client.post(
        "/api/chat/query",
        json={"message": "İlk soru sıfırlama sonrası nedir?"},
    )
    messages = client.get("/api/chat/messages").get_json()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert "sıfırlama" in messages[0]["content"].lower() or len(messages[0]["content"]) >= 10
