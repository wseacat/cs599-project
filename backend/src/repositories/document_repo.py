from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.document import Document, DocumentChunk
from src.repositories.base import GenericRepository


class DocumentRepository(GenericRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Document)

    async def get_user_documents(self, user_id: int) -> list[Document]:
        stmt = select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class DocumentChunkRepository(GenericRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, DocumentChunk)

    async def get_document_chunks(self, document_id: int) -> list[DocumentChunk]:
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_document_chunks(self, document_id: int) -> None:
        chunks = await self.get_document_chunks(document_id)
        for chunk in chunks:
            await self.session.delete(chunk)
        await self.session.flush()
