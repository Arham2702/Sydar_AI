"""Real vision provider backed by Google Gemini.

Sends a fridge image to a Gemini model (default ``gemini-2.5-flash-lite``) and
asks for structured detections of *every* item it sees (not limited to the
curated catalog — catalog names are passed only as a naming hint so known items
still link to recipes/freshness data). Activated when a Google API key is present
(see ``config.resolved_provider``); the offline ``MockVisionProvider`` remains
the default so dev and tests need no network.

The response-parsing (`parse_detections`) is a pure function so it can be
unit-tested without the SDK or a live API. The ``analyze`` network call itself
is excluded from the coverage gate and exercised manually with a real key.
"""
from __future__ import annotations

import json

from pydantic import BaseModel

from ..config import get_settings
from ..models.enums import DetectionSource
from .base import Detection, VisionError, VisionProvider, VisionResult


class _GeminiDetection(BaseModel):
    name: str
    category: str
    count: int
    confidence: float = 1.0
    freshness: float | None = None  # 0-100 visual freshness estimate


def _media_type(image_bytes: bytes) -> str:
    if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if image_bytes[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


def _to_vision_error(exc: object) -> VisionError:
    """Map a Gemini SDK APIError to a clean, user-facing VisionError."""
    code = getattr(exc, "code", None) or 502
    if code == 429:
        return VisionError(
            "Gemini rate limit or quota exceeded. The free tier allows only a small number "
            "of requests per day for this model — wait a bit and retry, reduce usage by "
            "setting FRIDGE_RECIPE_SEARCH=false, or enable billing. "
            "See https://ai.google.dev/gemini-api/docs/rate-limits.",
            status_code=429,
        )
    if code in (401, 403):
        return VisionError(
            "Gemini rejected the request — check that GOOGLE_API_KEY is valid.",
            status_code=502,
        )
    return VisionError(f"Gemini vision request failed ({code}).", status_code=502)


def parse_detections(text: str) -> list[Detection]:
    """Turn a Gemini JSON response into validated ``Detection`` objects.

    Accepts either a top-level array or a ``{"detections": [...]}`` object,
    skips malformed rows, and clamps confidence to [0, 1]. Pure + testable.
    """
    if not text or not text.strip():
        return []
    payload = json.loads(text)
    rows = payload.get("detections", []) if isinstance(payload, dict) else payload

    detections: list[Detection] = []
    for row in rows:
        try:
            parsed = _GeminiDetection(**row)
        except (TypeError, ValueError):
            continue
        if parsed.count <= 0:
            continue
        freshness = (
            max(0.0, min(100.0, parsed.freshness)) if parsed.freshness is not None else None
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
    return detections


class GeminiVisionProvider(VisionProvider):
    source = DetectionSource.GEMINI_VISION
    simulated = False

    def __init__(self, catalog_names: list[str] | None = None):
        self.settings = get_settings()
        self.catalog_names = catalog_names or []

    def _prompt(self) -> str:
        hint = ""
        if self.catalog_names:
            # Not a constraint — just a nudge to reuse canonical names when an
            # item clearly matches one, so it links to existing recipes/data.
            hint = (
                " When an item clearly matches one of these known names, reuse that exact "
                f"name: {', '.join(self.catalog_names)}."
            )
        return (
            "You are the vision system for a smart fridge. Look at this photo and identify "
            "EVERY distinct food or drink item you can see — do not limit yourself to any "
            "predefined list. Return exactly ONE object per distinct item type (e.g. all "
            "tomatoes in one object), never multiple objects for the same type. For each "
            "item return: name (a concise common name), category (one of: dairy, produce, "
            "meat, seafood, drinks, condiment, bakery, leftovers, frozen, other), count "
            "(integer TOTAL number of that item visible), confidence (0-1), and freshness "
            "(integer 1-100 estimating how fresh and edible the item looks from its VISUAL "
            "state — 100 = perfect/pristine, lower as you see bruising, browning, black "
            "spots, mould, wilting, or discolouration; e.g. a tomato with black spots is "
            "~10-40. When items of the same type vary in condition, report the freshness of "
            "the WORST-looking ones)." + hint + " Only include items you can actually see. "
            "Return only a JSON array of these objects."
        )

    def analyze(self, image_bytes: bytes, *, sample_name: str | None = None) -> VisionResult:
        # Imported lazily so the default mock path needs no SDK/network.
        from google import genai
        from google.genai import errors, types

        client = genai.Client(api_key=self.settings.google_key())
        try:
            response = client.models.generate_content(
                model=self.settings.gemini_model,
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes, mime_type=_media_type(image_bytes)
                    ),
                    self._prompt(),
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=list[_GeminiDetection],
                    temperature=0.0,
                ),
            )
        except errors.APIError as exc:
            raise _to_vision_error(exc) from exc
        detections = parse_detections(response.text or "")
        return VisionResult(source=self.source, simulated=False, detections=detections)
