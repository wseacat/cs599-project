from src.agents.state import RAGState
from src.agents.planner import get_llm, _extract_text

import structlog

logger = structlog.get_logger()


async def answer_agent(state: RAGState) -> dict:
    """Generate final answer with citations from reranked documents."""
    query = state["original_query"]
    reranked = state.get("reranked_documents", [])
    chat_history = state.get("chat_history", [])

    # Build conversation history context
    history_text = ""
    if chat_history:
        history_text = "\n".join([f"{msg.type}: {msg.content}" for msg in chat_history[-6:]])

    # Build document context and citations
    context_parts = []
    citations = []
    for i, doc in enumerate(reranked):
        content = doc.get("content", "")
        context_parts.append(f"[{i+1}] {content}")
        citations.append({
            "document_id": doc.get("document_id", 0),
            "chunk_id": doc.get("chunk_id", 0),
            "filename": doc.get("metadata", {}).get("filename") if doc.get("metadata") else None,
            "page": doc.get("metadata", {}).get("page") if doc.get("metadata") else None,
            "snippet": content[:200],
        })

    context = "\n\n".join(context_parts)

    # Generate answer with LLM
    llm = get_llm()
    prompt = f"""你是一个企业知识库问答助手。根据提供的文档上下文回答用户问题。

用户问题：{query}

{f'对话历史：{history_text}' if history_text else ''}

参考文档：
{context}

要求：
1. 只根据提供的文档内容回答
2. 回答要准确、完整、有条理
3. 在回答中标注引用来源，使用 [1] [2] 格式
4. 如果文档信息不足以回答，请明确说明

请直接输出回答内容，不要返回JSON。"""

    try:
        response = await llm.ainvoke(prompt)
        answer = _extract_text(response.content)
    except Exception as e:
        logger.error("answer_generation_failed", error=str(e))
        answer = "抱歉，生成答案时出现错误，请稍后重试。"

    logger.info("answer_complete", query=query[:50], answer_length=len(answer), citations_count=len(citations))

    trace_entry = {"step": "answer", "citations_count": len(citations)}
    return {
        "final_answer": answer,
        "citations": citations,
        "workflow_trace": state.get("workflow_trace", []) + [trace_entry],
    }
