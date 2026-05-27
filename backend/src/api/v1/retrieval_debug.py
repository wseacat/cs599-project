from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user
from src.core.deps import get_db
from src.models.user import User
from src.services.retrieval_service import get_retrieval_debug

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@router.get("/debug/{message_id}")
async def retrieval_debug(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await get_retrieval_debug(db, message_id)
    if not result:
        return {"error": "No retrieval log found"}
    return result
