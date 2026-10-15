"""
ExportIQ — Deterministic Compliance Matching Engine.
Evaluates export requirements against MSME profile, product HS code,
destination country, and uploaded document evidence.

Distinguishes:
- compliant
- non_compliant
- incomplete
- expired
- unverified
- missing
- not_applicable
"""
import logging
from datetime import date, datetime
from sqlalchemy.orm import Session

from app.models.assessment import Assessment, AssessmentRequirement, ComplianceStatus
from app.models.requirement import Requirement
from app.models.document import Document, DocumentStatus

logger = logging.getLogger(__name__)


def run_compliance_check(assessment_id: int, db: Session) -> None:
    """
    Evaluate all active requirements against the assessment's product,
    destination country, user profile, and uploaded documents.
    Populates or updates AssessmentRequirement records.
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        logger.error(f"Assessment {assessment_id} not found for compliance evaluation")
        return

    product = assessment.product
    destination = assessment.destination_country
    user_id = assessment.user_id

    # Fetch all active requirements (excluding internal ERI-TEST fixtures)
    requirements = db.query(Requirement).filter(
        Requirement.is_active == True,
        ~Requirement.code.like("ERI-TEST%")
    ).all()

    # Fetch user documents (both unassigned and assessment-linked)
    user_docs = db.query(Document).filter(
        Document.user_id == user_id,
        Document.status == DocumentStatus.PROCESSED,
    ).all()

    # Clear previous requirement results for this assessment
    db.query(AssessmentRequirement).filter(
        AssessmentRequirement.assessment_id == assessment_id
    ).delete()

    compliant_count = 0
    missing_count = 0
    incomplete_count = 0
    expired_count = 0
    total_evaluated = 0

    for req in requirements:
        status, explanation, evidence_ids, matched_fields = evaluate_single_requirement(
            req, product, destination, user_docs
        )

        # Calculate points
        points_possible = float(req.weight)
        points_earned = 0.0
        if status == ComplianceStatus.COMPLIANT:
            points_earned = points_possible
        elif status == ComplianceStatus.UNVERIFIED:
            points_earned = points_possible * 0.5  # partial credit for unverified evidence

        if status == ComplianceStatus.COMPLIANT:
            compliant_count += 1
        elif status == ComplianceStatus.MISSING:
            missing_count += 1
        elif status == ComplianceStatus.INCOMPLETE:
            incomplete_count += 1
        elif status == ComplianceStatus.EXPIRED:
            expired_count += 1

        if status != ComplianceStatus.NOT_APPLICABLE:
            total_evaluated += 1

        ar = AssessmentRequirement(
            assessment_id=assessment_id,
            requirement_id=req.id,
            status=status,
            explanation=explanation,
            evidence_document_ids=evidence_ids if evidence_ids else None,
            matched_fields=matched_fields if matched_fields else None,
            points_earned=points_earned,
            points_possible=points_possible,
        )
        db.add(ar)

    # Update assessment summary counts
    assessment.total_requirements = total_evaluated
    assessment.compliant_count = compliant_count
    assessment.missing_count = missing_count
    assessment.incomplete_count = incomplete_count
    assessment.expired_count = expired_count

    db.commit()
    logger.info(
        f"Compliance check completed for assessment {assessment_id}: "
        f"total={total_evaluated}, compliant={compliant_count}, missing={missing_count}"
    )


def evaluate_single_requirement(
    req: Requirement, product, destination, user_docs: list[Document]
) -> tuple[ComplianceStatus, str, list[int], dict]:
    """
    Evaluate applicability and compliance for a single requirement.
    Returns (status, explanation, evidence_document_ids, matched_fields).
    """
    # 1. Check Applicability
    if req.applicable_hs_codes:
        matches_hs = any(product.hs_code.startswith(prefix) for prefix in req.applicable_hs_codes)
        if not matches_hs:
            return (
                ComplianceStatus.NOT_APPLICABLE,
                f"Requirement does not apply to product HS code {product.hs_code}.",
                [],
                {}
            )

    if req.applicable_country_iso:
        if destination.iso_code not in req.applicable_country_iso:
            return (
                ComplianceStatus.NOT_APPLICABLE,
                f"Requirement does not apply to destination country {destination.name} ({destination.iso_code}).",
                [],
                {}
            )

    # 2. Check Evidence (Uploaded Documents)
    required_types = req.required_document_types or []
    if not required_types:
        return (
            ComplianceStatus.COMPLIANT if req.kb_status.value == "verified" else ComplianceStatus.UNVERIFIED,
            "Requirement has no mandatory document upload condition.",
            [],
            {}
        )

    matching_docs = [
        d for d in user_docs if d.document_type.value in required_types
    ]

    if not matching_docs:
        return (
            ComplianceStatus.MISSING,
            f"Required document type(s) [{', '.join(required_types)}] have not been uploaded.",
            [],
            {}
        )

    evidence_ids = []
    matched_fields = {}
    has_valid_evidence = False
    expiry_found = False

    for doc in matching_docs:
        evidence_ids.append(doc.id)
        fields = doc.extracted_fields or {}
        matched_fields.update(fields)

        validity_str = fields.get("validity_date") or fields.get("expiry_date")
        if validity_str:
            try:
                v_date = datetime.strptime(validity_str[:10], "%Y-%m-%d").date()
                if v_date < date.today():
                    expiry_found = True
            except Exception:
                pass

        required_fields = req.evidence_fields or []
        missing_fields = [f for f in required_fields if f not in fields or not fields[f]]

        if expiry_found:
            return (
                ComplianceStatus.EXPIRED,
                f"Uploaded document '{doc.original_filename}' has expired (validity past).",
                evidence_ids,
                matched_fields
            )

        if missing_fields and required_fields:
            return (
                ComplianceStatus.INCOMPLETE,
                f"Uploaded document '{doc.original_filename}' is missing required fields: {', '.join(missing_fields)}.",
                evidence_ids,
                matched_fields
            )

        has_valid_evidence = True

    if has_valid_evidence:
        if req.kb_status.value == "verified":
            return (
                ComplianceStatus.COMPLIANT,
                f"Valid evidence document provided: '{matching_docs[0].original_filename}'.",
                evidence_ids,
                matched_fields
            )
        else:
            return (
                ComplianceStatus.UNVERIFIED,
                f"Evidence provided but knowledge base entry is unverified. Manual review recommended.",
                evidence_ids,
                matched_fields
            )

    return (
        ComplianceStatus.MISSING,
        "No valid document evidence found.",
        [],
        {}
    )
