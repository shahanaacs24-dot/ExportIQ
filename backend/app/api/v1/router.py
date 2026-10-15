"""ExportIQ Backend — API v1 router."""
from fastapi import APIRouter

from app.api.v1.endpoints import health, auth, profile, products, documents, assessments, reports

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(profile.router, prefix="/profile", tags=["MSME Profile"])
api_router.include_router(products.router, prefix="/products", tags=["Products & Destinations"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["Assessments"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
