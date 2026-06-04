from fastapi import APIRouter

import structlog

logger = structlog.get_logger()

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint with service status."""
    from src.core.config import get_settings
    settings = get_settings()

    # Check services
    services = {}

    # Check Redis
    try:
        from src.memory.conversation_memory import get_redis
        redis = await get_redis()
        await redis.ping()
        services["redis"] = "connected"
    except Exception as e:
        services["redis"] = f"error: {str(e)}"

    # Check Milvus
    try:
        from src.retrieval.vector_store import ensure_collection
        ensure_collection()
        services["milvus"] = "connected"
    except Exception as e:
        services["milvus"] = f"error: {str(e)}"

    return {
        "status": "ok",
        "service": "enterprise-rag",
        "version": "0.1.0",
        "environment": settings.APP_ENV,
        "services": services,
    }
