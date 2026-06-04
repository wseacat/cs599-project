from src.retrieval.bm25 import BM25Index


def test_bm25_index_empty():
    index = BM25Index()
    results = index.search("test")
    assert results == []


def test_bm25_index_build():
    index = BM25Index()
    documents = ["Hello World", "Python programming", "Machine learning"]
    chunk_ids = [1, 2, 3]
    index.build(documents, chunk_ids)
    assert len(index._corpus) == 3


def test_bm25_index_search():
    index = BM25Index()
    documents = ["Hello World", "Python programming", "Machine learning"]
    chunk_ids = [1, 2, 3]
    index.build(documents, chunk_ids)
    results = index.search("Python")
    assert len(results) > 0
    assert results[0]["chunk_id"] == 2


def test_bm25_index_add_documents():
    index = BM25Index()
    documents = ["Hello World"]
    chunk_ids = [1]
    index.build(documents, chunk_ids)

    new_docs = ["Python programming", "Machine learning"]
    new_ids = [2, 3]
    index.add_documents(new_docs, new_ids)
    assert len(index._corpus) == 3


def test_bm25_index_remove_documents():
    index = BM25Index()
    documents = ["Hello World", "Python programming", "Machine learning"]
    chunk_ids = [1, 2, 3]
    index.build(documents, chunk_ids)

    index.remove_by_chunk_ids({2})
    assert len(index._corpus) == 2
    assert 2 not in index._chunk_ids


def test_bm25_index_search_no_results():
    index = BM25Index()
    documents = ["Hello World"]
    chunk_ids = [1]
    index.build(documents, chunk_ids)
    results = index.search("Nonexistent")
    assert len(results) == 0
