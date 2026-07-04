"""Vision pipeline package: provider contract, mock + Claude implementations."""
from __future__ import annotations

from ..config import get_settings
from .base import Detection, VisionProvider, VisionResult
from .mock_provider import MockVisionProvider

__all__ = [
    "Detection",
    "VisionProvider",
    "VisionResult",
    "MockVisionProvider",
    "get_vision_provider",
]


def get_vision_provider(catalog_names: list[str] | None = None) -> VisionProvider:
    """Return the configured provider: mock by default, or a real model when
    the matching API key is present (Claude or Gemini)."""
    provider = get_settings().resolved_provider()
    if provider == "claude":
        from .claude_provider import ClaudeVisionProvider

        return ClaudeVisionProvider(catalog_names=catalog_names)
    if provider == "gemini":
        from .gemini_provider import GeminiVisionProvider

        return GeminiVisionProvider(catalog_names=catalog_names)
    return MockVisionProvider()
