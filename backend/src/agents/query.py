import json

from src.agents.state import RAGState
from src.agents.planner import get_llm, _extract_text

import structlog

logger = structlog.get_logger()


async def query_agent(state: RAGState) -> dict:
    """Pass through optimized query from planner (merged for speed)."""
    rewritten = state.get("rewritten_query", state["original_query"])
    expanded = state.get("expanded_queries", [state["original_query"]])

    logger.info("query_agent_passthrough", rewritten=rewritten[:50], expanded_count=len(expanded))

    trace_entry = {"step": "query_agent", "output": {"rewritten": rewritten, "expanded": expanded}}
    return {
        "rewritten_query": rewritten,
        "expanded_queries": expanded,
        "workflow_trace": state.get("workflow_trace", []) + [trace_entry],
    }
