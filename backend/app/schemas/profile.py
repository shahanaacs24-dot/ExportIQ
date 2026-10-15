"""ExportIQ — MSME profile schemas."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.msme_profile import MSMECategory


class ProfileBase(BaseModel):
    business_name: str
    gstin: Optional[str] = None
    pan: Optional[str] = None
    iec_number: Optional[str] = None
    udyam_number: Optional[str] = None
    category: Optional[MSMECategory] = None
    industry_sector: Optional[str] = None
    year_established: Optional[int] = None
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    has_exported_before: bool = False
    export_experience_years: Optional[int] = None
    annual_turnover_inr: Optional[float] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    business_name: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    iec_number: Optional[str] = None
    udyam_number: Optional[str] = None
    category: Optional[MSMECategory] = None
    industry_sector: Optional[str] = None
    year_established: Optional[int] = None
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    has_exported_before: Optional[bool] = None
    export_experience_years: Optional[int] = None
    annual_turnover_inr: Optional[float] = None


class ProfileRead(ProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
