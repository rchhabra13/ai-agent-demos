"""Application configuration via environment variables."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    All configuration is loaded from environment variables (or a .env file).
    Required fields raise a clear error on startup if missing.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Anthropic ────────────────────────────────────────────────────────────
    anthropic_api_key: str = Field(
        description="Anthropic API key. Required.",
    )

    # ── LLM ─────────────────────────────────────────────────────────────────
    llm_model: str = Field(
        default="claude-opus-4-6",
        description="Anthropic model ID to use for reasoning.",
    )
    llm_max_tokens: int = Field(default=2048, ge=256, le=8192)
    llm_temperature: float = Field(default=0.1, ge=0.0, le=1.0)

    # ── ClinicalTrials.gov ───────────────────────────────────────────────────
    ctgov_base_url: str = Field(default="https://clinicaltrials.gov/api/v2")
    ctgov_user_agent: str = Field(
        default="ClinicalTrialMatchmaker/0.1.0 (contact@example.com)"
    )
    ctgov_max_results: int = Field(default=20, ge=1, le=100)
    ctgov_timeout_seconds: float = Field(default=30.0, gt=0)

    # ── FHIR ─────────────────────────────────────────────────────────────────
    fhir_base_url: str = Field(default="https://hapi.fhir.org/baseR4")
    fhir_timeout_seconds: float = Field(default=30.0, gt=0)

    # ── Server ───────────────────────────────────────────────────────────────
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")
    environment: Literal["development", "staging", "production"] = Field(
        default="development"
    )

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance. Call this instead of constructing directly."""
    return Settings()  # type: ignore[call-arg]
