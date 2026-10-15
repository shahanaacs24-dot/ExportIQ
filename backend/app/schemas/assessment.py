"""ExportIQ — Assessment schemas."""
from typing import Optional, Any, List
from datetime import datetime
from pydantic import BaseModel
from app.models.assessment import AssessmentStatus, ComplianceStatus


class AssessmentCreate(BaseModel):
    product_id: int
    destination_country_id: int
    user_responses: Optional[dict] = None


class AssessmentRead(BaseModel):
    id: int
    user_id: int
    product_id: int
    destination_country_id: int
    status: AssessmentStatus
    eri_score: Optional[float] = None
    total_requirements: Optional[int] = None
    compliant_count: Optional[int] = None
    missing_count: Optional[int] = None
    incomplete_count: Optional[int] = None
    expired_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RequirementInfo(BaseModel):
    id: int
    code: str
    name: str
    description: str
    category: str
    is_mandatory: bool
    issuing_authority: Optional[str] = None
    source_url: Optional[str] = None

    model_config = {"from_attributes": True}


class RequirementResultRead(BaseModel):
    id: int
    requirement_id: int
    status: ComplianceStatus
    explanation: Optional[str] = None
    evidence_document_ids: Optional[List[int]] = None
    matched_fields: Optional[Any] = None
    points_earned: float
    points_possible: float
    requirement: Optional[RequirementInfo] = None

    model_config = {"from_attributes": True}


class AssessmentDetail(AssessmentRead):
    category_scores: Optional[Any] = None
    score_breakdown: Optional[Any] = None
    user_responses: Optional[Any] = None
    submitted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    requirement_results: List[RequirementResultRead] = []
