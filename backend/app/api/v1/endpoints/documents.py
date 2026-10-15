"""ExportIQ — Document upload and retrieval endpoints."""
import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.document import Document, DocumentType
from app.models.user import User
from app.schemas.document import DocumentRead
from app.services.document.processor import process_document_background

router = APIRouter()
settings = get_settings()


@router.post("", response_model=DocumentRead, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(DocumentType.OTHER),
    assessment_id: int | None = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Upload a document and trigger background processing."""
    # Validate extension
    ext = os.path.splitext(file.filename or "")[1].lower().lstrip(".")
    if ext not in settings.allowed_extensions_set:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Allowed: {settings.allowed_extensions}"
        )

    # Read and validate size
    contents = await file.read()
    if len(contents) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum size of {settings.max_upload_size_mb} MB"
        )

    # Store file
    os.makedirs(settings.upload_dir, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(settings.upload_dir, stored_name)
    with open(file_path, "wb") as f:
        f.write(contents)

    doc = Document(
        user_id=current_user.id,
        assessment_id=assessment_id,
        original_filename=file.filename or stored_name,
        stored_filename=stored_name,
        file_path=file_path,
        file_size_bytes=len(contents),
        mime_type=file.content_type or "application/octet-stream",
        document_type=document_type,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Trigger processing (synchronous for now; async worker in Phase 3)
    process_document_background(doc.id)

    return doc


@router.get("", response_model=List[DocumentRead])
def list_documents(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )


@router.get("/{doc_id}", response_model=DocumentRead)
def get_document(
    doc_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    doc = db.query(Document).filter(
        Document.id == doc_id, Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{doc_id}", status_code=204)
def delete_document(
    doc_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    doc = db.query(Document).filter(
        Document.id == doc_id, Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    # Remove file from disk if it exists
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    db.delete(doc)
    db.commit()
