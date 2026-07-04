"""Database engine, session management, and one-time initialization/seeding."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine, select

from .config import get_settings
from .models import CatalogItem, Recipe, RecipeIngredient
from .models.enums import FreshnessProfile

SEED_DIR = Path(__file__).parent / "seed"

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        url = get_settings().database_url
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        _engine = create_engine(url, connect_args=connect_args)
    return _engine


def set_engine(engine) -> None:
    """Override the module engine (used by tests with in-memory SQLite)."""
    global _engine
    _engine = engine


def init_db(seed: bool = True) -> None:
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
    if seed:
        with Session(engine) as session:
            seed_catalog(session)
            seed_recipes(session)


def get_session() -> Iterator[Session]:
    with Session(get_engine()) as session:
        yield session


def seed_catalog(session: Session) -> None:
    """Load the curated food catalog if the table is empty (idempotent)."""
    if session.exec(select(CatalogItem)).first() is not None:
        return
    data = json.loads((SEED_DIR / "catalog.json").read_text())
    for row in data:
        session.add(
            CatalogItem(
                name=row["name"],
                category=row["category"],
                default_shelf_life_days=row["default_shelf_life_days"],
                freshness_profile=FreshnessProfile(row["freshness_profile"]),
                low_stock_threshold=row.get("low_stock_threshold", 1),
                unit=row.get("unit", "count"),
            )
        )
    session.commit()


def seed_recipes(session: Session) -> None:
    """Load the curated recipe dataset if empty (idempotent)."""
    if session.exec(select(Recipe)).first() is not None:
        return
    catalog = {c.name: c.id for c in session.exec(select(CatalogItem)).all()}
    data = json.loads((SEED_DIR / "recipes.json").read_text())
    for row in data:
        recipe = Recipe(
            name=row["name"],
            description=row.get("description", ""),
            cuisine=row.get("cuisine", ""),
            prep_minutes=row.get("prep_minutes", 0),
            steps=row.get("steps", []),
            image_ref=row.get("image_ref"),
        )
        session.add(recipe)
        session.flush()  # assign recipe.id
        for ing in row["ingredients"]:
            session.add(
                RecipeIngredient(
                    recipe_id=recipe.id,
                    catalog_item_id=catalog.get(ing["name"]),
                    name=ing["name"],
                    quantity=ing.get("quantity", 1),
                    unit=ing.get("unit", "count"),
                    optional=ing.get("optional", False),
                )
            )
    session.commit()
