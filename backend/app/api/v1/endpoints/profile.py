"""ExportIQ — MSME profile endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.msme_profile import MSMEProfile
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileRead

router = APIRouter()


@router.get("", response_model=ProfileRead)
def get_profile(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    profile = db.query(MSMEProfile).filter(MSMEProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Please create one.")
    return profile


@router.post("", response_model=ProfileRead, status_code=201)
def create_profile(
    payload: ProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if db.query(MSMEProfile).filter(MSMEProfile.user_id == current_user.id).first():
        raise HTTPException(status_code=400, detail="Profile already exists. Use PATCH to update.")
    profile = MSMEProfile(user_id=current_user.id, **payload.model_dump(exclude_unset=True))
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.patch("", response_model=ProfileRead)
def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    profile = db.query(MSMEProfile).filter(MSMEProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile
