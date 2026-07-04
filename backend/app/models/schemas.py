"""API response/request schemas (Pydantic).

Kept separate from the SQLModel tables so the HTTP contract can evolve
independently of the storage layer. See the ``api-schema`` skill for the
response-envelope conventions used by the routers.
"""
from __future__ import annotations

from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

from .enums import (
    AlertSeverity,
    AlertType,
    DetectionSource,
    FreshnessLevel,
    ItemStatus,
    ShoppingSource,
    ShoppingStatus,
)

T = TypeVar("T")


class Envelope(BaseModel, Generic[T]):
    """Standard success envelope: ``{"data": ..., "meta": {...}}``."""

    data: T
    meta: dict = {}


class FreshnessInfo(BaseModel):
    score: int  # 0-100
    level: FreshnessLevel
    days_remaining: float


class InventoryItemRead(BaseModel):
    id: int
    name: str
    category: str
    quantity: int
    unit: str
    status: ItemStatus
    first_seen_at: datetime
    last_seen_at: datetime
    freshness: FreshnessInfo


class InventoryAdjust(BaseModel):
    quantity: int


class DetectedItem(BaseModel):
    """A single item the vision pipeline saw in the captured frame."""

    name: str
    category: str
    count: int
    confidence: float
    freshness: Optional[int] = None  # visual 0-100 estimate, when the model gives one


class IngestResult(BaseModel):
    source: DetectionSource
    simulated: bool
    detections: int
    items_created: int
    items_updated: int
    items_depleted: int
    detected_items: list[DetectedItem] = []


class AlertRead(BaseModel):
    id: int
    fridge_item_id: int
    item_name: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    acknowledged: bool
    created_at: datetime


class IngredientStatus(BaseModel):
    name: str
    quantity: float
    unit: str
    optional: bool
    owned: bool
    owned_quantity: int


class RecipeSuggestion(BaseModel):
    id: int
    name: str
    description: str
    cuisine: str
    prep_minutes: int
    image_ref: Optional[str] = None
    match_score: float  # 0-1 fraction of required ingredients owned
    owned_count: int
    required_count: int
    uses_expiring: bool


class RecipeDetail(BaseModel):
    id: int
    name: str
    description: str
    cuisine: str
    prep_minutes: int
    image_ref: Optional[str] = None
    steps: list[str]
    ingredients: list[IngredientStatus]
    owned_count: int
    required_count: int
    missing: list[IngredientStatus]


class ShoppingItemRead(BaseModel):
    id: int
    name: str
    quantity: int
    unit: str
    source: ShoppingSource
    status: ShoppingStatus
    created_at: datetime


class ShoppingItemCreate(BaseModel):
    name: str
    quantity: int = 1
    unit: str = "count"


class ShoppingItemUpdate(BaseModel):
    status: Optional[ShoppingStatus] = None
    quantity: Optional[int] = None
