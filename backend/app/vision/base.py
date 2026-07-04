"""Vision provider contract.

A ``VisionProvider`` turns raw image bytes into a list of ``Detection`` objects.
The rest of the platform (reconciliation, inventory, freshness, ...) depends only
on this contract, so swapping the mock for a real model changes nothing
downstream. See the ``vision-pipeline`` skill for conventions on adding providers
and labeled samples.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from ..models.enums import DetectionSource


class VisionError(Exception):
    """A recoverable failure from a real vision provider (quota, rate limit,
    auth, network). Carries an HTTP status so the API can surface it cleanly
    instead of leaking a raw SDK traceback."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class Detection(BaseModel):
    """One recognized food item in a captured frame."""

    name: str
    category: str
    count: int = Field(ge=0)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    bbox: list[float] | None = None  # [x, y, w, h] normalized, optional
    # SIMULATION-ONLY hint: how long (days) this item has already been in the
    # fridge. Real providers cannot know this and leave it None; mock scenes set
    # it so freshness decay and expiry alerts are demonstrable without waiting
    # real days. Reconciliation uses it to backdate first_seen_at on creation.
    sim_age_days: float | None = None
    # Visual freshness estimate (0-100) judged by a real vision model from the
    # item's appearance (bruising, mould, wilting, discolouration). When set it
    # overrides the time-based freshness estimate. Mock/manual sources leave None.
    freshness_score: float | None = None


class VisionResult(BaseModel):
    """Structured output of a single frame analysis."""

    source: DetectionSource
    simulated: bool
    detections: list[Detection]


def merge_detections(detections: list[Detection]) -> list[Detection]:
    """Collapse detections of the same item within one capture.

    Vision models sometimes emit the same item type as several rows (an
    aggregate ``x4`` plus per-instance ``x1`` rows). Without merging, the
    reconciler's per-name upsert lets the last row silently overwrite the rest.
    We keep the largest count seen for a name (its best whole-count estimate)
    and the *worst* freshness (so visible spoilage isn't hidden by a pristine
    duplicate). Order is preserved.
    """
    merged: dict[str, Detection] = {}
    order: list[str] = []
    for det in detections:
        key = det.name.strip().lower()
        if key not in merged:
            merged[key] = det.model_copy(deep=True)
            order.append(key)
            continue
        current = merged[key]
        current.count = max(current.count, det.count)
        current.confidence = max(current.confidence, det.confidence)
        if det.freshness_score is not None:
            current.freshness_score = (
                det.freshness_score
                if current.freshness_score is None
                else min(current.freshness_score, det.freshness_score)
            )
        if det.sim_age_days is not None:
            current.sim_age_days = (
                det.sim_age_days
                if current.sim_age_days is None
                else max(current.sim_age_days, det.sim_age_days)
            )
    return [merged[k] for k in order]


class VisionProvider(ABC):
    """Abstract base for all image -> detections engines."""

    source: DetectionSource
    simulated: bool

    @abstractmethod
    def analyze(self, image_bytes: bytes, *, sample_name: str | None = None) -> VisionResult:
        """Analyze a frame and return structured detections.

        ``sample_name`` lets fixture-backed providers (the mock) resolve a
        labeled sample without needing to actually decode pixels.
        """
        raise NotImplementedError
