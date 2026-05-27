import json
import time

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
    else:
        conversation = Conversation(user_id=user_id, title=message[:50])
        conversation = await conv_repo.create(conversation)
        await session.commit()

    await save_message(conversation.id, "user", message)

    history_data = await get_history(conversation.id)
    chat_history = []
    for h in history_data:
        from langchain_core.messages import AIMessage, HumanMessage
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
    result = await rag_app.ainvoke(initial_state)
    elapsed = time.time() - t0
    logger.info("workflow_complete", elapsed=f"{elapsed:.1f}s", query=message[:50])

    ai_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=result.get("final_answer", ""),
        citations_json=json.dumps(result.get("citations", []), ensure_ascii=False),
    )
    ai_message = await msg_repo.create(ai_message)

    citations = result.get("citations", [])
    citation_repo = CitationRepository(session)
    for c in citations:
        doc_id = c.get("document_id", 0)
        chunk_id = c.get("chunk_id", 0)
        if not doc_id or not chunk_id:
            continue
        citation = Citation(
            message_id=ai_message.id,
            document_id=doc_id,
            chunk_id=chunk_id,
            page=c.get("page"),
            snippet=c.get("snippet"),
        )
        await citation_repo.create(citation)

    retrieval_log = RetrievalLog(
        message_id=ai_message.id,
        query=message,
        plan=result.get("retrieval_plan", ""),
        retrieved_docs=json.dumps(result.get("retrieved_documents", []), ensure_ascii=False, default=str),
        reranked_docs=json.dumps(result.get("reranked_documents", []), ensure_ascii=False, default=str),
        reflection_result=result.get("reflection_result", ""),
    )
    log_repo = RetrievalLogRepository(session)
    await log_repo.create(retrieval_log)

    await session.commit()
    await save_message(conversation.id, "assistant", result.get("final_answer", ""))

    return {
        "answer": result.get("final_answer", ""),
        "conversation_id": conversation.id,
        "message_id": ai_message.id,
        "citations": citations,
        "workflow_trace": result.get("workflow_trace", []),
    }
