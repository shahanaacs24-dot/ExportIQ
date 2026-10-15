"""
ExportIQ — Document processing pipeline.
Extracts text from PDF/images, applies OCR if needed, extracts structured fields,
and updates the database document record.
"""
import logging
import os
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.document import Document, DocumentStatus
from app.services.document.pdf_extractor import extract_text_from_pdf
from app.services.document.ocr_extractor import extract_text_from_image
from app.services.document.field_extractor import extract_fields_from_text

logger = logging.getLogger(__name__)


def process_document_background(document_id: int) -> None:
    """
    Process an uploaded document:
    1. Check file type (PDF vs image).
    2. Extract text (PDF text extraction or OCR).
    3. Extract structured fields via regex/rules.
    4. Save extracted text and fields to DB and mark as PROCESSED.
    """
    db: Session = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            logger.error(f"Document {document_id} not found for processing")
            return

        doc.status = DocumentStatus.PROCESSING
        db.commit()

        file_path = doc.file_path
        mime_type = doc.mime_type.lower()
        extracted_text = ""
        ocr_used = False

        if "pdf" in mime_type or file_path.lower().endswith(".pdf"):
            extracted_text, is_scanned = extract_text_from_pdf(file_path)
            if is_scanned or not extracted_text:
                # Try OCR fallback
                ocr_text = extract_text_from_image(file_path)
                if ocr_text:
                    extracted_text = ocr_text
                    ocr_used = True
        elif any(img_ext in mime_type or file_path.lower().endswith(img_ext) for img_ext in ["image", "png", "jpg", "jpeg", "tiff"]):
            extracted_text = extract_text_from_image(file_path)
            ocr_used = True
        else:
            # Fallback for text files or unknown types
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    extracted_text = f.read()
            except Exception:
                extracted_text = ""

        # Extract structured fields
        fields = extract_fields_from_text(extracted_text, doc.document_type.value)

        doc.extracted_text = extracted_text[:10000] if extracted_text else None  # cap size
        doc.extracted_fields = fields if fields else None
        doc.ocr_used = ocr_used
        doc.status = DocumentStatus.PROCESSED
        doc.processing_error = None
        db.commit()
        logger.info(f"Successfully processed document {doc.id} ({doc.original_filename}) | ocr={ocr_used}")

    except Exception as e:
        logger.exception(f"Error processing document {document_id}: {e}")
        try:
            doc = db.query(Document).filter(Document.id == document_id).first()
            if doc:
                doc.status = DocumentStatus.FAILED
                doc.processing_error = str(e)
                db.commit()
        except Exception:
            pass
    finally:
        db.close()
