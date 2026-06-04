import json

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user
from src.core.deps import get_db
from src.models.user import User
from src.schemas.chat import ChatRequest
from src.services.chat_service import chat

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
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message and get a streaming response via SSE."""

    async def event_generator():
        try:
            # Send start event
            yield {"event": "start", "data": json.dumps({"message": "Processing..."}, ensure_ascii=False)}

            # Process chat
            result = await chat(db, user_id=current_user.id, message=request.message, conversation_id=request.conversation_id)

            # Send token event with answer
            yield {"event": "token", "data": json.dumps({"text": result["answer"]}, ensure_ascii=False)}

            # Send final event with complete result
            yield {"event": "final", "data": json.dumps(result, ensure_ascii=False, default=str)}

        except Exception as e:
            logger.error("chat_stream_failed", error=str(e))
            yield {"event": "error", "data": json.dumps({"detail": str(e)}, ensure_ascii=False)}

    return EventSourceResponse(event_generator())
