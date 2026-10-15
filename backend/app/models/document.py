"""
ExportIQ — Document model.
Tracks uploaded files, their processing status, and extracted fields.
"""
from datetime import datetime
import enum

from sqlalchemy import (
    Boolean, DateTime, Enum, ForeignKey, Integer, JSON, String, Text, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _enum_values(e):
    return [m.value for m in e]


class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class DocumentType(str, enum.Enum):
    # Identity / Registration
    IEC_CERTIFICATE = "iec_certificate"
    GSTIN_CERTIFICATE = "gstin_certificate"
    UDYAM_CERTIFICATE = "udyam_certificate"
    PAN_CARD = "pan_card"
    COI = "certificate_of_incorporation"
    # Product / Quality
    BIS_CERTIFICATE = "bis_certificate"
    FSSAI_LICENSE = "fssai_license"
    APEDA_CERTIFICATE = "apeda_certificate"
    QUALITY_CERTIFICATE = "quality_certificate"
    TEST_REPORT = "test_report"
    # Trade
    INVOICE = "invoice"
    PACKING_LIST = "packing_list"
    SHIPPING_BILL = "shipping_bill"
    BILL_OF_LADING = "bill_of_lading"
    CERTIFICATE_OF_ORIGIN = "certificate_of_origin"
    PHYTOSANITARY_CERTIFICATE = "phytosanitary_certificate"
    HEALTH_CERTIFICATE = "health_certificate"
    # Other
    OTHER = "other"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assessment_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("assessments.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # ── File metadata ─────────────────────────────────────────
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # ── Classification ────────────────────────────────────────
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType, values_callable=_enum_values, name="documenttype"),
        default=DocumentType.OTHER, nullable=False
    )

    # ── Processing ────────────────────────────────────────────
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, values_callable=_enum_values, name="documentstatus"),
        default=DocumentStatus.UPLOADED, nullable=False
    )
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_fields: Mapped[dict | None] = mapped_column(
        JSON, nullable=True,
        comment="Structured fields extracted via NLP/rules from document text"
    )
    ocr_used: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
        comment="True if OCR was applied (scanned document)"
    )
    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Timestamps ────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # ── Relationships ─────────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="documents")
    assessment: Mapped["Assessment | None"] = relationship("Assessment", back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document id={self.id} type={self.document_type} status={self.status}>"
