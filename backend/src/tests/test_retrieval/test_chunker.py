from src.retrieval.chunker import chunk_text


def test_chunk_text_basic():
    text = "这是一段测试文本。" * 100
    chunks = chunk_text(text)
    assert len(chunks) > 0
    assert all("content" in c for c in chunks)
    assert all("chunk_index" in c for c in chunks)


def test_chunk_text_with_metadata():
    text = "测试内容" * 100
    metadata = {"filename": "test.pdf", "document_id": 1}
    chunks = chunk_text(text, metadata=metadata)
    assert len(chunks) > 0
    assert chunks[0]["metadata"]["filename"] == "test.pdf"


def test_chunk_text_short():
    text = "短文本"
    chunks = chunk_text(text)
    assert len(chunks) >= 1
