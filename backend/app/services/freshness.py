"""Freshness scoring — pure, deterministic, time-based.

Freshness is derived on read from how long an item has been in the fridge
(age since ``first_seen_at``) versus its catalog shelf life, shaped by the
item's ``FreshnessProfile``. Nothing here touches the database, so it unit-tests
in isolation with a frozen ``now``.
"""
from __future__ import annotations

from datetime import datetime, timezone

from ..config import get_settings
from ..models.entities import CatalogItem, FridgeItem
from ..models.enums import FreshnessLevel, FreshnessProfile
from ..models.schemas import FreshnessInfo

# Shape of the score curve per profile. gamma > 1 makes the score fall faster
# early (fast-perishing feels "aging" sooner); gamma < 1 holds it high longer.
_PROFILE_GAMMA = {
    FreshnessProfile.FAST_PERISH: 1.6,
    FreshnessProfile.SLOW_PERISH: 1.0,
    FreshnessProfile.SHELF_STABLE: 0.7,
}

# Fallback shelf life for items with no catalog match.
_DEFAULT_SHELF_LIFE_DAYS = 30.0
_DEFAULT_PROFILE = FreshnessProfile.SHELF_STABLE

# When an item isn't in the curated catalog (e.g. free-form detections from a
# real vision model), estimate its shelf life + profile from the category the
# model assigned. Keeps freshness meaningful for "detect everything" uploads.
_CATEGORY_DEFAULTS: dict[str, tuple[float, FreshnessProfile]] = {
    "produce": (7.0, FreshnessProfile.FAST_PERISH),
    "vegetable": (7.0, FreshnessProfile.FAST_PERISH),
    "vegetables": (7.0, FreshnessProfile.FAST_PERISH),
    "fruit": (7.0, FreshnessProfile.FAST_PERISH),
    "fruits": (7.0, FreshnessProfile.FAST_PERISH),
    "meat": (3.0, FreshnessProfile.FAST_PERISH),
    "poultry": (3.0, FreshnessProfile.FAST_PERISH),
    "seafood": (2.0, FreshnessProfile.FAST_PERISH),
    "fish": (2.0, FreshnessProfile.FAST_PERISH),
    "dairy": (14.0, FreshnessProfile.SLOW_PERISH),
    "eggs": (21.0, FreshnessProfile.SLOW_PERISH),
    "leftovers": (4.0, FreshnessProfile.FAST_PERISH),
    "bakery": (5.0, FreshnessProfile.FAST_PERISH),
    "drinks": (14.0, FreshnessProfile.SHELF_STABLE),
    "drink": (14.0, FreshnessProfile.SHELF_STABLE),
    "beverage": (14.0, FreshnessProfile.SHELF_STABLE),
    "beverages": (14.0, FreshnessProfile.SHELF_STABLE),
    "condiment": (120.0, FreshnessProfile.SHELF_STABLE),
    "condiments": (120.0, FreshnessProfile.SHELF_STABLE),
    "sauce": (120.0, FreshnessProfile.SHELF_STABLE),
    "frozen": (90.0, FreshnessProfile.SHELF_STABLE),
}


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def compute_freshness(
    first_seen_at: datetime,
    shelf_life_days: float,
    profile: FreshnessProfile,
    now: datetime,
    expiring_threshold: float | None = None,
) -> FreshnessInfo:
    """Core scoring function. All inputs explicit for testability."""
    if expiring_threshold is None:
        expiring_threshold = get_settings().expiring_threshold

    # Normalize to timezone-aware UTC so naive/aware mixes don't raise.
    if first_seen_at.tzinfo is None:
        first_seen_at = first_seen_at.replace(tzinfo=timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    shelf_life_days = max(shelf_life_days, 0.01)
    age_days = (now - first_seen_at).total_seconds() / 86400.0
    remaining_days = shelf_life_days - age_days
    fraction = _clamp(remaining_days / shelf_life_days)

    gamma = _PROFILE_GAMMA.get(profile, 1.0)
    score = round((fraction**gamma) * 100)

    if remaining_days <= 0:
        level = FreshnessLevel.EXPIRED
        score = 0
    elif fraction <= expiring_threshold:
        level = FreshnessLevel.EXPIRING
    elif fraction <= 0.5:
        level = FreshnessLevel.AGING
    else:
        level = FreshnessLevel.FRESH

    return FreshnessInfo(
        score=int(score),
        level=level,
        days_remaining=round(remaining_days, 1),
    )


def freshness_from_visual_score(score: float, shelf_life_days: float) -> FreshnessInfo:
    """Build a FreshnessInfo from a vision model's 0-100 visual estimate.

    The score directly drives the level bands; ``days_remaining`` is projected
    from it and the item's shelf life so the UI meter/label stay meaningful.
    """
    score = _clamp(score, 0, 100)
    if score >= 70:
        level = FreshnessLevel.FRESH
    elif score >= 40:
        level = FreshnessLevel.AGING
    elif score >= 15:
        level = FreshnessLevel.EXPIRING
    else:
        level = FreshnessLevel.EXPIRED
    return FreshnessInfo(
        score=int(round(score)),
        level=level,
        days_remaining=round(shelf_life_days * score / 100, 1),
    )


def _resolve_shelf(
    item: FridgeItem, catalog: CatalogItem | None
) -> tuple[float, FreshnessProfile]:
    if catalog:
        return catalog.default_shelf_life_days, catalog.freshness_profile
    return _CATEGORY_DEFAULTS.get(
        (item.category or "").lower(), (_DEFAULT_SHELF_LIFE_DAYS, _DEFAULT_PROFILE)
    )


def score_item(
    item: FridgeItem,
    catalog: CatalogItem | None,
    now: datetime | None = None,
) -> FreshnessInfo:
    """Score a FridgeItem's freshness.

    Prefers a vision model's ``visual_freshness`` estimate when present;
    otherwise computes it from age vs. shelf life. Catalog items use their
    authored shelf life/profile; un-catalogued items fall back to a per-category
    estimate, then a generic default.
    """
    now = now or datetime.now(timezone.utc)
    shelf_life, profile = _resolve_shelf(item, catalog)
    if item.visual_freshness is not None:
        return freshness_from_visual_score(item.visual_freshness, shelf_life)
    return compute_freshness(item.first_seen_at, shelf_life, profile, now)
