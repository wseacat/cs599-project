from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

from src.core.config import get_settings
from src.retrieval.embeddings import embed_query, embed_documents

import structlog

logger = structlog.get_logger()

_collection: Collection | None = None


def connect_milvus(timeout: float = 3.0) -> None:
    settings = get_settings()
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((settings.MILVUS_HOST, int(settings.MILVUS_PORT)))
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        logger.warning("milvus_not_reachable", host=settings.MILVUS_HOST, port=settings.MILVUS_PORT, error=str(e))
        return
    finally:
        sock.close()
    connections.connect("default", host=settings.MILVUS_HOST, port=settings.MILVUS_PORT)
    logger.info("milvus_connected", host=settings.MILVUS_HOST, port=settings.MILVUS_PORT)


def ensure_collection() -> Collection:
    global _collection
    if _collection is not None:
        return _collection

    settings = get_settings()
    collection_name = settings.MILVUS_COLLECTION

    if not utility.has_collection(collection_name):
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="chunk_id", dtype=DataType.INT64),
            FieldSchema(name="document_id", dtype=DataType.INT64),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=8192),
            FieldSchema(name="metadata_json", dtype=DataType.VARCHAR, max_length=2048),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=settings.EMBEDDING_DIM),
        ]
        schema = CollectionSchema(fields, description="Enterprise RAG document chunks")
        collection = Collection(collection_name, schema)
        index_params = {"index_type": "IVF_FLAT", "metric_type": "COSINE", "params": {"nlist": 1024}}
        collection.create_index("embedding", index_params)
        logger.info("milvus_collection_created", name=collection_name)
    else:
        collection = Collection(collection_name)

    collection.load()
    _collection = collection
    return collection


async def insert_chunks(chunk_ids: list[int], document_ids: list[int], contents: list[str], metadatas: list[str]) -> list[int]:
    collection = ensure_collection()
    embeddings = await embed_documents(contents)
    data = [chunk_ids, document_ids, contents, metadatas, embeddings]
    result = collection.insert(data)
    collection.flush()
    logger.info("milvus_insert", count=len(chunk_ids))
    return result.primary_keys


async def search_similar(query: str, top_k: int = 10, score_threshold: float = 0.0) -> list[dict]:
    collection = ensure_collection()
    query_embedding = await embed_query(query)
    search_params = {"metric_type": "COSINE", "params": {"nprobe": 16}}
    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        output_fields=["chunk_id", "document_id", "content", "metadata_json"],
    )
    hits = []
    for hit in results[0]:
        if hit.score >= score_threshold:
            hits.append({
                "chunk_id": hit.entity.get("chunk_id"),
                "document_id": hit.entity.get("document_id"),
                "content": hit.entity.get("content"),
                "metadata_json": hit.entity.get("metadata_json"),
                "score": hit.score,
                "source": "vector",
            })
    return hits


def disconnect_milvus() -> None:
    connections.disconnect("default")
    logger.info("milvus_disconnected")
