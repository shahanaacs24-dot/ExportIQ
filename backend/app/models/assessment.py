"""
ExportIQ — Assessment and AssessmentRequirement models.
An Assessment captures a point-in-time readiness check for one user,
product, and destination country combination.
"""
from datetime import datetime
import enum

from sqlalchemy import (
    DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _enum_values(e):
    return [m.value for m in e]


class AssessmentStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ComplianceStatus(str, enum.Enum):
    """Per-requirement compliance verdict."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    INCOMPLETE = "incomplete"
    EXPIRED = "expired"
    UNVERIFIED = "unverified"
    MISSING = "missing"
    NOT_APPLICABLE = "not_applicable"


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False
    )
    destination_country_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("destination_countries.id"), nullable=False
    )

    status: Mapped[AssessmentStatus] = mapped_column(
        Enum(AssessmentStatus, values_callable=_enum_values, name="assessmentstatus"),
        default=AssessmentStatus.DRAFT, nullable=False
    )

    eri_score: Mapped[float | None] = mapped_column(
        Float, nullable=True,
        comment="Export Readiness Index 0-100; null until assessment is completed"
    )
    category_scores: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    score_breakdown: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    total_requirements: Mapped[int | None] = mapped_column(Integer, nullable=True)
    compliant_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    missing_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    incomplete_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expired_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user_responses: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="assessments")
    product: Mapped["Product"] = relationship("Product", back_populates="assessments")
    destination_country: Mapped["DestinationCountry"] = relationship(
        "DestinationCountry", back_populates="assessments"
    )
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="assessment")
    requirement_results: Mapped[list["AssessmentRequirement"]] = relationship(
        "AssessmentRequirement", back_populates="assessment", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Assessment id={self.id} status={self.status} eri={self.eri_score}>"


class AssessmentRequirement(Base):
    """Junction table: per-requirement compliance result within an assessment."""
    __tablename__ = "assessment_requirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    assessment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    requirement_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("requirements.id"), nullable=False
    )

    status: Mapped[ComplianceStatus] = mapped_column(
        Enum(ComplianceStatus, values_callable=_enum_values, name="compliancestatus"),
        nullable=False, default=ComplianceStatus.MISSING
    )
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_document_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    matched_fields: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    points_earned: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    points_possible: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="requirement_results")
    requirement: Mapped["Requirement"] = relationship("Requirement", back_populates="assessment_requirements")

    def __repr__(self) -> str:
        return f"<AssessmentRequirement aid={self.assessment_id} rid={self.requirement_id} status={self.status}>"
