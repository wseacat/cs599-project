from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user
from src.core.deps import get_db
from src.models.user import User
from src.services.retrieval_service import get_retrieval_debug

import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@router.get("/debug/{message_id}")
async def retrieval_debug(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get retrieval debug information for a message."""
    try:
        result = await get_retrieval_debug(db, message_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No retrieval log found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("retrieval_debug_failed", message_id=message_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get retrieval debug info")
