import json

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.retrieval import RetrievalLog
from src.repositories.retrieval_repo import RetrievalLogRepository

import structlog

logger = structlog.get_logger()


async def get_retrieval_debug(session: AsyncSession, message_id: int) -> dict | None:
    """Get retrieval debug information for a message."""
    repo = RetrievalLogRepository(session)
    logs = await repo.get_by_filter(message_id=message_id)
    if not logs:
        return None

    log = logs[0]

    # Parse JSON fields
    retrieved_docs = []
    reranked_docs = []

    try:
        if log.retrieved_docs:
            retrieved_docs = json.loads(log.retrieved_docs)
    except json.JSONDecodeError:
        logger.warning("failed_to_parse_retrieved_docs", message_id=message_id)

    try:
        if log.reranked_docs:
            reranked_docs = json.loads(log.reranked_docs)
    except json.JSONDecodeError:
        logger.warning("failed_to_parse_reranked_docs", message_id=message_id)

    return {
        "query": log.query,
        "plan": log.plan,
        "retrieved_docs": retrieved_docs,
        "reranked_docs": reranked_docs,
        "reflection_result": log.reflection_result,
        "retrieved_count": len(retrieved_docs),
        "reranked_count": len(reranked_docs),
    }
