"""
ExportIQ — Export Readiness Index (ERI) Calculator & Gap Analysis Engine.

Calculates a transparent, explainable 0–100 Export Readiness Score based on
weighted requirement compliance. Normalizes scores for non-applicable requirements.
Never gives credit for missing, expired, or unknown information.

DISCLAIMER: ERI is an indicative assessment score for decision support only.
It does not constitute an official certification or a guaranteed prediction of export success.
"""
import logging
from sqlalchemy.orm import Session

from app.models.assessment import Assessment, AssessmentRequirement, ComplianceStatus
from app.models.requirement import RequirementCategory

logger = logging.getLogger(__name__)

# Category weights for ERI calculation (must sum to 1.0 or scale accordingly)
CATEGORY_WEIGHTS = {
    RequirementCategory.LEGAL_REGISTRATION: 0.30,
    RequirementCategory.PRODUCT_QUALITY: 0.25,
    RequirementCategory.TRADE_DOCUMENTATION: 0.25,
    RequirementCategory.PHYTOSANITARY: 0.10,
    RequirementCategory.LABELLING: 0.05,
    RequirementCategory.PACKAGING: 0.05,
}


def calculate_eri(assessment_id: int, db: Session) -> None:
    """
    Calculate overall ERI score, category-level breakdown, deductions,
    gap analysis, and prioritized recommendations for an assessment.
    """
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        logger.error(f"Assessment {assessment_id} not found for ERI calculation")
        return

    req_results = db.query(AssessmentRequirement).filter(
        AssessmentRequirement.assessment_id == assessment_id
    ).all()

    if not req_results:
        assessment.eri_score = 0.0
        assessment.category_scores = {}
        assessment.score_breakdown = {"gaps": [], "recommendations": []}
        db.commit()
        return

    total_possible_points = 0.0
    total_earned_points = 0.0

    category_possible = {}
    category_earned = {}

    gaps = []
    recommendations = []

    for ar in req_results:
        req = ar.requirement
        if ar.status == ComplianceStatus.NOT_APPLICABLE:
            continue  # Exclude from calculation

        cat = req.category
        base_weight = CATEGORY_WEIGHTS.get(cat, 0.05)
        # Scale requirement weight by category weight
        req_weight = float(req.weight) * base_weight

        total_possible_points += req_weight

        # Earned points based on status
        earned = 0.0
        if ar.status == ComplianceStatus.COMPLIANT:
            earned = req_weight
        elif ar.status == ComplianceStatus.UNVERIFIED:
            earned = req_weight * 0.5
        elif ar.status == ComplianceStatus.INCOMPLETE:
            earned = req_weight * 0.25
        elif ar.status in [ComplianceStatus.MISSING, ComplianceStatus.EXPIRED, ComplianceStatus.NON_COMPLIANT]:
            earned = 0.0

        total_earned_points += earned

        # Category aggregation
        category_possible[cat.value] = category_possible.get(cat.value, 0.0) + req_weight
        category_earned[cat.value] = category_earned.get(cat.value, 0.0) + earned

        # Identify gaps and recommendations for non-compliant states
        if ar.status in [ComplianceStatus.MISSING, ComplianceStatus.INCOMPLETE, ComplianceStatus.EXPIRED, ComplianceStatus.UNVERIFIED]:
            severity = "critical" if (req.is_mandatory and ar.status in [ComplianceStatus.MISSING, ComplianceStatus.EXPIRED]) else "moderate"
            if ar.status == ComplianceStatus.UNVERIFIED:
                severity = "low"

            gaps.append({
                "requirement_code": req.code,
                "requirement_name": req.name,
                "category": cat.value,
                "status": ar.status.value,
                "severity": severity,
                "explanation": ar.explanation,
                "is_mandatory": req.is_mandatory,
            })

            # Recommendation action
            action_text = f"Obtain or update {req.name}."
            if ar.status == ComplianceStatus.MISSING:
                action_text = f"Upload required document for '{req.name}' (Required types: {', '.join(req.required_document_types)})."
            elif ar.status == ComplianceStatus.EXPIRED:
                action_text = f"Renew expired document for '{req.name}'."
            elif ar.status == ComplianceStatus.INCOMPLETE:
                action_text = f"Provide complete documentation and ensure all required fields are present for '{req.name}'."
            elif ar.status == ComplianceStatus.UNVERIFIED:
                action_text = f"Verify evidence for '{req.name}' with {req.issuing_authority or 'issuing authority'}."

            recommendations.append({
                "priority": 1 if severity == "critical" else (2 if severity == "moderate" else 3),
                "requirement_code": req.code,
                "title": f"Address Gap: {req.name}",
                "action": action_text,
                "reason": ar.explanation,
                "issuing_authority": req.issuing_authority,
                "source_url": req.source_url,
            })

    # Calculate overall ERI score (0 to 100)
    if total_possible_points > 0:
        eri = (total_earned_points / total_possible_points) * 100.0
        eri = max(0.0, min(100.0, eri))
    else:
        eri = 0.0

    # Calculate category percentage scores
    category_scores = {}
    for cat_key, possible in category_possible.items():
        earned = category_earned.get(cat_key, 0.0)
        category_scores[cat_key] = round((earned / possible) * 100.0, 1) if possible > 0 else 0.0

    # Sort recommendations by priority
    recommendations.sort(key=lambda x: x["priority"])

    assessment.eri_score = round(eri, 1)
    assessment.category_scores = category_scores
    assessment.score_breakdown = {
        "formula": "ERI = (Sum of Earned Weighted Points / Sum of Possible Weighted Points) * 100",
        "total_earned_points": round(total_earned_points, 2),
        "total_possible_points": round(total_possible_points, 2),
        "category_weights": {k.value: v for k, v in CATEGORY_WEIGHTS.items()},
        "gaps": gaps,
        "recommendations": recommendations,
        "disclaimer": "Indicative assessment score only. Not an official certification or validated prediction of export success.",
    }
    assessment.status = "completed"

    db.commit()
    logger.info(f"ERI calculated for assessment {assessment_id}: score={assessment.eri_score}")
