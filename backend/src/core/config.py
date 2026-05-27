from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # LLM
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    LLM_MODEL: str = "qwen-plus"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 4096

    # Embedding
    EMBEDDING_MODEL: str = "BAAI/bge-large-zh-v1.5"
    EMBEDDING_DEVICE: str = "cpu"
    EMBEDDING_DIM: int = 1024

    # Reranker
    RERANKER_MODEL: str = "BAAI/bge-reranker-large"
    RERANKER_DEVICE: str = "cpu"

    # Milvus
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION: str = "enterprise_rag"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    REDIS_TTL: int = 1800

    # Database
    DATABASE_URL: str = ""

    # Retrieval
    RETRIEVAL_TOP_K: int = 10
    RERANK_TOP_K: int = 5
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    MAX_RETRY_COUNT: int = 2

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # LangSmith
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "enterprise-rag"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"

    @computed_field
    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @computed_field
    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    if not s.DATABASE_URL:
        raise ValueError("DATABASE_URL is required. Set it in .env or environment variables.")
    if not s.SECRET_KEY:
        raise ValueError("SECRET_KEY is required. Set it in .env or environment variables.")
    if not s.LLM_API_KEY:
        raise ValueError("LLM_API_KEY is required. Set it in .env or environment variables.")
    return s
