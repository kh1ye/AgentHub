import json
import re
from copy import deepcopy
from threading import RLock
from typing import Protocol

import redis
from redis import Redis


MessageRecord = dict[str, str]
SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class ConversationMemory(Protocol):
    def load(self, user_id: str, conversation_id: str) -> list[MessageRecord]: ...

    def save(
        self,
        user_id: str,
        conversation_id: str,
        messages: list[MessageRecord],
    ) -> None: ...

    def append_turn(
        self,
        user_id: str,
        conversation_id: str,
        user_message: str,
        assistant_message: str,
    ) -> None: ...


def conversation_key(user_id: str, conversation_id: str) -> str:
    for field_name, value in (
        ("user_id", user_id),
        ("conversation_id", conversation_id),
    ):
        if not SAFE_ID.fullmatch(value):
            raise ValueError(
                f"{field_name} must contain 1-64 letters, numbers, '_' or '-'."
            )
    return f"agenthub:{user_id}:{conversation_id}"


class RedisMemory:
    def __init__(
        self,
        url: str,
        *,
        ttl_seconds: int = 604800,
        client: Redis | None = None,
    ) -> None:
        self.redis = client or redis.from_url(url, decode_responses=True)
        self.ttl_seconds = ttl_seconds

    def ping(self) -> bool:
        return bool(self.redis.ping())

    def load(self, user_id: str, conversation_id: str) -> list[MessageRecord]:
        value = self.redis.get(conversation_key(user_id, conversation_id))
        if not value:
            return []
        payload = json.loads(value)
        if not isinstance(payload, list):
            raise ValueError("Stored conversation payload must be a JSON list.")
        return payload

    def save(
        self,
        user_id: str,
        conversation_id: str,
        messages: list[MessageRecord],
    ) -> None:
        key = conversation_key(user_id, conversation_id)
        value = json.dumps(messages, ensure_ascii=False)
        if self.ttl_seconds > 0:
            self.redis.setex(key, self.ttl_seconds, value)
        else:
            self.redis.set(key, value)

    def append_turn(
        self,
        user_id: str,
        conversation_id: str,
        user_message: str,
        assistant_message: str,
    ) -> None:
        messages = self.load(user_id, conversation_id)
        messages.extend(
            [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_message},
            ]
        )
        self.save(user_id, conversation_id, messages)


class InMemoryMemory:
    def __init__(self) -> None:
        self._data: dict[str, list[MessageRecord]] = {}
        self._lock = RLock()

    def ping(self) -> bool:
        return True

    def load(self, user_id: str, conversation_id: str) -> list[MessageRecord]:
        key = conversation_key(user_id, conversation_id)
        with self._lock:
            return deepcopy(self._data.get(key, []))

    def save(
        self,
        user_id: str,
        conversation_id: str,
        messages: list[MessageRecord],
    ) -> None:
        key = conversation_key(user_id, conversation_id)
        with self._lock:
            self._data[key] = deepcopy(messages)

    def append_turn(
        self,
        user_id: str,
        conversation_id: str,
        user_message: str,
        assistant_message: str,
    ) -> None:
        messages = self.load(user_id, conversation_id)
        messages.extend(
            [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_message},
            ]
        )
        self.save(user_id, conversation_id, messages)

