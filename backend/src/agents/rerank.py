from src.agents.state import RAGState
from src.retrieval.reranker import rerank
from src.core.config import get_settings

import structlog

logger = structlog.get_logger()


async def rerank_agent(state: RAGState) -> dict:
    """Rerank retrieved documents using BGE Reranker."""
    retrieved = state.get("retrieved_documents", [])
    query = state.get("rewritten_query", state["original_query"])
    settings = get_settings()

    # Return empty if no documents retrieved
    if not retrieved:
        return {"reranked_documents": [], "workflow_trace": state.get("workflow_trace", [])}

    # Rerank documents with fallback to score-based sorting
    try:
        reranked = await rerank(query, retrieved, top_k=settings.RERANK_TOP_K)
    except Exception as e:
        logger.warning("rerank_agent_failed", error=str(e))
        reranked = sorted(retrieved, key=lambda x: x.get("score", 0), reverse=True)[:settings.RERANK_TOP_K]

    logger.info("rerank_agent_complete", input_count=len(retrieved), output_count=len(reranked))

    trace_entry = {"step": "rerank", "input_count": len(retrieved), "output_count": len(reranked)}
    return {
        "reranked_documents": reranked,
        "workflow_trace": state.get("workflow_trace", []) + [trace_entry],
    }
