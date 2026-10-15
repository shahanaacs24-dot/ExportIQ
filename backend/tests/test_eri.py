"""
ExportIQ — ERI Scoring and Gap Analysis Unit Tests.
Covers missing (0), incomplete (25), unverified (50), compliant (100),
not-applicable normalization, and mixed compliance states.
"""
import uuid
import pytest
from app.core.database import SessionLocal
from app.models.requirement import Requirement, RequirementCategory, RequirementStatus
from app.models.product import Product, DestinationCountry
from app.models.assessment import Assessment, AssessmentRequirement, ComplianceStatus
from app.services.eri.calculator import calculate_eri


def test_eri_all_missing_is_zero():
    db = SessionLocal()
    try:
        prod = db.query(Product).first()
        dest = db.query(DestinationCountry).first()
        uid = uuid.uuid4().hex[:8]

        req = Requirement(
            code=f"ERI-MISSING-{uid}",
            name="Missing Req",
            description="Test",
            category=RequirementCategory.LEGAL_REGISTRATION,
            weight=10,
            is_mandatory=True,
            kb_status=RequirementStatus.VERIFIED,
        )
        db.add(req)
        db.flush()

        assessment = Assessment(
            user_id=1,
            product_id=prod.id,
            destination_country_id=dest.id,
            status="draft",
        )
        db.add(assessment)
        db.flush()

        ar = AssessmentRequirement(
            assessment_id=assessment.id,
            requirement_id=req.id,
            status=ComplianceStatus.MISSING,
            points_earned=0.0,
            points_possible=10.0,
        )
        db.add(ar)
        db.commit()

        calculate_eri(assessment.id, db)
        db.refresh(assessment)
        assert assessment.eri_score == 0.0
    finally:
        db.close()


def test_eri_all_incomplete_is_25():
    db = SessionLocal()
    try:
        prod = db.query(Product).first()
        dest = db.query(DestinationCountry).first()
        uid = uuid.uuid4().hex[:8]

        req = Requirement(
            code=f"ERI-INCOMPLETE-{uid}",
            name="Incomplete Req",
            description="Test",
            category=RequirementCategory.LEGAL_REGISTRATION,
            weight=10,
            is_mandatory=True,
            kb_status=RequirementStatus.VERIFIED,
        )
        db.add(req)
        db.flush()

        assessment = Assessment(
            user_id=1,
            product_id=prod.id,
            destination_country_id=dest.id,
            status="draft",
        )
        db.add(assessment)
        db.flush()

        ar = AssessmentRequirement(
            assessment_id=assessment.id,
            requirement_id=req.id,
            status=ComplianceStatus.INCOMPLETE,
            points_earned=2.5,
            points_possible=10.0,
        )
        db.add(ar)
        db.commit()

        calculate_eri(assessment.id, db)
        db.refresh(assessment)
        # Incomplete awards 25% of points = 25.0 ERI
        assert assessment.eri_score == 25.0
    finally:
        db.close()


def test_eri_all_unverified_is_50():
    db = SessionLocal()
    try:
        prod = db.query(Product).first()
        dest = db.query(DestinationCountry).first()
        uid = uuid.uuid4().hex[:8]

        req = Requirement(
            code=f"ERI-UNVERIFIED-{uid}",
            name="Unverified Req",
            description="Test",
            category=RequirementCategory.LEGAL_REGISTRATION,
            weight=10,
            is_mandatory=True,
            kb_status=RequirementStatus.UNVERIFIED,
        )
        db.add(req)
        db.flush()

        assessment = Assessment(
            user_id=1,
            product_id=prod.id,
            destination_country_id=dest.id,
            status="draft",
        )
        db.add(assessment)
        db.flush()

        ar = AssessmentRequirement(
            assessment_id=assessment.id,
            requirement_id=req.id,
            status=ComplianceStatus.UNVERIFIED,
            points_earned=5.0,
            points_possible=10.0,
        )
        db.add(ar)
        db.commit()

        calculate_eri(assessment.id, db)
        db.refresh(assessment)
        # Unverified awards 50% of points = 50.0 ERI
        assert assessment.eri_score == 50.0
    finally:
        db.close()


def test_eri_not_applicable_normalization():
    db = SessionLocal()
    try:
        prod = db.query(Product).first()
        dest = db.query(DestinationCountry).first()
        uid = uuid.uuid4().hex[:8]

        req_na = Requirement(
            code=f"ERI-NA-{uid}",
            name="NA Req",
            description="Test",
            category=RequirementCategory.LEGAL_REGISTRATION,
            weight=10,
            is_mandatory=True,
            kb_status=RequirementStatus.VERIFIED,
        )
        req_comp = Requirement(
            code=f"ERI-COMP-{uid}",
            name="Compliant Req",
            description="Test",
            category=RequirementCategory.LEGAL_REGISTRATION,
            weight=10,
            is_mandatory=True,
            kb_status=RequirementStatus.VERIFIED,
        )
        db.add(req_na)
        db.add(req_comp)
        db.flush()

        assessment = Assessment(
            user_id=1,
            product_id=prod.id,
            destination_country_id=dest.id,
            status="draft",
        )
        db.add(assessment)
        db.flush()

        ar_na = AssessmentRequirement(
            assessment_id=assessment.id,
            requirement_id=req_na.id,
            status=ComplianceStatus.NOT_APPLICABLE,
            points_earned=0.0,
            points_possible=0.0,
        )
        ar_comp = AssessmentRequirement(
            assessment_id=assessment.id,
            requirement_id=req_comp.id,
            status=ComplianceStatus.COMPLIANT,
            points_earned=10.0,
            points_possible=10.0,
        )
        db.add(ar_na)
        db.add(ar_comp)
        db.commit()

        calculate_eri(assessment.id, db)
        db.refresh(assessment)
        # NA is excluded, leaving only the compliant requirement = 100.0 ERI
        assert assessment.eri_score == 100.0
    finally:
        db.close()
