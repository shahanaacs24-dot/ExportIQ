"""
ExportIQ Backend — Application configuration.
Reads settings from environment variables / .env file.
"""
from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────
    app_env: str = "development"
    app_name: str = "ExportIQ"
    app_version: str = "1.0.0"
    debug: bool = True

    # ── Security ──────────────────────────────────────────────
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # ── Database ──────────────────────────────────────────────
    database_url: str = "postgresql+psycopg2://exportiq:change_me@localhost:5432/exportiq"
    async_database_url: str = "postgresql+asyncpg://exportiq:change_me@localhost:5432/exportiq"

    # ── File Storage ──────────────────────────────────────────
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 20
    allowed_extensions: str = "pdf,jpg,jpeg,png,tiff"

    @property
    def allowed_extensions_set(self) -> set:
        return {ext.strip().lower() for ext in self.allowed_extensions.split(",")}

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    # ── CORS ──────────────────────────────────────────────────
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    # ── Optional LLM ─────────────────────────────────────────
    llm_provider: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm_provider and self.anthropic_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
