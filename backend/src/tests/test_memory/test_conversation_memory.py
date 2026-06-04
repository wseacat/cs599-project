import pytest
from src.memory.conversation_memory import get_history, clear_history


@pytest.mark.asyncio
async def test_get_history_empty():
    history = await get_history(99999)
    assert history == []


@pytest.mark.asyncio
async def test_clear_history_nonexistent():
    await clear_history(99999)
