from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool

from app.api.schemas import DocumentUploadResponse
from app.config import get_settings
from app.rag.loader import SUPPORTED_SUFFIXES
from app.rag.retriever import RAGService, get_rag_service


router = APIRouter(tags=["knowledge"])
MAX_UPLOAD_BYTES = 20 * 1024 * 1024


def rag_service_dependency() -> RAGService:
    return get_rag_service()


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    service: RAGService = Depends(rag_service_dependency),
) -> DocumentUploadResponse:
    original_name = Path(file.filename or "").name
    suffix = Path(original_name).suffix.lower()
    if not original_name or suffix not in SUPPORTED_SUFFIXES:
        supported = ", ".join(sorted(SUPPORTED_SUFFIXES))
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Supported document types: {supported}",
        )

    payload = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(payload) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Document exceeds the 20 MB upload limit.",
        )

    settings = get_settings()
    directory = settings.documents_directory
    directory.mkdir(parents=True, exist_ok=True)
    stored_path = directory / f"{uuid4().hex}_{original_name}"
    await run_in_threadpool(stored_path.write_bytes, payload)

    try:
        result = await run_in_threadpool(service.ingest, stored_path)
    except Exception:
        stored_path.unlink(missing_ok=True)
        raise
    return DocumentUploadResponse(**result)


@router.get("/documents/stats")
async def document_stats(
    service: RAGService = Depends(rag_service_dependency),
) -> dict:
    return await run_in_threadpool(service.stats)

