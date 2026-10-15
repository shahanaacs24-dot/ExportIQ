"""
ExportIQ — MSME business profile model.
Stores organisation-level information tied to a User.
"""
from datetime import datetime
import enum

from sqlalchemy import (
    Boolean, DateTime, Enum, ForeignKey,
    Integer, Numeric, String, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _enum_values(e):
    """Return the .value strings for a Python enum — used by SQLAlchemy PG enums."""
    return [m.value for m in e]


class MSMECategory(str, enum.Enum):
    MICRO = "micro"
    SMALL = "small"
    MEDIUM = "medium"


class MSMEProfile(Base):
    __tablename__ = "msme_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    # ── Organisation details ──────────────────────────────────
    business_name: Mapped[str] = mapped_column(String(300), nullable=False)
    gstin: Mapped[str | None] = mapped_column(String(15), nullable=True, index=True)
    pan: Mapped[str | None] = mapped_column(String(10), nullable=True)
    iec_number: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="Import Export Code issued by DGFT"
    )
    udyam_number: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="Udyam Registration Number"
    )

    # ── Classification ────────────────────────────────────────
    category: Mapped[MSMECategory | None] = mapped_column(
        Enum(MSMECategory, values_callable=_enum_values, name="msmecategory"), nullable=True
    )
    industry_sector: Mapped[str | None] = mapped_column(String(200), nullable=True)
    year_established: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ── Contact ───────────────────────────────────────────────
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    website: Mapped[str | None] = mapped_column(String(300), nullable=True)

    # ── Export history ────────────────────────────────────────
    has_exported_before: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    export_experience_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    annual_turnover_inr: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)

    # ── Timestamps ────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # ── Relationships ─────────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="profile")

    def __repr__(self) -> str:
        return f"<MSMEProfile id={self.id} name={self.business_name!r}>"
