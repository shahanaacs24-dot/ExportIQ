"""
ExportIQ — Compliance engine unit tests.
Tests applicability, missing evidence, incomplete evidence, expired evidence,
and compliant states.
"""
import pytest
from datetime import date, timedelta
from app.core.database import SessionLocal
from app.models.requirement import Requirement, RequirementCategory, RequirementStatus
from app.models.product import Product, DestinationCountry
from app.models.document import Document, DocumentType, DocumentStatus
from app.services.compliance.engine import evaluate_single_requirement, ComplianceStatus


def test_compliance_not_applicable():
    db = SessionLocal()
    try:
        req = Requirement(
            code="TEST-USA-001",
            name="US Specific Rule",
            description="Only for USA",
            category=RequirementCategory.TRADE_DOCUMENTATION,
            applicable_country_iso=["USA"],
            required_document_types=["health_certificate"],
            kb_status=RequirementStatus.VERIFIED,
        )
        product = Product(hs_code="100630", name="Rice")
        dest = DestinationCountry(iso_code="GBR", iso_code_2="GB", name="United Kingdom")

        status, explanation, _, _ = evaluate_single_requirement(req, product, dest, [])
        assert status == ComplianceStatus.NOT_APPLICABLE
    finally:
        db.close()


def test_compliance_missing():
    db = SessionLocal()
    try:
        req = Requirement(
            code="TEST-IEC-001",
            name="IEC Requirement",
            description="IEC needed",
            category=RequirementCategory.LEGAL_REGISTRATION,
            required_document_types=["iec_certificate"],
            kb_status=RequirementStatus.VERIFIED,
        )
        product = Product(hs_code="100630", name="Rice")
        dest = DestinationCountry(iso_code="USA", iso_code_2="US", name="USA")

        status, explanation, _, _ = evaluate_single_requirement(req, product, dest, [])
        assert status == ComplianceStatus.MISSING
    finally:
        db.close()


def test_compliance_compliant():
    db = SessionLocal()
    try:
        req = Requirement(
            code="TEST-IEC-002",
            name="IEC Requirement",
            description="IEC needed",
            category=RequirementCategory.LEGAL_REGISTRATION,
            required_document_types=["iec_certificate"],
            evidence_fields=["iec_number"],
            kb_status=RequirementStatus.VERIFIED,
        )
        product = Product(hs_code="100630", name="Rice")
        dest = DestinationCountry(iso_code="USA", iso_code_2="US", name="USA")

        doc = Document(
            id=999,
            user_id=1,
            original_filename="iec.pdf",
            stored_filename="stored_iec.pdf",
            file_path="uploads/stored_iec.pdf",
            file_size_bytes=1000,
            mime_type="application/pdf",
            document_type=DocumentType.IEC_CERTIFICATE,
            status=DocumentStatus.PROCESSED,
            extracted_fields={"iec_number": "0388002931"},
        )

        status, explanation, _, _ = evaluate_single_requirement(req, product, dest, [doc])
        assert status == ComplianceStatus.COMPLIANT
    finally:
        db.close()


def test_compliance_expired():
    db = SessionLocal()
    try:
        req = Requirement(
            code="TEST-EXP-001",
            name="FSSAI License",
            description="FSSAI needed",
            category=RequirementCategory.PRODUCT_QUALITY,
            required_document_types=["fssai_license"],
            evidence_fields=["fssai_license_number"],
            kb_status=RequirementStatus.VERIFIED,
        )
        product = Product(hs_code="100630", name="Rice")
        dest = DestinationCountry(iso_code="USA", iso_code_2="US", name="USA")

        yesterday = (date.today() - timedelta(days=5)).isoformat()
        doc = Document(
            id=998,
            user_id=1,
            original_filename="fssai.pdf",
            stored_filename="stored_fssai.pdf",
            file_path="uploads/stored_fssai.pdf",
            file_size_bytes=1000,
            mime_type="application/pdf",
            document_type=DocumentType.FSSAI_LICENSE,
            status=DocumentStatus.PROCESSED,
            extracted_fields={"fssai_license_number": "12345678901234", "validity_date": yesterday},
        )

        status, explanation, _, _ = evaluate_single_requirement(req, product, dest, [doc])
        assert status == ComplianceStatus.EXPIRED
    finally:
        db.close()
