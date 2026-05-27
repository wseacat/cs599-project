from sqlalchemy.ext.asyncio import AsyncSession

from src.models.retrieval import RetrievalLog
from src.repositories.retrieval_repo import RetrievalLogRepository

import structlog

logger = structlog.get_logger()


async def get_retrieval_debug(session: AsyncSession, message_id: int) -> dict | None:
    repo = RetrievalLogRepository(session)
    logs = await repo.get_by_filter(message_id=message_id)
    if not logs:
        return None
    log = logs[0]
    return {
        "query": log.query,
        "plan": log.plan,
        "retrieved_docs": log.retrieved_docs,
        "reranked_docs": log.reranked_docs,
        "reflection_result": log.reflection_result,
    }
