import json
import time
import asyncio

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


def _build_initial_state(message: str, chat_history: list, conversation_id: int, user_id: int | None = None) -> RAGState:
    """Build the initial RAG state for a chat request."""
    return {
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
        "conversation_id": conversation_id,
        "message_id": None,
        "workflow_trace": [],
        "user_id": user_id,
    }


async def _get_or_create_conversation(session: AsyncSession, user_id: int, conversation_id: int | None, message: str) -> Conversation:
    """Get existing conversation or create a new one."""
    conv_repo = ConversationRepository(session)
    if conversation_id:
        conversation = await conv_repo.get(conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        return conversation

    # Auto-generate title from first message (truncate at 50 chars)
    title = message.strip()[:50] if message.strip() else "新对话"
    conversation = Conversation(user_id=user_id, title=title)
    conversation = await conv_repo.create(conversation)
    await session.commit()
    return conversation


async def _build_chat_history(conversation_id: int) -> list:
    """Build chat history from Redis."""
    history_data = await get_history(conversation_id)
    chat_history = []
    for h in history_data:
        if h["role"] == "user":
            chat_history.append(HumanMessage(content=h["content"]))
        else:
            chat_history.append(AIMessage(content=h["content"]))
    return chat_history


async def _save_result(session: AsyncSession, conversation: Conversation, result: dict) -> dict:
    """Save the RAG result to database and return the response."""
    msg_repo = MessageRepository(session)

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
        query=result.get("original_query", ""),
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


async def chat(session: AsyncSession, user_id: int, message: str, conversation_id: int | None = None) -> dict:
    """Non-streaming chat: run the full RAG workflow and return the result."""
    conversation = await _get_or_create_conversation(session, user_id, conversation_id, message)
    await save_message(conversation.id, "user", message)

    chat_history = await _build_chat_history(conversation.id)
    initial_state = _build_initial_state(message, chat_history, conversation.id, user_id)

    rag_app = get_rag_app()
    t0 = time.time()
    try:
        result = await rag_app.ainvoke(initial_state)
    except Exception as e:
        logger.error("workflow_failed", error=str(e), query=message[:50])
        raise HTTPException(status_code=500, detail="Chat processing failed")
    elapsed = time.time() - t0
    logger.info("workflow_complete", elapsed=f"{elapsed:.1f}s", query=message[:50])

    return await _save_result(session, conversation, result)


async def chat_stream(user_id: int, message: str, conversation_id: int | None = None):
    """Streaming chat: run the RAG workflow and yield progress events.

    Creates its own DB session since the SSE generator outlives the request session.
    Yields tuples of (event_type: str, data: dict) for each workflow step.
    """
    from src.core.deps import async_session_factory

    async with async_session_factory() as session:
        conversation = await _get_or_create_conversation(session, user_id, conversation_id, message)
        await save_message(conversation.id, "user", message)

        chat_history = await _build_chat_history(conversation.id)
        initial_state = _build_initial_state(message, chat_history, conversation.id, user_id)

        rag_app = get_rag_app()
        t0 = time.time()

        # Run the workflow with streaming
        accumulated_state = dict(initial_state)
        try:
            async for event in rag_app.astream(initial_state, stream_mode="updates"):
                for node_name, state_update in event.items():
                    if node_name == "__end__":
                        continue

                    # Merge state updates into accumulated state
                    for key, value in state_update.items():
                        if value is not None:
                            accumulated_state[key] = value

                    # Emit progress event based on the node
                    trace = state_update.get("workflow_trace", [])
                    step_info = trace[-1] if trace else {}

                    event_data = {
                        "agent": node_name,
                        "step": step_info,
                        "timestamp": time.time(),
                    }

                    # Add step-specific data
                    if node_name == "planner":
                        event_data["plan"] = state_update.get("retrieval_plan", "")
                    elif node_name == "query_agent":
                        event_data["rewritten_query"] = state_update.get("rewritten_query", "")
                        event_data["expanded_queries"] = state_update.get("expanded_queries", [])
                    elif node_name == "retriever":
                        event_data["doc_count"] = len(state_update.get("retrieved_documents", []))
                    elif node_name == "rerank":
                        event_data["doc_count"] = len(state_update.get("reranked_documents", []))
                    elif node_name == "reflection":
                        event_data["passed"] = state_update.get("reflection_passed", False)
                        event_data["result"] = state_update.get("reflection_result", "")
                    elif node_name == "answer":
                        answer_text = state_update.get("final_answer", "")
                        event_data["answer_length"] = len(answer_text)
                        # Send token event with the answer text
                        if answer_text:
                            yield ("token", {"text": answer_text})

                    yield ("progress", event_data)

        except Exception as e:
            logger.error("workflow_stream_failed", error=str(e), query=message[:50])
            yield ("error", {"detail": "Chat processing failed"})
            return

        elapsed = time.time() - t0
        logger.info("workflow_stream_complete", elapsed=f"{elapsed:.1f}s", query=message[:50])

        # Save the result using accumulated state
        final_answer = accumulated_state.get("final_answer", "")
        if final_answer:
            result = await _save_result(session, conversation, accumulated_state)
            yield ("final", result)
        else:
            yield ("error", {"detail": "No answer generated"})
