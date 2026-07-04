"""Recipe matching engine.

Scores seed recipes against current inventory: what fraction of a recipe's
required ingredients you own, with a bonus for recipes that use soon-to-expire
items (to reduce waste). Also builds the detailed owned-vs-missing view.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from ..models.entities import CatalogItem, FridgeItem, Recipe, RecipeIngredient, utcnow
from ..models.enums import FreshnessLevel, ItemStatus
from ..models.schemas import IngredientStatus, RecipeDetail, RecipeSuggestion
from .freshness import score_item

_EXPIRING_LEVELS = {FreshnessLevel.EXPIRING, FreshnessLevel.EXPIRED}


def _inventory_index(
    session: Session, now: datetime
) -> tuple[dict[int, dict], dict[str, dict]]:
    """Index in-stock items by catalog id and by lowercased name."""
    by_catalog: dict[int, dict] = {}
    by_name: dict[str, dict] = {}
    stmt = select(FridgeItem).where(
        FridgeItem.status == ItemStatus.ACTIVE, FridgeItem.quantity > 0
    )
    for item in session.exec(stmt):
        catalog = (
            session.get(CatalogItem, item.catalog_item_id) if item.catalog_item_id else None
        )
        fresh = score_item(item, catalog, now)
        info = {"quantity": item.quantity, "level": fresh.level}
        if item.catalog_item_id:
            by_catalog[item.catalog_item_id] = info
        by_name[item.name.lower()] = info
    return by_catalog, by_name


def _owned(ing: RecipeIngredient, by_catalog: dict, by_name: dict) -> Optional[dict]:
    if ing.catalog_item_id and ing.catalog_item_id in by_catalog:
        return by_catalog[ing.catalog_item_id]
    return by_name.get(ing.name.lower())


def _ingredients(session: Session, recipe_id: int) -> list[RecipeIngredient]:
    return list(
        session.exec(select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe_id))
    )


def suggestions(session: Session, now: datetime | None = None) -> list[RecipeSuggestion]:
    now = now or utcnow()
    by_catalog, by_name = _inventory_index(session, now)
    results: list[RecipeSuggestion] = []

    for recipe in session.exec(select(Recipe)):
        ingredients = _ingredients(session, recipe.id)
        required = [i for i in ingredients if not i.optional]
        owned_required = 0
        uses_expiring = False
        for ing in ingredients:
            info = _owned(ing, by_catalog, by_name)
            if info:
                if not ing.optional:
                    owned_required += 1
                if info["level"] in _EXPIRING_LEVELS:
                    uses_expiring = True
        required_count = len(required)
        score = owned_required / required_count if required_count else 1.0
        results.append(
            RecipeSuggestion(
                id=recipe.id,
                name=recipe.name,
                description=recipe.description,
                cuisine=recipe.cuisine,
                prep_minutes=recipe.prep_minutes,
                image_ref=recipe.image_ref,
                match_score=round(score, 3),
                owned_count=owned_required,
                required_count=required_count,
                uses_expiring=uses_expiring,
            )
        )

    # Best matches first; break ties toward using expiring items, then quick recipes.
    results.sort(key=lambda r: (-r.match_score, not r.uses_expiring, r.prep_minutes))
    return results


def detail(session: Session, recipe: Recipe, now: datetime | None = None) -> RecipeDetail:
    now = now or utcnow()
    by_catalog, by_name = _inventory_index(session, now)
    statuses: list[IngredientStatus] = []
    owned_required = 0
    required_count = 0

    for ing in _ingredients(session, recipe.id):
        info = _owned(ing, by_catalog, by_name)
        owned = info is not None
        if not ing.optional:
            required_count += 1
            if owned:
                owned_required += 1
        statuses.append(
            IngredientStatus(
                name=ing.name,
                quantity=ing.quantity,
                unit=ing.unit,
                optional=ing.optional,
                owned=owned,
                owned_quantity=info["quantity"] if info else 0,
            )
        )

    missing = [s for s in statuses if not s.owned]
    return RecipeDetail(
        id=recipe.id,
        name=recipe.name,
        description=recipe.description,
        cuisine=recipe.cuisine,
        prep_minutes=recipe.prep_minutes,
        image_ref=recipe.image_ref,
        steps=recipe.steps,
        ingredients=statuses,
        owned_count=owned_required,
        required_count=required_count,
        missing=missing,
    )
