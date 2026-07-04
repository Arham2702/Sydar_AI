"""Unit tests for freshness scoring (frozen `now`, no DB)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.models.entities import FridgeItem
from app.models.enums import FreshnessLevel, FreshnessProfile
from app.services.freshness import (
    compute_freshness,
    freshness_from_visual_score,
    score_item,
)

NOW = datetime(2026, 7, 4, tzinfo=timezone.utc)


def _at_age(days: float):
    return NOW - timedelta(days=days)


def _uncatalogued(category: str, age_days: float) -> FridgeItem:
    return FridgeItem(name="Mystery", category=category, first_seen_at=_at_age(age_days))


def test_fresh_item_full_score():
    info = compute_freshness(_at_age(0), 10, FreshnessProfile.SLOW_PERISH, NOW)
    assert info.level == FreshnessLevel.FRESH
    assert info.score == 100
    assert info.days_remaining == 10.0


def test_aging_level_mid_life():
    # 6 days into a 10-day life -> 40% remaining -> AGING
    info = compute_freshness(_at_age(6), 10, FreshnessProfile.SLOW_PERISH, NOW)
    assert info.level == FreshnessLevel.AGING


def test_expiring_level_near_end():
    # 8 days into a 10-day life -> 20% remaining -> EXPIRING (<= 0.25 default)
    info = compute_freshness(_at_age(8), 10, FreshnessProfile.SLOW_PERISH, NOW)
    assert info.level == FreshnessLevel.EXPIRING


def test_expired_when_past_shelf_life():
    info = compute_freshness(_at_age(12), 10, FreshnessProfile.FAST_PERISH, NOW)
    assert info.level == FreshnessLevel.EXPIRED
    assert info.score == 0
    assert info.days_remaining < 0


def test_profile_shapes_score_not_level():
    # Same 60% remaining: fast-perish scores lower than shelf-stable.
    fast = compute_freshness(_at_age(4), 10, FreshnessProfile.FAST_PERISH, NOW)
    stable = compute_freshness(_at_age(4), 10, FreshnessProfile.SHELF_STABLE, NOW)
    assert fast.score < stable.score
    # Level is time-based, so both are the same band here.
    assert fast.level == stable.level == FreshnessLevel.FRESH


def test_expiring_threshold_is_configurable():
    # At 40% remaining, a 0.5 threshold flags EXPIRING where the default 0.25 wouldn't.
    info = compute_freshness(
        _at_age(6), 10, FreshnessProfile.SLOW_PERISH, NOW, expiring_threshold=0.5
    )
    assert info.level == FreshnessLevel.EXPIRING


def test_uncatalogued_item_uses_category_shelf_life():
    # Free-form "produce" detection -> 7-day fast-perish estimate.
    fresh = score_item(_uncatalogued("produce", age_days=1), catalog=None, now=NOW)
    assert fresh.days_remaining == 6.0
    assert fresh.level == FreshnessLevel.FRESH


def test_uncatalogued_meat_expires_quickly():
    # "meat" estimate is 3 days; 4 days old -> expired.
    fresh = score_item(_uncatalogued("meat", age_days=4), catalog=None, now=NOW)
    assert fresh.level == FreshnessLevel.EXPIRED


def test_unknown_category_falls_back_to_default():
    # An unrecognized category uses the generic 30-day shelf-stable default.
    fresh = score_item(_uncatalogued("gadgets", age_days=1), catalog=None, now=NOW)
    assert fresh.days_remaining == 29.0
    assert fresh.level == FreshnessLevel.FRESH


def test_visual_score_bands():
    assert freshness_from_visual_score(90, 10).level == FreshnessLevel.FRESH
    assert freshness_from_visual_score(50, 10).level == FreshnessLevel.AGING
    assert freshness_from_visual_score(25, 10).level == FreshnessLevel.EXPIRING
    assert freshness_from_visual_score(5, 10).level == FreshnessLevel.EXPIRED


def test_visual_score_projects_days_remaining():
    info = freshness_from_visual_score(20, 10)
    assert info.score == 20
    assert info.days_remaining == 2.0  # 10 days * 20%


def test_score_item_prefers_visual_freshness_over_age():
    # Just added (age 0 -> would be fully fresh by time), but visually spoiling.
    item = _uncatalogued("produce", age_days=0)
    item.visual_freshness = 20
    info = score_item(item, catalog=None, now=NOW)
    assert info.level == FreshnessLevel.EXPIRING  # visual estimate wins
    assert info.score == 20
    assert info.days_remaining == 1.4  # produce shelf life 7 * 20%


def test_naive_datetimes_are_handled():
    naive_now = datetime(2026, 7, 4)
    naive_seen = naive_now - timedelta(days=1)
    info = compute_freshness(naive_seen, 10, FreshnessProfile.SLOW_PERISH, naive_now)
    assert info.level == FreshnessLevel.FRESH
