"""ExportIQ — Products and destination countries endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.product import Product, DestinationCountry
from app.schemas.product import ProductRead, DestinationCountryRead

router = APIRouter()


@router.get("", response_model=List[ProductRead])
def list_products(
    q: Optional[str] = Query(None, description="Search by name or HS code"),
    db: Session = Depends(get_db),
    _=Depends(get_current_active_user),
):
    query = db.query(Product).filter(Product.is_active == True)
    if q:
        query = query.filter(
            Product.name.ilike(f"%{q}%") | Product.hs_code.ilike(f"%{q}%")
        )
    return query.order_by(Product.name).all()


@router.get("/destinations", response_model=List[DestinationCountryRead])
def list_destinations(
    q: Optional[str] = Query(None, description="Search by name or ISO code"),
    db: Session = Depends(get_db),
    _=Depends(get_current_active_user),
):
    query = db.query(DestinationCountry).filter(DestinationCountry.is_active == True)
    if q:
        query = query.filter(
            DestinationCountry.name.ilike(f"%{q}%") |
            DestinationCountry.iso_code.ilike(f"%{q}%")
        )
    return query.order_by(DestinationCountry.name).all()
