"""ExportIQ — Assessment endpoints."""
from typing import List
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.assessment import Assessment, AssessmentStatus, AssessmentRequirement
from app.models.user import User
from app.schemas.assessment import AssessmentCreate, AssessmentRead, AssessmentDetail, RequirementResultRead
from app.services.compliance.engine import run_compliance_check
from app.services.eri.calculator import calculate_eri

router = APIRouter()


@router.post("", response_model=AssessmentRead, status_code=201)
def create_assessment(
    payload: AssessmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    assessment = Assessment(
        user_id=current_user.id,
        product_id=payload.product_id,
        destination_country_id=payload.destination_country_id,
        status=AssessmentStatus.DRAFT,
        user_responses=payload.user_responses,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.get("", response_model=List[AssessmentRead])
def list_assessments(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Assessment)
        .filter(Assessment.user_id == current_user.id)
        .order_by(Assessment.created_at.desc())
        .all()
    )


@router.get("/{assessment_id}", response_model=AssessmentDetail)
def get_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    a = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id,
    ).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return a


@router.post("/{assessment_id}/submit", response_model=AssessmentDetail)
def submit_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Trigger compliance matching and ERI calculation."""
    a = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id,
    ).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assessment not found")

    a.status = AssessmentStatus.IN_PROGRESS
    a.submitted_at = datetime.now(timezone.utc)
    db.commit()

    # Run compliance engine
    run_compliance_check(a.id, db)

    # Calculate ERI
    calculate_eri(a.id, db)

    db.refresh(a)
    return a
