import json

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user
from src.core.deps import get_db
from src.models.user import User
from src.schemas.chat import ChatRequest
from src.services.chat_service import chat, chat_stream

import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def chat_endpoint(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message and get a complete response."""
    result = await chat(db, user_id=current_user.id, message=request.message, conversation_id=request.conversation_id)
    return result


@router.post("/stream")
async def chat_stream_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """Send a message and get a streaming response via SSE.

    Emits real-time agent progress events as the RAG workflow executes:
    - progress: each agent step (planner, query, retriever, rerank, reflection, answer)
    - token: the final answer text
    - final: complete result with citations
    - error: if something fails
    """

    async def event_generator():
        try:
            async for event_type, event_data in chat_stream(
                user_id=current_user.id,
                message=request.message,
                conversation_id=request.conversation_id,
            ):
                if event_type == "progress":
                    yield {
                        "event": "progress",
                        "data": json.dumps(event_data, ensure_ascii=False),
                    }
                elif event_type == "final":
                    yield {
                        "event": "token",
                        "data": json.dumps({"text": event_data.get("answer", "")}, ensure_ascii=False),
                    }
                    yield {
                        "event": "final",
                        "data": json.dumps(event_data, ensure_ascii=False, default=str),
                    }
                elif event_type == "error":
                    yield {
                        "event": "error",
                        "data": json.dumps(event_data, ensure_ascii=False),
                    }

        except Exception as e:
            logger.error("chat_stream_failed", error=str(e))
            yield {
                "event": "error",
                "data": json.dumps({"detail": str(e)}, ensure_ascii=False),
            }

    return EventSourceResponse(event_generator())
