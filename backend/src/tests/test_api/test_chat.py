import pytest
from httpx import AsyncClient


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict:
    await client.post("/api/auth/register", json={
        "username": "chattest",
        "email": "chat@example.com",
        "password": "password123"
    })
    login_response = await client.post("/api/auth/login", json={
        "username": "chattest",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_chat_unauthorized(client: AsyncClient):
    response = await client.post("/api/chat", json={"message": "Hello"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_conversations_empty(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/conversations/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_conversations_unauthorized(client: AsyncClient):
    response = await client.get("/api/conversations/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_nonexistent_conversation(client: AsyncClient, auth_headers: dict):
    response = await client.delete("/api/conversations/99999", headers=auth_headers)
    assert response.status_code == 404
