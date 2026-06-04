import pytest
from src.agents.reflection import reflection_agent


@pytest.mark.asyncio
async def test_reflection_agent_no_documents():
    state = {
        "original_query": "test",
        "reranked_documents": [],
        "retry_count": 0,
        "workflow_trace": [],
    }
    result = await reflection_agent(state)
    assert result["reflection_passed"] is False
    assert result["retry_count"] == 1


@pytest.mark.asyncio
async def test_reflection_agent_with_documents():
    state = {
        "original_query": "test",
        "reranked_documents": [{"id": 1}, {"id": 2}, {"id": 3}],
        "retry_count": 0,
        "workflow_trace": [],
    }
    result = await reflection_agent(state)
    assert result["reflection_passed"] is True
    assert result["retry_count"] == 0


@pytest.mark.asyncio
async def test_reflection_agent_few_documents():
    state = {
        "original_query": "test",
        "reranked_documents": [{"id": 1}],
        "retry_count": 0,
        "workflow_trace": [],
    }
    result = await reflection_agent(state)
    assert result["reflection_passed"] is True
    assert result["retry_count"] == 0


@pytest.mark.asyncio
async def test_reflection_agent_max_retry():
    state = {
        "original_query": "test",
        "reranked_documents": [],
        "retry_count": 2,
        "workflow_trace": [],
    }
    result = await reflection_agent(state)
    assert result["reflection_passed"] is False
    assert result["retry_count"] == 2
