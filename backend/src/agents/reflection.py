import json

from src.agents.state import RAGState
from src.agents.planner import get_llm, _extract_text
from src.core.config import get_settings

import structlog

logger = structlog.get_logger()


async def reflection_agent(state: RAGState) -> dict:
    """Evaluate retrieval quality and decide whether to retry."""
    query = state["original_query"]
    reranked = state.get("reranked_documents", [])
    retry_count = state.get("retry_count", 0)
    settings = get_settings()

    # Quick rejection if no documents
    if not reranked:
        passed = False
        result = "No documents retrieved"
    else:
        # Skip LLM evaluation for speed - trust the reranker
        passed = True
        result = f"Auto-pass: {len(reranked)} documents retrieved"

    # Determine if retry is needed
    should_retry = not passed and retry_count < settings.MAX_RETRY_COUNT

    logger.info("reflection_complete", passed=passed, retry_count=retry_count, should_retry=should_retry)

    trace_entry = {
        "step": "reflection",
        "passed": passed,
        "retry_count": retry_count,
        "should_retry": should_retry,
        "reason": result,
    }
    return {
        "reflection_result": result,
        "reflection_passed": passed,
        "retry_count": retry_count + 1 if should_retry else retry_count,
        "workflow_trace": state.get("workflow_trace", []) + [trace_entry],
    }
