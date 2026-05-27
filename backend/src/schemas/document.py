from datetime import datetime

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    status: str
    chunk_count: int
    created_at: datetime


class DocumentListResponse(BaseModel):
    documents: list[DocumentUploadResponse]
    total: int


class DocumentChunkResponse(BaseModel):
    id: int
    chunk_index: int
    content: str
    metadata_json: str | None
