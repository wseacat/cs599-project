import asyncio
import hashlib
import json

import structlog

from src.retrieval.bm25 import get_bm25_index
from src.retrieval.vector_store import search_similar
from src.memory.conversation_memory import get_redis

logger = structlog.get_logger()

# Cache TTL for search results (5 minutes)
SEARCH_CACHE_TTL = 300


async def hybrid_search(query: str, top_k: int = 10, user_id: int | None = None) -> list[dict]:
    # Check cache first
    cache_key = f"search:{hashlib.md5(query.encode()).hexdigest()}:{top_k}"
    try:
        redis = await get_redis()
        cached = await redis.get(cache_key)
        if cached:
            logger.info("search_cache_hit", query=query[:50])
            return json.loads(cached)
    except Exception:
        pass

    # Run BM25 and vector search in parallel
    bm25_index = get_bm25_index()
    bm25_task = asyncio.to_thread(bm25_index.search, query, top_k, user_id)
    vector_task = search_similar(query, top_k=top_k)

    bm25_results, vector_results = await asyncio.gather(
        bm25_task,
        vector_task,
        return_exceptions=True,
    )

    # Handle exceptions
    if isinstance(bm25_results, Exception):
        logger.warning("bm25_search_failed", error=str(bm25_results))
        bm25_results = []

    if isinstance(vector_results, Exception):
        logger.warning("vector_search_failed", error=str(vector_results))
        vector_results = []

    # Merge by chunk_id
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

    # Cache results
    try:
        redis = await get_redis()
        await redis.setex(cache_key, SEARCH_CACHE_TTL, json.dumps(ranked, ensure_ascii=False))
    except Exception:
        pass

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
