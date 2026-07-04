"""SQLModel table definitions — the persisted domain entities.

Relationships:
    CatalogItem 1─N FridgeItem
    FridgeItem  1─N InventoryEvent
    FridgeItem  1─N Alert
    Recipe      1─N RecipeIngredient
    RecipeIngredient N─1 CatalogItem (nullable)
    ShoppingListItem N─1 CatalogItem (nullable, free-text manual adds allowed)
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import JSON, Column, Field, SQLModel

from .enums import (
    AlertSeverity,
    AlertType,
    DetectionSource,
    EventType,
    FreshnessProfile,
    ItemStatus,
    ShoppingSource,
    ShoppingStatus,
)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CatalogItem(SQLModel, table=True):
    """Reference knowledge for a known food: shelf life + thresholds.

    Seeded from ``app/seed/catalog.json``. Drives freshness scoring and the
    low-stock threshold used by the shopping list.
    """

    __tablename__ = "catalog_item"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    category: str
    default_shelf_life_days: float
    freshness_profile: FreshnessProfile
    low_stock_threshold: int = 1
    unit: str = "count"


class FridgeItem(SQLModel, table=True):
    """An item currently or previously tracked in the fridge."""

    __tablename__ = "fridge_item"

    id: Optional[int] = Field(default=None, primary_key=True)
    catalog_item_id: Optional[int] = Field(default=None, foreign_key="catalog_item.id")
    name: str = Field(index=True)
    category: str
    quantity: int = 0
    unit: str = "count"
    first_seen_at: datetime = Field(default_factory=utcnow)
    last_seen_at: datetime = Field(default_factory=utcnow)
    added_at: datetime = Field(default_factory=utcnow)
    status: ItemStatus = ItemStatus.ACTIVE
    # Visual freshness (0-100) from a vision model; when set, freshness scoring
    # uses it instead of the time-based estimate. None -> time-based.
    visual_freshness: Optional[int] = None


class InventoryEvent(SQLModel, table=True):
    """Append-only audit log of every change to a fridge item."""

    __tablename__ = "inventory_event"

    id: Optional[int] = Field(default=None, primary_key=True)
    fridge_item_id: int = Field(foreign_key="fridge_item.id", index=True)
    event_type: EventType
    quantity_delta: int = 0
    source: DetectionSource = DetectionSource.MANUAL
    created_at: datetime = Field(default_factory=utcnow)
    raw_detection: Optional[dict] = Field(default=None, sa_column=Column(JSON))


class Alert(SQLModel, table=True):
    __tablename__ = "alert"

    id: Optional[int] = Field(default=None, primary_key=True)
    fridge_item_id: int = Field(foreign_key="fridge_item.id", index=True)
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    created_at: datetime = Field(default_factory=utcnow)
    acknowledged: bool = False


class Recipe(SQLModel, table=True):
    __tablename__ = "recipe"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: str = ""
    cuisine: str = ""
    prep_minutes: int = 0
    steps: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    image_ref: Optional[str] = None


class RecipeIngredient(SQLModel, table=True):
    __tablename__ = "recipe_ingredient"

    id: Optional[int] = Field(default=None, primary_key=True)
    recipe_id: int = Field(foreign_key="recipe.id", index=True)
    catalog_item_id: Optional[int] = Field(default=None, foreign_key="catalog_item.id")
    name: str
    quantity: float = 1
    unit: str = "count"
    optional: bool = False


class ShoppingListItem(SQLModel, table=True):
    __tablename__ = "shopping_list_item"

    id: Optional[int] = Field(default=None, primary_key=True)
    catalog_item_id: Optional[int] = Field(default=None, foreign_key="catalog_item.id")
    name: str = Field(index=True)
    quantity: int = 1
    unit: str = "count"
    source: ShoppingSource = ShoppingSource.MANUAL
    status: ShoppingStatus = ShoppingStatus.NEEDED
    created_at: datetime = Field(default_factory=utcnow)
