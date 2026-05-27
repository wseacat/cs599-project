from datetime import datetime

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None


class CitationResponse(BaseModel):
    document_id: int
    chunk_id: int
    filename: str | None = None
    page: int | None = None
    snippet: str | None = None


class ChatResponse(BaseModel):
    answer: str
    conversation_id: int
    message_id: int
    citations: list[CitationResponse]
    workflow_trace: list[dict] | None = None


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    citations_json: str | None = None
    created_at: datetime


class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class ConversationDetailResponse(BaseModel):
    id: int
    title: str
    messages: list[MessageResponse]
