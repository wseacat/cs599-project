from datetime import datetime

from src.schemas.document import DocumentUploadResponse, DocumentListResponse, DocumentChunkResponse


def test_document_upload_response():
    now = datetime.now()
    response = DocumentUploadResponse(
        id=1,
        filename="test.pdf",
        file_type="pdf",
        status="pending",
        chunk_count=0,
        created_at=now,
    )
    assert response.id == 1
    assert response.filename == "test.pdf"
    assert response.file_type == "pdf"
    assert response.status == "pending"
    assert response.chunk_count == 0


def test_document_list_response():
    now = datetime.now()
    doc = DocumentUploadResponse(
        id=1,
        filename="test.pdf",
        file_type="pdf",
        status="completed",
        chunk_count=10,
        created_at=now,
    )
    response = DocumentListResponse(documents=[doc], total=1)
    assert len(response.documents) == 1
    assert response.total == 1


def test_document_chunk_response():
    response = DocumentChunkResponse(
        id=1,
        chunk_index=0,
        content="Hello World",
        metadata_json='{"filename": "test.pdf"}',
    )
    assert response.id == 1
    assert response.chunk_index == 0
    assert response.content == "Hello World"
    assert response.metadata_json == '{"filename": "test.pdf"}'
