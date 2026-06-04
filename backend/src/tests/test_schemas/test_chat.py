from datetime import datetime

from src.schemas.chat import (
    ChatRequest,
    ChatResponse,
    CitationResponse,
    MessageResponse,
    ConversationResponse,
    ConversationDetailResponse,
)


def test_chat_request():
    request = ChatRequest(message="Hello", conversation_id=1)
    assert request.message == "Hello"
    assert request.conversation_id == 1


def test_chat_request_no_conversation():
    request = ChatRequest(message="Hello")
    assert request.message == "Hello"
    assert request.conversation_id is None


def test_citation_response():
    citation = CitationResponse(
        document_id=1,
        chunk_id=2,
        filename="test.pdf",
        page=1,
        snippet="Hello World",
    )
    assert citation.document_id == 1
    assert citation.chunk_id == 2
    assert citation.filename == "test.pdf"


def test_chat_response():
    response = ChatResponse(
        answer="Hello",
        conversation_id=1,
        message_id=2,
        citations=[],
        workflow_trace=[],
    )
    assert response.answer == "Hello"
    assert response.conversation_id == 1
    assert response.message_id == 2


def test_message_response():
    now = datetime.now()
    response = MessageResponse(
        id=1,
        role="user",
        content="Hello",
        citations_json=None,
        created_at=now,
    )
    assert response.id == 1
    assert response.role == "user"
    assert response.content == "Hello"


def test_conversation_response():
    now = datetime.now()
    response = ConversationResponse(
        id=1,
        title="Test",
        created_at=now,
        updated_at=now,
        message_count=5,
    )
    assert response.id == 1
    assert response.title == "Test"
    assert response.message_count == 5


def test_conversation_detail_response():
    now = datetime.now()
    message = MessageResponse(
        id=1,
        role="user",
        content="Hello",
        created_at=now,
    )
    response = ConversationDetailResponse(
        id=1,
        title="Test",
        messages=[message],
    )
    assert response.id == 1
    assert len(response.messages) == 1
