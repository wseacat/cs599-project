import pytest
from src.workflows.document_pipeline import process_document


@pytest.mark.asyncio
async def test_process_document_empty():
    result = await process_document(1, "", "test.txt")
    assert result["chunk_count"] == 0
    assert result["status"] == "empty"


@pytest.mark.asyncio
async def test_process_document_short():
    content = "Hello World"
    result = await process_document(1, content, "test.txt")
    assert result["chunk_count"] >= 1
    assert result["status"] == "completed"


@pytest.mark.asyncio
async def test_process_document_long():
    content = "Hello World " * 1000
    result = await process_document(1, content, "test.txt")
    assert result["chunk_count"] > 1
    assert result["status"] == "completed"
