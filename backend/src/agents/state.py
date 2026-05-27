from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class RetrievalDocument(TypedDict):
    chunk_id: int
    document_id: int
    content: str
    score: float
    source: str
    metadata: dict | None


class CitationInfo(TypedDict):
    document_id: int
    chunk_id: int
    filename: str | None
    page: int | None
    snippet: str | None


class RAGState(TypedDict):
    original_query: str
    rewritten_query: str
    expanded_queries: list[str]
    retrieval_plan: str
    retrieved_documents: list[RetrievalDocument]
    reranked_documents: list[RetrievalDocument]
    reflection_result: str
    reflection_passed: bool
    retry_count: int
    final_answer: str
    citations: list[CitationInfo]
    chat_history: Annotated[list, add_messages]
    conversation_id: int | None
    message_id: int | None
    workflow_trace: list[dict]
