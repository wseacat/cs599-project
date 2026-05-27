from sqlalchemy.ext.asyncio import AsyncSession

from src.models.retrieval import Citation, RetrievalLog
from src.repositories.base import GenericRepository


class RetrievalLogRepository(GenericRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, RetrievalLog)


class CitationRepository(GenericRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Citation)

    async def get_message_citations(self, message_id: int) -> list[Citation]:
        return list(await self.get_by_filter(message_id=message_id))
