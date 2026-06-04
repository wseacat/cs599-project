import pytest
from httpx import AsyncClient


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict:
    await client.post("/api/auth/register", json={
        "username": "doctest",
        "email": "doc@example.com",
        "password": "password123"
    })
    login_response = await client.post("/api/auth/login", json={
        "username": "doctest",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_documents_empty(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/documents/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["documents"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_upload_document(client: AsyncClient, auth_headers: dict):
    files = {"file": ("test.txt", b"Hello World", "text/plain")}
    response = await client.post("/api/documents/upload", files=files, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["file_type"] == "txt"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_upload_unsupported_type(client: AsyncClient, auth_headers: dict):
    files = {"file": ("test.exe", b"binary", "application/octet-stream")}
    response = await client.post("/api/documents/upload", files=files, headers=auth_headers)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_list_documents_after_upload(client: AsyncClient, auth_headers: dict):
    files = {"file": ("test.txt", b"Hello World", "text/plain")}
    await client.post("/api/documents/upload", files=files, headers=auth_headers)

    response = await client.get("/api/documents/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["documents"][0]["filename"] == "test.txt"


@pytest.mark.asyncio
async def test_delete_document(client: AsyncClient, auth_headers: dict):
    files = {"file": ("test.txt", b"Hello World", "text/plain")}
    upload_response = await client.post("/api/documents/upload", files=files, headers=auth_headers)
    doc_id = upload_response.json()["id"]

    response = await client.delete(f"/api/documents/{doc_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_delete_nonexistent_document(client: AsyncClient, auth_headers: dict):
    response = await client.delete("/api/documents/99999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_upload_unauthorized(client: AsyncClient):
    files = {"file": ("test.txt", b"Hello World", "text/plain")}
    response = await client.post("/api/documents/upload", files=files)
    assert response.status_code == 401
