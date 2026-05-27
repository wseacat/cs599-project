import json

import structlog

from src.retrieval.chunker import chunk_text
from src.retrieval.vector_store import insert_chunks

logger = structlog.get_logger()


async def process_document(document_id: int, content: str, filename: str, session=None) -> dict:
    chunks = chunk_text(content, metadata={"filename": filename, "document_id": document_id})

    if not chunks:
        return {"chunk_count": 0, "status": "empty"}

    # Save chunks to PostgreSQL if session provided
    chunk_db_ids = []
    if session is not None:
        from src.models.document import DocumentChunk
        for i, chunk in enumerate(chunks):
            db_chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=i,
                content=chunk["content"],
                metadata_json=json.dumps(chunk["metadata"], ensure_ascii=False),
            )
            session.add(db_chunk)
        await session.flush()

        # Reload to get the auto-generated IDs
        from sqlalchemy import select
        result = await session.execute(
            select(DocumentChunk.id)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
        )
        chunk_db_ids = [row[0] for row in result.all()]
    else:
        # Fallback: generate unique IDs from document_id + index
        chunk_db_ids = [document_id * 100000 + i for i in range(len(chunks))]

    document_ids = [document_id] * len(chunks)
    contents = [c["content"] for c in chunks]
    metadatas = [json.dumps(c["metadata"], ensure_ascii=False) for c in chunks]

    try:
        await insert_chunks(chunk_db_ids, document_ids, contents, metadatas)
    except Exception as e:
        logger.warning("milvus_insert_failed", error=str(e))

    # Add to BM25 index
    from src.retrieval.bm25 import get_bm25_index
    bm25 = get_bm25_index()
    bm25.add_documents(contents, chunk_db_ids)

    logger.info("document_processed", document_id=document_id, chunk_count=len(chunks))
    return {"chunk_count": len(chunks), "status": "completed"}
