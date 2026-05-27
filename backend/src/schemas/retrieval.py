from pydantic import BaseModel


class RetrievalDebugResponse(BaseModel):
    query: str
    plan: str | None = None
    original_query: str | None = None
    rewritten_query: str | None = None
    expanded_queries: list[str] = []
    retrieved_documents: list[dict] = []
    reranked_documents: list[dict] = []
    reflection_result: str | None = None
    retry_count: int = 0


class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    collection: str | None = None


class SearchResponse(BaseModel):
    results: list[dict]
    query: str
    total: int
