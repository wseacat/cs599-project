import json

import redis.asyncio as aioredis
import structlog

from src.core.config import get_settings

logger = structlog.get_logger()

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        settings = get_settings()
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True, max_connections=20)
    return _redis


async def save_message(conversation_id: int, role: str, content: str) -> None:
    try:
        redis = await get_redis()
        key = f"session:{conversation_id}:history"
        msg = json.dumps({"role": role, "content": content}, ensure_ascii=False)
        await redis.rpush(key, msg)
        settings = get_settings()
        await redis.expire(key, settings.REDIS_TTL)
    except Exception:
        logger.warning("redis_save_message_failed", conversation_id=conversation_id)


async def get_history(conversation_id: int, limit: int = 20) -> list[dict]:
    try:
        redis = await get_redis()
        key = f"session:{conversation_id}:history"
        messages = await redis.lrange(key, -limit, -1)
        return [json.loads(m) for m in messages]
    except Exception:
        logger.warning("redis_get_history_failed", conversation_id=conversation_id)
        return []


async def clear_history(conversation_id: int) -> None:
    try:
        redis = await get_redis()
        key = f"session:{conversation_id}:history"
        await redis.delete(key)
    except Exception:
        logger.warning("redis_clear_history_failed", conversation_id=conversation_id)


async def cache_retrieval(query_hash: str, results: list[dict], ttl: int = 3600) -> None:
    try:
        redis = await get_redis()
        key = f"retrieval:{query_hash}"
        await redis.setex(key, ttl, json.dumps(results, ensure_ascii=False))
    except Exception:
        logger.warning("redis_cache_retrieval_failed", query_hash=query_hash)


async def get_cached_retrieval(query_hash: str) -> list[dict] | None:
    try:
        redis = await get_redis()
        key = f"retrieval:{query_hash}"
        data = await redis.get(key)
        if data:
            return json.loads(data)
    except Exception:
        logger.warning("redis_get_cached_retrieval_failed", query_hash=query_hash)
    return None


async def disconnect_redis() -> None:
    global _redis
    if _redis:
        await _redis.close()
        _redis = None
        logger.info("redis_disconnected")
