"""Unit tests for Gemini response parsing (no SDK / network needed).

The live ``analyze`` call is exercised manually with a real key; here we cover
the pure ``parse_detections`` helper that turns Gemini's JSON into Detections.
"""
from __future__ import annotations

import json

from app.vision.base import VisionError
from app.vision.gemini_provider import _to_vision_error, parse_detections


class _FakeApiError(Exception):
    def __init__(self, code):
        self.code = code


def test_quota_error_maps_to_429():
    err = _to_vision_error(_FakeApiError(429))
    assert isinstance(err, VisionError)
    assert err.status_code == 429
    assert "quota" in err.message.lower() or "rate limit" in err.message.lower()


def test_auth_error_maps_to_502():
    assert _to_vision_error(_FakeApiError(403)).status_code == 502


def test_unknown_error_maps_to_502():
    assert _to_vision_error(_FakeApiError(None)).status_code == 502


def test_parses_top_level_array():
    text = json.dumps(
        [
            {"name": "Milk", "category": "dairy", "count": 1, "confidence": 0.97},
            {"name": "Eggs", "category": "dairy", "count": 6, "confidence": 0.9},
        ]
    )
    dets = parse_detections(text)
    assert [d.name for d in dets] == ["Milk", "Eggs"]
    assert dets[0].count == 1
    assert dets[0].confidence == 0.97


def test_parses_wrapped_object():
    text = json.dumps({"detections": [{"name": "Tomatoes", "category": "produce", "count": 3}]})
    dets = parse_detections(text)
    assert len(dets) == 1
    assert dets[0].confidence == 1.0  # default when omitted


def test_skips_malformed_rows_and_zero_counts():
    text = json.dumps(
        [
            {"name": "Milk", "category": "dairy", "count": 2},
            {"name": "Bad"},  # missing required fields -> skipped
            {"name": "Empty", "category": "dairy", "count": 0},  # zero -> skipped
        ]
    )
    dets = parse_detections(text)
    assert [d.name for d in dets] == ["Milk"]


def test_clamps_confidence():
    text = json.dumps([{"name": "Milk", "category": "dairy", "count": 1, "confidence": 5}])
    assert parse_detections(text)[0].confidence == 1.0


def test_empty_text_returns_empty_list():
    assert parse_detections("") == []
    assert parse_detections("   ") == []


def test_parses_and_clamps_visual_freshness():
    text = json.dumps(
        [
            {"name": "Tomatoes", "category": "produce", "count": 2, "freshness": 25},
            {"name": "Milk", "category": "dairy", "count": 1, "freshness": 150},
            {"name": "Eggs", "category": "dairy", "count": 6},
        ]
    )
    dets = parse_detections(text)
    assert dets[0].freshness_score == 25
    assert dets[1].freshness_score == 100  # clamped to 100
    assert dets[2].freshness_score is None  # omitted -> None
