"""
ExportIQ — PDF Report Generation Unit Tests.
"""
import pytest
from app.core.database import SessionLocal
from app.models.product import Product, DestinationCountry
from app.models.assessment import Assessment, AssessmentRequirement, ComplianceStatus
from app.services.reports.pdf_generator import generate_assessment_pdf


def test_pdf_generation():
    db = SessionLocal()
    try:
        prod = db.query(Product).first()
        dest = db.query(DestinationCountry).first()

        assessment = Assessment(
            user_id=1,
            product_id=prod.id,
            destination_country_id=dest.id,
            status="completed",
            eri_score=85.0,
        )
        db.add(assessment)
        db.flush()

        pdf_bytes = generate_assessment_pdf(assessment.id, db)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 500
        # PDF magic bytes
        assert pdf_bytes.startswith(b"%PDF")
    finally:
        db.close()
