import json
import time

from fastapi import HTTPException, status
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.state import RAGState
from src.memory.conversation_memory import get_history, save_message
from src.models.conversation import Conversation, Message
from src.models.retrieval import Citation, RetrievalLog
from src.repositories.conversation_repo import ConversationRepository, MessageRepository
from src.repositories.retrieval_repo import CitationRepository, RetrievalLogRepository
from src.workflows.rag_workflow import get_rag_app

import structlog

logger = structlog.get_logger()


async def chat(session: AsyncSession, user_id: int, message: str, conversation_id: int | None = None) -> dict:
    conv_repo = ConversationRepository(session)
    msg_repo = MessageRepository(session)

    if conversation_id:
        conversation = await conv_repo.get(conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    else:
        conversation = Conversation(user_id=user_id, title=message[:50])
        conversation = await conv_repo.create(conversation)
        await session.commit()

    await save_message(conversation.id, "user", message)

    history_data = await get_history(conversation.id)
    chat_history = []
    for h in history_data:
        if h["role"] == "user":
            chat_history.append(HumanMessage(content=h["content"]))
        else:
            chat_history.append(AIMessage(content=h["content"]))

    initial_state: RAGState = {
        "original_query": message,
        "rewritten_query": "",
        "expanded_queries": [],
        "retrieval_plan": "",
        "retrieved_documents": [],
        "reranked_documents": [],
        "reflection_result": "",
        "reflection_passed": False,
        "retry_count": 0,
        "final_answer": "",
        "citations": [],
        "chat_history": chat_history,
        "conversation_id": conversation.id,
        "message_id": None,
        "workflow_trace": [],
    }

    rag_app = get_rag_app()
    t0 = time.time()
    try:
        result = await rag_app.ainvoke(initial_state)
    except Exception as e:
        logger.error("workflow_failed", error=str(e), query=message[:50])
        raise HTTPException(status_code=500, detail="Chat processing failed")
    elapsed = time.time() - t0
    logger.info("workflow_complete", elapsed=f"{elapsed:.1f}s", query=message[:50])

    ai_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=result.get("final_answer", ""),
        citations_json=json.dumps(result.get("citations", []), ensure_ascii=False),
    )
    ai_message = await msg_repo.create(ai_message)

    # Batch insert citations
    citations = result.get("citations", [])
    citation_objs = []
    for c in citations:
        doc_id = c.get("document_id", 0)
        chunk_id = c.get("chunk_id", 0)
        if not doc_id or not chunk_id:
            continue
        citation_objs.append(Citation(
            message_id=ai_message.id,
            document_id=doc_id,
            chunk_id=chunk_id,
            page=c.get("page"),
            snippet=c.get("snippet"),
        ))
    if citation_objs:
        session.add_all(citation_objs)

    retrieval_log = RetrievalLog(
        message_id=ai_message.id,
        query=message,
        plan=result.get("retrieval_plan", ""),
        retrieved_docs=json.dumps(result.get("retrieved_documents", []), ensure_ascii=False, default=str),
        reranked_docs=json.dumps(result.get("reranked_documents", []), ensure_ascii=False, default=str),
        reflection_result=result.get("reflection_result", ""),
    )
    session.add(retrieval_log)

    await session.commit()
    await save_message(conversation.id, "assistant", result.get("final_answer", ""))

    return {
        "answer": result.get("final_answer", ""),
        "conversation_id": conversation.id,
        "message_id": ai_message.id,
        "citations": citations,
        "workflow_trace": result.get("workflow_trace", []),
    }
