"""ExportIQ — PDF Report Download endpoint."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.assessment import Assessment
from app.services.reports.pdf_generator import generate_assessment_pdf

router = APIRouter()


@router.get("/{assessment_id}/pdf")
def download_assessment_pdf(
    assessment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Generate and download a downloadable PDF readiness report for the specified assessment.
    Ensures the user owns the assessment.
    """
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id,
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found or unauthorized")

    try:
        pdf_bytes = generate_assessment_pdf(assessment_id, db)
        filename = f"ExportIQ_Readiness_Report_Assessment_{assessment_id}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {e}")
