from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.document import Document, DocumentChunk
from src.repositories.base import GenericRepository


class DocumentRepository(GenericRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Document)

    async def get_user_documents(self, user_id: int) -> list[Document]:
        stmt = select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_document_with_chunks(self, document_id: int) -> Document | None:
        stmt = (
            select(Document)
            .where(Document.id == document_id)
            .options(selectinload(Document.chunks))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


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
        # Use bulk delete for better performance
        from sqlalchemy import delete
        stmt = delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
        await self.session.execute(stmt)
        await self.session.flush()
