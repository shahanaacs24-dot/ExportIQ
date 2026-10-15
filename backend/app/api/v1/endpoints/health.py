"""ExportIQ — Health check endpoint."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db, check_db_connection
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("")
def health_check():
    """Basic liveness check — no DB required."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    """Readiness check — verifies DB connectivity."""
    db_ok = check_db_connection()
    status = "ready" if db_ok else "not_ready"
    return {
        "status": status,
        "database": "connected" if db_ok else "unreachable",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
