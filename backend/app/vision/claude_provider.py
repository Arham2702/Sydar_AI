"""Real vision provider backed by a Claude multimodal model.

Sends a fridge image to Claude and asks for structured detections constrained
to the curated catalog. Activated only when an API key is available (see
``config.resolved_provider``); the deterministic ``MockVisionProvider`` is the
default so dev and tests never depend on the network.

This module is intentionally excluded from the coverage gate — it requires a
live API and is exercised manually via the real-vision path in the README.
"""
from __future__ import annotations

import base64
import json

from pydantic import BaseModel

from ..config import get_settings
from ..models.enums import DetectionSource
from .base import Detection, VisionError, VisionProvider, VisionResult

# Structured-output schema Claude must return.
DETECTION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "detections": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "category": {"type": "string"},
                    "count": {"type": "integer"},
                    "confidence": {"type": "number"},
                    "freshness": {"type": "number"},
                },
                "required": ["name", "category", "count", "confidence", "freshness"],
            },
        }
    },
    "required": ["detections"],
}


class _ClaudeDetection(BaseModel):
    name: str
    category: str
    count: int
    confidence: float
    freshness: float | None = None


def _media_type(image_bytes: bytes) -> str:
    if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if image_bytes[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    return "image/png"


class ClaudeVisionProvider(VisionProvider):
    source = DetectionSource.CLAUDE_VISION
    simulated = False

    def __init__(self, catalog_names: list[str] | None = None):
        self.settings = get_settings()
        self.catalog_names = catalog_names or []

    def _prompt(self) -> str:
        hint = ""
        if self.catalog_names:
            hint = (
                " When an item clearly matches one of these known names, reuse that exact "
                f"name: {', '.join(self.catalog_names)}."
            )
        return (
            "You are the vision system for a smart fridge. Identify EVERY distinct food or "
            "drink item visible in this photo — do not limit to a preset list. Return exactly "
            "ONE object per distinct item type with the TOTAL count of that item; never emit "
            "multiple objects for the same type. For each item give name, category, count, "
            "confidence (0-1), and freshness (integer 1-100 estimating how fresh/edible it "
            "looks from its visual state: 100 = pristine, lower for bruising, browning, black "
            "spots, mould, or wilting; when they vary, report the worst-looking ones)."
            + hint + " Return JSON matching the schema; omit items you cannot see."
        )

    def analyze(self, image_bytes: bytes, *, sample_name: str | None = None) -> VisionResult:
        import anthropic  # imported lazily so the mock path needs no SDK/network

        client = anthropic.Anthropic(api_key=self.settings.anthropic_api_key)
        encoded = base64.standard_b64encode(image_bytes).decode("utf-8")
        try:
            response = client.messages.create(
                model=self.settings.claude_model,
                max_tokens=2048,
                output_config={"format": {"type": "json_schema", "schema": DETECTION_SCHEMA}},
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": _media_type(image_bytes),
                                    "data": encoded,
                                },
                            },
                            {"type": "text", "text": self._prompt()},
                        ],
                    }
                ],
            )
        except anthropic.APIStatusError as exc:
            code = exc.status_code
            msg = (
                "Claude rate limit or quota exceeded — wait and retry, or check billing."
                if code == 429
                else f"Claude vision request failed ({code})."
            )
            raise VisionError(msg, status_code=429 if code == 429 else 502) from exc
        except anthropic.APIError as exc:
            raise VisionError("Claude vision request failed (connection error).", 502) from exc
        text = next(b.text for b in response.content if b.type == "text")
        payload = json.loads(text)
        detections = []
        for row in payload["detections"]:
            parsed = _ClaudeDetection(**row)
            freshness = (
                max(0.0, min(100.0, parsed.freshness))
                if parsed.freshness is not None
                else None
            )
            detections.append(
                Detection(
                    name=parsed.name,
                    category=parsed.category,
                    count=parsed.count,
                    confidence=max(0.0, min(1.0, parsed.confidence)),
                    freshness_score=freshness,
                )
            )
        return VisionResult(source=self.source, simulated=False, detections=detections)
