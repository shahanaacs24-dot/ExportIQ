"""ExportIQ — Document schemas."""
from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel
from app.models.document import DocumentStatus, DocumentType


class DocumentRead(BaseModel):
    id: int
    user_id: int
    assessment_id: Optional[int] = None
    original_filename: str
    file_size_bytes: int
    mime_type: str
    document_type: DocumentType
    status: DocumentStatus
    extracted_fields: Optional[Any] = None
    ocr_used: bool
    processing_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
