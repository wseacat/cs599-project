import structlog

from src.retrieval.bm25 import get_bm25_index
from src.retrieval.vector_store import search_similar

logger = structlog.get_logger()


async def hybrid_search(query: str, top_k: int = 10) -> list[dict]:
    bm25_index = get_bm25_index()
    bm25_results = bm25_index.search(query, top_k=top_k)

    vector_results = []
    try:
        vector_results = await search_similar(query, top_k=top_k)
    except Exception:
        logger.warning("vector_search_failed", query=query[:50])

    # Merge by chunk_id (both sources now use chunk_id)
    merged: dict[int, dict] = {}

    for r in bm25_results:
        key = r["chunk_id"]
        merged[key] = {**r, "bm25_score": r["score"], "vector_score": 0.0}

    for r in vector_results:
        key = r["chunk_id"]
        if key in merged:
            merged[key]["vector_score"] = r["score"]
        else:
            merged[key] = {**r, "bm25_score": 0.0, "vector_score": r["score"]}

    ranked = rrf_rank(list(merged.values()), top_k=top_k)
    logger.info("hybrid_search_complete", query=query[:50], results_count=len(ranked))
    return ranked


def rrf_rank(results: list[dict], k: int = 60, top_k: int = 10) -> list[dict]:
    # Assign BM25 ranks
    bm25_sorted = sorted(
        [r for r in results if r.get("bm25_score", 0) > 0],
        key=lambda x: x["bm25_score"],
        reverse=True,
    )
    for i, r in enumerate(bm25_sorted):
        r["bm25_rank"] = i + 1

    # Assign vector ranks
    vector_sorted = sorted(
        [r for r in results if r.get("vector_score", 0) > 0],
        key=lambda x: x["vector_score"],
        reverse=True,
    )
    for i, r in enumerate(vector_sorted):
        r["vector_rank"] = i + 1

    # Compute RRF scores once
    for r in results:
        bm25_rank = r.get("bm25_rank", k + 1)
        vector_rank = r.get("vector_rank", k + 1)
        r["rrf_score"] = 1.0 / (k + bm25_rank) + 1.0 / (k + vector_rank)

    ranked = sorted(results, key=lambda x: x["rrf_score"], reverse=True)[:top_k]
    return ranked
