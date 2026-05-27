import asyncio

from src.agents.state import RAGState
from src.retrieval.hybrid import hybrid_search
from src.core.config import get_settings

import structlog

logger = structlog.get_logger()


async def retriever_agent(state: RAGState) -> dict:
    original_query = state["original_query"]
    rewritten_query = state.get("rewritten_query", original_query)
    expanded_queries = state.get("expanded_queries", [rewritten_query])
    settings = get_settings()

    # Always include original query to avoid losing good matches from bad rewrites
    queries = list(dict.fromkeys([original_query, rewritten_query] + expanded_queries))

    # Run all searches concurrently
    search_results = await asyncio.gather(
        *[hybrid_search(q, top_k=settings.RETRIEVAL_TOP_K) for q in queries],
        return_exceptions=True,
    )

    all_results = {}
    for results in search_results:
        if isinstance(results, Exception):
            logger.warning("search_failed", error=str(results))
            continue
        for r in results:
            key = r.get("chunk_id") or r.get("doc_id")
            if key and key not in all_results:
                all_results[key] = r
            elif key and r.get("rrf_score", 0) > all_results[key].get("rrf_score", 0):
                all_results[key] = r

    documents = list(all_results.values())
    documents.sort(key=lambda x: x.get("rrf_score", 0), reverse=True)
    documents = documents[:settings.RETRIEVAL_TOP_K]

    logger.info("retriever_complete", query=rewritten_query[:50], doc_count=len(documents))

    trace_entry = {"step": "retriever", "input": rewritten_query[:100], "output": {"count": len(documents)}}
    return {
        "retrieved_documents": documents,
        "workflow_trace": state.get("workflow_trace", []) + [trace_entry],
    }
