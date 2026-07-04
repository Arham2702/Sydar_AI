"""Unit tests for the deterministic mock vision provider."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.models.enums import DetectionSource
from app.vision.mock_provider import SAMPLES_DIR, MockVisionProvider


@pytest.fixture
def provider():
    return MockVisionProvider()


def test_lists_all_sample_scenes(provider):
    assert set(provider.available_samples()) == {
        "fridge_full",
        "fridge_low",
        "fridge_expiring",
    }


def test_named_sample_matches_fixture(provider):
    result = provider.analyze(b"", sample_name="fridge_full")
    raw = json.loads((SAMPLES_DIR / "fridge_full.expected.json").read_text())
    assert result.source == DetectionSource.MOCK_VISION
    assert result.simulated is True
    assert len(result.detections) == len(raw["detections"])
    assert result.detections[0].name == raw["detections"][0]["name"]


def test_unknown_sample_raises(provider):
    with pytest.raises(FileNotFoundError):
        provider.analyze(b"", sample_name="does_not_exist")


def test_bytes_hash_is_deterministic(provider):
    a = provider.analyze(b"some-image-bytes")
    b = provider.analyze(b"some-image-bytes")
    assert [d.name for d in a.detections] == [d.name for d in b.detections]


def test_sample_names_match_catalog():
    catalog = {
        c["name"]
        for c in json.loads(
            (Path(SAMPLES_DIR).parent / "app" / "seed" / "catalog.json").read_text()
        )
    }
    provider = MockVisionProvider()
    for scene in provider.available_samples():
        for det in provider.analyze(b"", sample_name=scene).detections:
            assert det.name in catalog, f"{det.name} in {scene} not in catalog"
