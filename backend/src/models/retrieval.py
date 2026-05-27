from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin


class RetrievalLog(Base, TimestampMixin):
    __tablename__ = "retrieval_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"), nullable=False, index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    retrieved_docs: Mapped[str | None] = mapped_column(Text, nullable=True)
    reranked_docs: Mapped[str | None] = mapped_column(Text, nullable=True)
    reflection_result: Mapped[str | None] = mapped_column(Text, nullable=True)

    message = relationship("Message", back_populates="retrieval_logs")


class Citation(Base, TimestampMixin):
    __tablename__ = "citations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"), nullable=False, index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False)
    chunk_id: Mapped[int] = mapped_column(ForeignKey("document_chunks.id"), nullable=False)
    page: Mapped[int | None] = mapped_column(nullable=True)
    snippet: Mapped[str | None] = mapped_column(Text, nullable=True)

    message = relationship("Message", back_populates="citations")
