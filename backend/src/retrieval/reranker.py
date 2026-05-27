import asyncio
import os

from src.core.config import get_settings

import structlog

logger = structlog.get_logger()

_reranker = None
_LOAD_TIMEOUT = 10  # seconds


def _is_model_cached(model_name: str) -> bool:
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
    model_dir = os.path.join(cache_dir, "models--" + model_name.replace("/", "--"))
    return os.path.isdir(model_dir) and any(
        f.endswith(".safetensors") or f.endswith(".bin")
        for f in os.listdir(model_dir) if os.path.isfile(os.path.join(model_dir, f))
    )


def _load_reranker():
    from FlagEmbedding import FlagReranker
    settings = get_settings()
    return FlagReranker(settings.RERANKER_MODEL, use_fp16=settings.RERANKER_DEVICE != "cpu")


async def get_reranker():
    global _reranker
    if _reranker is not None:
        return _reranker

    settings = get_settings()
    if not _is_model_cached(settings.RERANKER_MODEL):
        logger.warning("reranker_not_cached", model=settings.RERANKER_MODEL)
        return None

    try:
        logger.info("loading_reranker", model=settings.RERANKER_MODEL, device=settings.RERANKER_DEVICE)
        _reranker = await asyncio.wait_for(
            asyncio.to_thread(_load_reranker),
            timeout=_LOAD_TIMEOUT,
        )
        return _reranker
    except asyncio.TimeoutError:
        logger.warning("reranker_load_timeout", timeout=_LOAD_TIMEOUT)
        return None
    except Exception as e:
        logger.warning("reranker_load_failed", error=str(e))
        return None


async def rerank(query: str, documents: list[dict], top_k: int = 5) -> list[dict]:
    if not documents:
        return []

    reranker = await get_reranker()
    if reranker is None:
        logger.info("rerank_skipped", reason="model_unavailable", input_count=len(documents))
        return sorted(documents, key=lambda x: x.get("score", 0), reverse=True)[:top_k]

    try:
        pairs = [[query, doc.get("content", "")] for doc in documents]
        scores = await asyncio.wait_for(
            asyncio.to_thread(lambda: reranker.compute_score(pairs, normalize=True)),
            timeout=30,
        )
        if isinstance(scores, float):
            scores = [scores]

        for doc, score in zip(documents, scores):
            doc["rerank_score"] = score

        reranked = sorted(documents, key=lambda x: x.get("rerank_score", 0), reverse=True)[:top_k]
        logger.info("rerank_complete", input_count=len(documents), output_count=len(reranked))
        return reranked
    except asyncio.TimeoutError:
        logger.warning("rerank_timeout")
        return sorted(documents, key=lambda x: x.get("score", 0), reverse=True)[:top_k]
    except Exception as e:
        logger.warning("rerank_failed", error=str(e))
        return sorted(documents, key=lambda x: x.get("score", 0), reverse=True)[:top_k]
