from uuid import uuid4


class ChatSessionService:
    """In-memory sohbet oturumu (MVP)."""

    def __init__(self) -> None:
        self._messages: list[dict] = []
        self._last_sources: list[dict] = []

    def list_messages(self) -> list[dict]:
        return list(self._messages)

    def last_sources(self) -> list[dict]:
        return list(self._last_sources)

    def record_exchange(self, user_text: str, response: dict) -> None:
        self._messages.append(
            {
                "id": f"msg-{uuid4()}",
                "role": "user",
                "content": user_text,
            }
        )
        self._messages.append(response["message"])
        self._last_sources = response.get("sources") or []

    def history_for_prompt(self, max_turns: int = 10) -> list[dict]:
        """Sıfırlanana kadar biriken user/assistant mesajları (son kullanıcı hariç)."""
        if max_turns < 1:
            return []
        msgs = list(self._messages)
        if msgs and msgs[-1].get("role") == "user":
            msgs = msgs[:-1]
        if not msgs:
            return []
        max_messages = max_turns * 2
        return msgs[-max_messages:]

    def clear(self) -> None:
        self._messages.clear()
        self._last_sources.clear()
