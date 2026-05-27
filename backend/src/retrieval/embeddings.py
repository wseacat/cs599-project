import asyncio

from sentence_transformers import SentenceTransformer
import structlog

from src.core.config import get_settings

logger = structlog.get_logger()

_embedding_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        settings = get_settings()
        logger.info("loading_embedding_model", model=settings.EMBEDDING_MODEL, device=settings.EMBEDDING_DEVICE)
        _embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL, device=settings.EMBEDDING_DEVICE)
    return _embedding_model


async def embed_documents(texts: list[str], batch_size: int = 32) -> list[list[float]]:
    model = get_embedding_model()
    embeddings = await asyncio.to_thread(
        lambda: model.encode(texts, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=False)
    )
    return embeddings.tolist()


async def embed_query(text: str) -> list[float]:
    model = get_embedding_model()
    embedding = await asyncio.to_thread(
        lambda: model.encode([text], normalize_embeddings=True)
    )
    return embedding[0].tolist()
