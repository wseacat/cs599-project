from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user
from src.core.deps import get_db
from src.models.user import User
from src.repositories.conversation_repo import ConversationRepository, MessageRepository
from src.schemas.chat import ConversationDetailResponse, ConversationResponse, MessageResponse

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/", response_model=list[ConversationResponse])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conv_repo = ConversationRepository(db)
    rows = await conv_repo.get_user_conversations_with_counts(user_id=current_user.id)
    return [
        ConversationResponse(
            id=c.id, title=c.title, created_at=c.created_at,
            updated_at=c.updated_at, message_count=count,
        )
        for c, count in rows
    ]


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conv_repo = ConversationRepository(db)
    msg_repo = MessageRepository(db)
    conv = await conv_repo.get(conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    messages = await msg_repo.get_conversation_messages(conversation_id)
    return ConversationDetailResponse(
        id=conv.id,
        title=conv.title,
        messages=[MessageResponse(id=m.id, role=m.role, content=m.content, citations_json=m.citations_json, created_at=m.created_at) for m in messages],
    )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    import structlog
    logger = structlog.get_logger()
    try:
        from src.memory.conversation_memory import clear_history
        conv_repo = ConversationRepository(db)
        conv = await conv_repo.get(conversation_id)
        if not conv or conv.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        try:
            await clear_history(conversation_id)
        except Exception as e:
            logger.warning("redis_clear_failed", error=str(e))
        await conv_repo.delete(conv)
        await db.commit()
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_conversation_failed", error=str(e), type=type(e).__name__)
        raise HTTPException(status_code=500, detail=str(e))
