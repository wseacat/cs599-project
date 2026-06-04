from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.core.logging import setup_logging
from src.memory.conversation_memory import disconnect_redis
from src.retrieval.vector_store import connect_milvus, disconnect_milvus

import structlog

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.LOG_LEVEL, settings.LOG_FORMAT)

    logger.info("starting_application", env=settings.APP_ENV)
    try:
        connect_milvus()
    except Exception as e:
        logger.warning("milvus_connection_failed", error=str(e))

    # Rebuild BM25 index from persisted chunks
    try:
        from src.retrieval.bm25 import rebuild_bm25_from_db
        await rebuild_bm25_from_db()
    except Exception as e:
        logger.warning("bm25_rebuild_failed", error=str(e))

    # Pre-warm RAG models
    try:
        from src.workflows.rag_workflow import warmup_rag
        await warmup_rag()
        logger.info("rag_models_warmed_up")
    except Exception as e:
        logger.warning("rag_warmup_failed", error=str(e))

    yield

    logger.info("shutting_down_application")
    await disconnect_redis()
    try:
        disconnect_milvus()
    except Exception:
        pass


settings = get_settings()
app = FastAPI(
    title="Enterprise Agentic-RAG Knowledge Base",
    description="基于 LangGraph 的企业级 Agentic-RAG 智能知识库系统",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.api.v1.health import router as health_router
from src.api.v1.auth import router as auth_router
from src.api.v1.documents import router as documents_router
from src.api.v1.chat import router as chat_router
from src.api.v1.conversations import router as conversations_router
from src.api.v1.retrieval_debug import router as retrieval_router

app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(conversations_router, prefix="/api")
app.include_router(retrieval_router, prefix="/api")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    logger.error("unhandled_exception", path=str(request.url), method=request.method, error=str(exc), traceback=traceback.format_exc())
    from fastapi.responses import JSONResponse
    detail = str(exc) if settings.APP_ENV == "development" else "Internal server error"
    return JSONResponse(status_code=500, content={"detail": detail})


@app.exception_handler(404)
async def not_found_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=404, content={"detail": "Resource not found"})


@app.exception_handler(422)
async def validation_error_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=422, content={"detail": "Validation error", "errors": exc.errors() if hasattr(exc, 'errors') else str(exc)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=settings.APP_ENV == "development")
