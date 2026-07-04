"""Deterministic, fixture-driven vision provider.

Simulates the not-yet-existing camera feed. Every labeled sample image in
``backend/samples/`` has a sibling ``<name>.expected.json`` describing the items
a real model *would* detect in that scene. Given a ``sample_name`` we return
that fixture verbatim; given raw bytes with no name we hash them to pick a
labeled scene reproducibly. Output is always marked ``simulated=True`` so the
API and UI can label it honestly as mock data.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ..models.enums import DetectionSource
from .base import Detection, VisionProvider, VisionResult

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "samples"


class MockVisionProvider(VisionProvider):
    source = DetectionSource.MOCK_VISION
    simulated = True

    def __init__(self, samples_dir: Path | None = None):
        self.samples_dir = samples_dir or SAMPLES_DIR

    def available_samples(self) -> list[str]:
        return sorted(p.stem.replace(".expected", "") for p in self.samples_dir.glob("*.expected.json"))

    def _fixture_path(self, sample_name: str) -> Path:
        return self.samples_dir / f"{sample_name}.expected.json"

    def _resolve_sample(self, image_bytes: bytes | None, sample_name: str | None) -> str:
        if sample_name:
            if not self._fixture_path(sample_name).exists():
                raise FileNotFoundError(f"Unknown sample '{sample_name}'")
            return sample_name
        samples = self.available_samples()
        if not samples:
            raise FileNotFoundError("No sample fixtures available")
        if not image_bytes:
            return samples[0]
        # Deterministically map arbitrary uploaded bytes to one labeled scene.
        digest = int(hashlib.sha256(image_bytes).hexdigest(), 16)
        return samples[digest % len(samples)]

    def analyze(self, image_bytes: bytes, *, sample_name: str | None = None) -> VisionResult:
        name = self._resolve_sample(image_bytes, sample_name)
        raw = json.loads(self._fixture_path(name).read_text())
        detections = [Detection(**d) for d in raw["detections"]]
        return VisionResult(source=self.source, simulated=True, detections=detections)
