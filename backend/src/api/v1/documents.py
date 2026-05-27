from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user
from src.core.deps import get_db
from src.models.user import User
from src.repositories.document_repo import DocumentRepository
from src.schemas.document import DocumentChunkResponse, DocumentListResponse, DocumentUploadResponse
from src.services.document_service import delete_document, process_document_upload, upload_document

router = APIRouter(prefix="/documents", tags=["documents"])


async def _get_owned_document(db: AsyncSession, document_id: int, user_id: int):
    repo = DocumentRepository(db)
    doc = await repo.get(document_id)
    if not doc or doc.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    import structlog
    logger = structlog.get_logger()
    try:
        content = await file.read()
        doc = await upload_document(db, user_id=current_user.id, filename=file.filename or "unknown", file_content=content)
        return DocumentUploadResponse(
            id=doc.id, filename=doc.filename, file_type=doc.file_type,
            status=doc.status, chunk_count=doc.chunk_count, created_at=doc.created_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("upload_failed", error=str(e), type=type(e).__name__)
        raise HTTPException(status_code=500, detail="Upload failed")


@router.post("/{document_id}/process")
async def process_doc(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _get_owned_document(db, document_id, current_user.id)
    result = await process_document_upload(db, document_id)
    return result


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = DocumentRepository(db)
    docs = await repo.get_user_documents(user_id=current_user.id)
    return DocumentListResponse(
        documents=[
            DocumentUploadResponse(
                id=d.id, filename=d.filename, file_type=d.file_type,
                status=d.status, chunk_count=d.chunk_count, created_at=d.created_at,
            )
            for d in docs
        ],
        total=len(docs),
    )


@router.get("/{document_id}/chunks")
async def get_chunks(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _get_owned_document(db, document_id, current_user.id)
    from src.repositories.document_repo import DocumentChunkRepository
    repo = DocumentChunkRepository(db)
    chunks = await repo.get_document_chunks(document_id)
    return [DocumentChunkResponse(id=c.id, chunk_index=c.chunk_index, content=c.content, metadata_json=c.metadata_json) for c in chunks]


@router.delete("/{document_id}")
async def delete_doc(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _get_owned_document(db, document_id, current_user.id)
    success = await delete_document(db, document_id)
    return {"success": success}
