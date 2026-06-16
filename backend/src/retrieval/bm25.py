import jieba
from rank_bm25 import BM25Okapi

import structlog

logger = structlog.get_logger()


class BM25Index:
    def __init__(self) -> None:
        self._corpus: list[str] = []
        self._tokenized: list[list[str]] = []
        self._bm25: BM25Okapi | None = None
        self._chunk_ids: list[int] = []
        self._document_ids: list[int] = []
        self._user_ids: list[int] = []
        self._metadatas: list[str] = []

    def build(self, documents: list[str], chunk_ids: list[int], document_ids: list[int] | None = None, metadatas: list[str] | None = None, user_ids: list[int] | None = None) -> None:
        self._corpus = documents
        self._chunk_ids = chunk_ids
        self._document_ids = document_ids or [0] * len(chunk_ids)
        self._user_ids = user_ids or [0] * len(chunk_ids)
        self._metadatas = metadatas or ["{}"] * len(chunk_ids)
        self._tokenized = [list(jieba.cut(doc)) for doc in documents]
        self._bm25 = BM25Okapi(self._tokenized)
        logger.info("bm25_index_built", doc_count=len(documents))

    def add_documents(self, documents: list[str], chunk_ids: list[int], document_ids: list[int] | None = None, metadatas: list[str] | None = None, user_ids: list[int] | None = None) -> None:
        self._corpus.extend(documents)
        self._chunk_ids.extend(chunk_ids)
        self._document_ids.extend(document_ids or [0] * len(chunk_ids))
        self._user_ids.extend(user_ids or [0] * len(chunk_ids))
        self._metadatas.extend(metadatas or ["{}"] * len(chunk_ids))
        self._tokenized.extend([list(jieba.cut(doc)) for doc in documents])
        self._bm25 = BM25Okapi(self._tokenized)
        logger.info("bm25_documents_added", added=len(documents), total=len(self._corpus))

    def remove_by_chunk_ids(self, chunk_ids_to_remove: set[int]) -> None:
        keep_indices = [i for i, cid in enumerate(self._chunk_ids) if cid not in chunk_ids_to_remove]
        if len(keep_indices) == len(self._chunk_ids):
            return
        self._corpus = [self._corpus[i] for i in keep_indices]
        self._chunk_ids = [self._chunk_ids[i] for i in keep_indices]
        self._document_ids = [self._document_ids[i] for i in keep_indices]
        self._user_ids = [self._user_ids[i] for i in keep_indices]
        self._metadatas = [self._metadatas[i] for i in keep_indices]
        self._tokenized = [self._tokenized[i] for i in keep_indices]
        self._bm25 = BM25Okapi(self._tokenized) if self._corpus else None
        logger.info("bm25_documents_removed", remaining=len(self._corpus))

    def search(self, query: str, top_k: int = 10, user_id: int | None = None) -> list[dict]:
        if self._bm25 is None or not self._corpus:
            return []

        query_tokens = list(jieba.cut(query))
        scores = self._bm25.get_scores(query_tokens)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in ranked:
            if score <= 0:
                continue
            # Filter by user_id if specified
            if user_id is not None and self._user_ids[idx] != user_id:
                continue
            results.append({
                "chunk_id": self._chunk_ids[idx],
                "document_id": self._document_ids[idx],
                "content": self._corpus[idx],
                "metadata_json": self._metadatas[idx],
                "score": float(score),
                "source": "bm25",
            })
            if len(results) >= top_k:
                break
        return results


_bm25_index: BM25Index | None = None


def get_bm25_index() -> BM25Index:
    global _bm25_index
    if _bm25_index is None:
        _bm25_index = BM25Index()
    return _bm25_index


async def rebuild_bm25_from_db() -> None:
    """Load all document chunks from DB and rebuild the BM25 index."""
    from sqlalchemy import select
    from src.core.deps import async_session_factory
    from src.models.document import DocumentChunk, Document

    async with async_session_factory() as session:
        result = await session.execute(
            select(DocumentChunk.id, DocumentChunk.document_id, DocumentChunk.content, DocumentChunk.metadata_json, Document.user_id)
            .join(Document, DocumentChunk.document_id == Document.id)
        )
        rows = result.all()

    if not rows:
        logger.info("bm25_rebuild_skipped", reason="no chunks in db")
        return

    chunk_ids = [r[0] for r in rows]
    document_ids = [r[1] for r in rows]
    contents = [r[2] for r in rows]
    metadatas = [r[3] or "{}" for r in rows]
    user_ids = [r[4] for r in rows]

    index = get_bm25_index()
    index.build(contents, chunk_ids, document_ids, metadatas, user_ids)
    logger.info("bm25_rebuild_complete", chunk_count=len(chunk_ids))
