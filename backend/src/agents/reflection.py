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
    elif len(reranked) >= 3:
        # Use LLM to evaluate relevance for sufficient document count
        try:
            llm = get_llm()
            doc_summaries = "\n".join(
                f"[{i+1}] {doc.get('content', '')[:150]}"
                for i, doc in enumerate(reranked[:5])
            )
            prompt = f"""判断以下检索结果是否与用户问题相关。

用户问题：{query}

检索结果：
{doc_summaries}

返回JSON格式：
{{"passed": true/false, "reason": "判断理由"}}

只返回JSON，不要其他内容。"""

            response = await llm.ainvoke(prompt)
            eval_text = _extract_text(response.content)
            eval_result = json.loads(eval_text)
            passed = eval_result.get("passed", True)
            result = eval_result.get("reason", "LLM evaluation completed")
        except Exception as e:
            logger.warning("reflection_llm_failed", error=str(e))
            # Fallback to count-based evaluation
            passed = True
            result = f"LLM evaluation failed, auto-passed with {len(reranked)} documents"
    else:
        # Few documents - still pass but with warning
        passed = True
        result = f"Auto-pass: {len(reranked)} documents retrieved (few but acceptable)"

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
