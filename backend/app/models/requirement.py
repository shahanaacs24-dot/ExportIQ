"""
ExportIQ — Requirement model.
Knowledge base: requirements applicable to product-country combinations.
Each row is one verifiable export requirement with source and applicability metadata.
"""
from datetime import date, datetime
import enum

from sqlalchemy import (
    Boolean, Date, DateTime, Enum, Integer, JSON,
    String, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _enum_values(e):
    return [m.value for m in e]


class RequirementCategory(str, enum.Enum):
    """High-level categories used in ERI scoring."""
    LEGAL_REGISTRATION = "legal_registration"
    PRODUCT_QUALITY = "product_quality"
    TRADE_DOCUMENTATION = "trade_documentation"
    PHYTOSANITARY = "phytosanitary"
    LABELLING = "labelling"
    PACKAGING = "packaging"
    FINANCIAL = "financial"
    LOGISTICS = "logistics"


class RequirementStatus(str, enum.Enum):
    """Knowledge-base verification status (not user compliance status)."""
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    DEPRECATED = "deprecated"


class Requirement(Base):
    __tablename__ = "requirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # ── Identity ──────────────────────────────────────────────
    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True,
        comment="Internal code e.g. IND-IEC-001"
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[RequirementCategory] = mapped_column(
        Enum(RequirementCategory, values_callable=_enum_values, name="requirementcategory"),
        nullable=False, index=True
    )

    # ── Applicability conditions ──────────────────────────────
    applicable_hs_codes: Mapped[list | None] = mapped_column(
        JSON, nullable=True,
        comment="HS code prefixes this requirement applies to; null = all"
    )
    applicable_country_iso: Mapped[list | None] = mapped_column(
        JSON, nullable=True,
        comment="ISO-3 codes of destination countries; null = all"
    )
    applicable_product_categories: Mapped[list | None] = mapped_column(
        JSON, nullable=True,
        comment="Product category strings; null = all"
    )
    conditions: Mapped[dict | None] = mapped_column(
        JSON, nullable=True,
        comment="Extra applicability conditions as key-value pairs"
    )

    # ── Evidence ──────────────────────────────────────────────
    required_document_types: Mapped[list] = mapped_column(
        JSON, nullable=False, default=list,
        comment="DocumentType enum values that provide evidence"
    )
    evidence_fields: Mapped[list | None] = mapped_column(
        JSON, nullable=True,
        comment="Specific extracted fields required in the document"
    )

    # ── Scoring ───────────────────────────────────────────────
    weight: Mapped[float] = mapped_column(
        Integer, nullable=False, default=1,
        comment="Relative importance weight for ERI calculation"
    )
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ── Source metadata ───────────────────────────────────────
    issuing_authority: Mapped[str | None] = mapped_column(String(300), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    source_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    kb_status: Mapped[RequirementStatus] = mapped_column(
        Enum(RequirementStatus, values_callable=_enum_values, name="requirementstatus"),
        default=RequirementStatus.UNVERIFIED, nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Lifecycle ─────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # ── Relationships ─────────────────────────────────────────
    assessment_requirements: Mapped[list["AssessmentRequirement"]] = relationship(
        "AssessmentRequirement", back_populates="requirement"
    )

    def __repr__(self) -> str:
        return f"<Requirement code={self.code!r} name={self.name!r}>"
