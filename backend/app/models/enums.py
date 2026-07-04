"""Enumerations shared across the domain model."""
from __future__ import annotations

from enum import Enum


class FreshnessProfile(str, Enum):
    """How quickly a food category loses freshness."""

    FAST_PERISH = "fast_perish"  # leafy greens, berries, raw fish
    SLOW_PERISH = "slow_perish"  # root veg, dairy, eggs
    SHELF_STABLE = "shelf_stable"  # condiments, drinks


class FreshnessLevel(str, Enum):
    FRESH = "fresh"
    AGING = "aging"
    EXPIRING = "expiring"
    EXPIRED = "expired"


class ItemStatus(str, Enum):
    ACTIVE = "active"
    DEPLETED = "depleted"
    REMOVED = "removed"


class EventType(str, Enum):
    DETECTED = "detected"
    ADDED = "added"
    DECREMENTED = "decremented"
    REMOVED = "removed"
    MANUAL_ADJUST = "manual_adjust"


class DetectionSource(str, Enum):
    MOCK_VISION = "mock_vision"
    CLAUDE_VISION = "claude_vision"
    GEMINI_VISION = "gemini_vision"
    MANUAL = "manual"


class AlertType(str, Enum):
    EXPIRING = "expiring"
    EXPIRED = "expired"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ShoppingSource(str, Enum):
    AUTO_LOW_STOCK = "auto_low_stock"
    AUTO_OUT = "auto_out"
    MANUAL = "manual"


class ShoppingStatus(str, Enum):
    NEEDED = "needed"
    PURCHASED = "purchased"
