"""Application configuration.

Central place for tunable knobs: database location, which vision provider to
use, and the freshness/alert thresholds the domain services read from.
"""
from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FRIDGE_", extra="ignore")

    # Persistence
    database_url: str = "sqlite:///./fridge.db"

    # Vision provider selection: "mock" (default, offline), "claude", or "gemini".
    # When set to "auto", we pick a real provider only if a matching key exists.
    vision_provider: str = "auto"
    anthropic_api_key: str | None = None
    claude_model: str = "claude-opus-4-8"
    google_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash-lite"

    # Dynamic recipe search makes a second LLM call per ingest. Disable it
    # (FRIDGE_RECIPE_SEARCH=false) to halve API usage on tight free-tier quotas.
    recipe_search: bool = True

    # Freshness: fraction of remaining shelf life at which an item is flagged.
    expiring_threshold: float = 0.25  # <=25% life left -> "expiring"

    def google_key(self) -> str | None:
        """Google/Gemini key from settings or common env var names."""
        return (
            self.google_api_key
            or os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("GEMINI_API_KEY")
        )

    def resolved_provider(self) -> str:
        """Resolve the "auto" selection into a concrete provider name."""
        if self.vision_provider != "auto":
            return self.vision_provider
        if self.anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY"):
            return "claude"
        if self.google_key():
            return "gemini"
        return "mock"


@lru_cache
def get_settings() -> Settings:
    return Settings()
