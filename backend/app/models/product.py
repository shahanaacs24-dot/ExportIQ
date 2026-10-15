"""
ExportIQ — Product and DestinationCountry reference data models.
These are seeded from the knowledge base; not user-created.
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    hs_code: Mapped[str] = mapped_column(
        String(12), nullable=False, index=True,
        comment="Harmonised System code (6-digit minimum)"
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    assessments: Mapped[list["Assessment"]] = relationship("Assessment", back_populates="product")

    def __repr__(self) -> str:
        return f"<Product hs={self.hs_code!r} name={self.name!r}>"


class DestinationCountry(Base):
    __tablename__ = "destination_countries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    iso_code: Mapped[str] = mapped_column(
        String(3), unique=True, nullable=False, index=True,
        comment="ISO 3166-1 alpha-3 code"
    )
    iso_code_2: Mapped[str] = mapped_column(String(2), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    trade_bloc: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
        comment="E.g. EU, ASEAN, GCC, SAARC"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    assessments: Mapped[list["Assessment"]] = relationship(
        "Assessment", back_populates="destination_country"
    )

    def __repr__(self) -> str:
        return f"<DestinationCountry {self.iso_code!r} {self.name!r}>"
