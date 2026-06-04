from src.retrieval.hybrid import rrf_rank


def test_rrf_rank_empty():
    results = []
    ranked = rrf_rank(results)
    assert ranked == []


def test_rrf_rank_single():
    results = [
        {"chunk_id": 1, "bm25_score": 0.8, "vector_score": 0.9},
    ]
    ranked = rrf_rank(results, top_k=10)
    assert len(ranked) == 1
    assert "rrf_score" in ranked[0]


def test_rrf_rank_multiple():
    results = [
        {"chunk_id": 1, "bm25_score": 0.8, "vector_score": 0.3},
        {"chunk_id": 2, "bm25_score": 0.3, "vector_score": 0.9},
        {"chunk_id": 3, "bm25_score": 0.6, "vector_score": 0.6},
    ]
    ranked = rrf_rank(results, top_k=10)
    assert len(ranked) == 3
    assert all("rrf_score" in r for r in ranked)
    assert ranked[0]["rrf_score"] >= ranked[1]["rrf_score"]


def test_rrf_rank_top_k():
    results = [
        {"chunk_id": i, "bm25_score": 0.5, "vector_score": 0.5}
        for i in range(10)
    ]
    ranked = rrf_rank(results, top_k=3)
    assert len(ranked) == 3


def test_rrf_rank_with_zero_scores():
    results = [
        {"chunk_id": 1, "bm25_score": 0.0, "vector_score": 0.9},
        {"chunk_id": 2, "bm25_score": 0.9, "vector_score": 0.0},
    ]
    ranked = rrf_rank(results, top_k=10)
    assert len(ranked) == 2
    assert all("rrf_score" in r for r in ranked)
