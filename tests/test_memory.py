import pytest

from app.memory.redis_memory import InMemoryMemory, conversation_key


def test_memory_isolates_users_and_conversations():
    memory = InMemoryMemory()
    memory.append_turn("user_a", "conv_1", "hello", "hi")
    memory.append_turn("user_a", "conv_2", "other", "response")
    memory.append_turn("user_b", "conv_1", "private", "answer")

    assert memory.load("user_a", "conv_1")[0]["content"] == "hello"
    assert memory.load("user_a", "conv_2")[0]["content"] == "other"
    assert memory.load("user_b", "conv_1")[0]["content"] == "private"


def test_conversation_key_contract_and_validation():
    assert conversation_key("user_001", "conv-001") == "agenthub:user_001:conv-001"
    with pytest.raises(ValueError):
        conversation_key("user:unsafe", "conv_001")

