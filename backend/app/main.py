"""
ExportIQ Backend — FastAPI application entry point.

DISCLAIMER: ExportIQ is a decision-support tool for indicative assessment only.
It does not issue official certifications, provide legal approval, or guarantee
export success. All scores are indicative and should be verified with qualified
trade professionals and official regulatory bodies.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import get_settings
from app.api.v1.router import api_router

settings = get_settings()

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app_name} v{settings.app_version} [{settings.app_env}]")
    yield
    logger.info(f"Shutting down {settings.app_name}")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "ExportIQ — AI-Powered MSME Export Readiness Assessment Platform.\n\n"
        "**Disclaimer:** This tool provides an indicative readiness assessment only. "
        "It is not an official certification and does not guarantee export approval. "
        "Always verify requirements with the relevant regulatory authorities."
    ),
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/api/docs",
        "disclaimer": (
            "Indicative assessment tool only. "
            "Not an official certification or legal approval."
        ),
    }
