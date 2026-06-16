import json

from langchain_openai import ChatOpenAI

from src.agents.state import RAGState
from src.core.config import get_settings

import structlog

logger = structlog.get_logger()


def _extract_text(content) -> str:
    """Extract text from LLM response content."""
    if isinstance(content, str):
        return content
    if isinstance(content, list) and content:
        block = content[0]
        if isinstance(block, dict):
            return block.get("text", "")
        return getattr(block, "text", str(block))
    return ""


_llm: ChatOpenAI | None = None


def get_llm() -> ChatOpenAI:
    """Get or create LLM instance (singleton)."""
    global _llm
    if _llm is not None:
        return _llm
    settings = get_settings()
    _llm = ChatOpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=settings.LLM_MAX_TOKENS,
        timeout=60,
        max_retries=1,
    )
    return _llm


async def planner_agent(state: RAGState) -> dict:
    """Analyze user query and generate retrieval plan."""
    query = state["original_query"]
    chat_history = state.get("chat_history", [])

    # Build conversation history context
    history_text = ""
    if chat_history:
        history_text = "\n".join([f"{msg.type}: {msg.content}" for msg in chat_history[-6:]])

    llm = get_llm()
    prompt = f"""你是一个查询分析专家。分析用户问题并生成检索计划。

用户问题：{query}

{f'对话历史：{history_text}' if history_text else ''}

请返回JSON格式的检索计划：
{{
    "needs_decomposition": true/false,
    "sub_queries": ["子查询1", "子查询2"],
    "strategy": "描述检索策略",
    "key_entities": ["关键实体1", "关键实体2"]
}}

只返回JSON，不要其他内容。"""

    try:
        response = await llm.ainvoke(prompt)
        plan_text = _extract_text(response.content)
        # Try to extract JSON from response (may contain markdown code blocks)
        if "```" in plan_text:
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', plan_text, re.DOTALL)
            if json_match:
                plan_text = json_match.group(1)
        plan = json.loads(plan_text)
    except Exception as e:
        logger.warning("planner_parse_failed", error=str(e))
        plan = {"needs_decomposition": False, "sub_queries": [query], "strategy": "直接检索", "key_entities": []}

    logger.info("planner_complete", query=query[:50], plan=plan)

    trace_entry = {"step": "planner", "input": query[:100], "output": plan}
    return {
        "retrieval_plan": json.dumps(plan, ensure_ascii=False),
        "workflow_trace": state.get("workflow_trace", []) + [trace_entry],
    }
