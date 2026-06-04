import json

from src.agents.state import RAGState
from src.agents.planner import get_llm, _extract_text

import structlog

logger = structlog.get_logger()


async def query_agent(state: RAGState) -> dict:
    """Optimize and expand user query for better retrieval."""
    query = state["original_query"]
    plan = state.get("retrieval_plan", "{}")
    retry_count = state.get("retry_count", 0)
    reflection_result = state.get("reflection_result", "")

    # Parse retrieval plan
    try:
        plan_obj = json.loads(plan)
    except json.JSONDecodeError:
        plan_obj = {"sub_queries": [query]}

    # Add retry hint if this is a retry attempt
    retry_hint = ""
    if retry_count > 0:
        retry_hint = f"\n上一次检索结果不理想：{reflection_result}\n请调整查询策略。"

    llm = get_llm()
    prompt = f"""你是一个查询优化专家。对用户查询进行改写和扩展。

原始查询：{query}
检索计划：{json.dumps(plan_obj, ensure_ascii=False)}
{retry_hint}

请返回JSON格式：
{{
    "rewritten_query": "优化后的查询",
    "expanded_queries": ["扩展查询1", "扩展查询2", "扩展查询3"]
}}

要求：
1. rewritten_query: 改写为更适合检索的形式
2. expanded_queries: 生成2-4个相关查询，覆盖不同方面

只返回JSON，不要其他内容。"""

    try:
        response = await llm.ainvoke(prompt)
        result_text = _extract_text(response.content)
        result = json.loads(result_text)
        rewritten = result.get("rewritten_query", query)
        expanded = result.get("expanded_queries", [query])
    except Exception as e:
        logger.warning("query_optimization_failed", error=str(e))
        rewritten = query
        expanded = [query]

    logger.info("query_agent_complete", rewritten=rewritten[:50], expanded_count=len(expanded))

    trace_entry = {"step": "query_agent", "input": query[:100], "output": {"rewritten": rewritten, "expanded": expanded}}
    return {
        "rewritten_query": rewritten,
        "expanded_queries": expanded,
        "workflow_trace": state.get("workflow_trace", []) + [trace_entry],
    }
