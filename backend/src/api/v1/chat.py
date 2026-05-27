import json

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user
from src.core.deps import get_db
from src.models.user import User
from src.schemas.chat import ChatRequest
from src.services.chat_service import chat

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def chat_endpoint(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await chat(db, user_id=current_user.id, message=request.message, conversation_id=request.conversation_id)
    return result


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    async def event_generator():
        result = await chat(db, user_id=current_user.id, message=request.message, conversation_id=request.conversation_id)
        yield {"event": "token", "data": json.dumps({"text": result["answer"]}, ensure_ascii=False)}
        yield {"event": "final", "data": json.dumps(result, ensure_ascii=False, default=str)}

    return EventSourceResponse(event_generator())
