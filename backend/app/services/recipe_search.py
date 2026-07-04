"""Dynamic recipe search from current inventory (Gemini-backed).

Instead of a fixed seed list, when a Google API key is present we ask Gemini to
propose recipes that best use what's actually in the fridge. The generated
recipes replace the ``Recipe``/``RecipeIngredient`` tables, so the existing
``services.recipes`` matching (owned-ingredient %, sorted descending) and the
recipe-detail endpoint work unchanged. With no key, the seeded recipes remain as
the offline fallback.

``parse_recipes`` is a pure function so it can be unit-tested without the SDK.
The live ``generate_recipes`` call is excluded from the coverage gate.
"""
from __future__ import annotations

import json

from pydantic import BaseModel
from sqlmodel import Session, delete, select

from ..config import get_settings
from ..models.entities import CatalogItem, Recipe, RecipeIngredient


class GeneratedIngredient(BaseModel):
    name: str
    quantity: float = 1
    unit: str = "count"


class GeneratedRecipe(BaseModel):
    name: str
    cuisine: str = ""
    prep_minutes: int = 0
    description: str = ""
    steps: list[str] = []
    ingredients: list[GeneratedIngredient] = []


def search_enabled() -> bool:
    """Dynamic search runs when a Gemini key is configured and it's not disabled."""
    settings = get_settings()
    return settings.recipe_search and settings.google_key() is not None


def parse_recipes(text: str) -> list[GeneratedRecipe]:
    """Validate Gemini's JSON into recipes, skipping malformed / empty ones."""
    if not text or not text.strip():
        return []
    payload = json.loads(text)
    rows = payload.get("recipes", []) if isinstance(payload, dict) else payload
    recipes: list[GeneratedRecipe] = []
    for row in rows:
        try:
            recipe = GeneratedRecipe(**row)
        except (TypeError, ValueError):
            continue
        if recipe.name and recipe.ingredients:
            recipes.append(recipe)
    return recipes


def generate_recipes(inventory_names: list[str]) -> list[GeneratedRecipe]:  # pragma: no cover
    """Ask Gemini for recipes that best match the current inventory."""
    from google import genai
    from google.genai import types

    settings = get_settings()
    client = genai.Client(api_key=settings.google_key())
    have = ", ".join(inventory_names) if inventory_names else "an empty fridge"
    prompt = (
        "A user's fridge currently contains: " + have + ". Suggest 8 realistic recipes "
        "that best use these ingredients, prioritising recipes where most ingredients are "
        "already available. For each recipe return: name, cuisine, prep_minutes (integer), "
        "description (one sentence), steps (list of strings), and ingredients (each with "
        "name, quantity, unit). Use ingredient names that match the fridge items where "
        "possible. Return only a JSON array of recipe objects."
    )
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[GeneratedRecipe],
            temperature=0.4,
        ),
    )
    return parse_recipes(response.text or "")


def replace_recipes(session: Session, recipes: list[GeneratedRecipe]) -> int:
    """Replace all stored recipes with the given set. Returns the count stored."""
    if not recipes:
        return 0
    session.exec(delete(RecipeIngredient))
    session.exec(delete(Recipe))
    catalog = {c.name.lower(): c.id for c in session.exec(select(CatalogItem)).all()}
    for gen in recipes:
        recipe = Recipe(
            name=gen.name,
            description=gen.description,
            cuisine=gen.cuisine,
            prep_minutes=gen.prep_minutes,
            steps=gen.steps,
        )
        session.add(recipe)
        session.flush()
        for ing in gen.ingredients:
            session.add(
                RecipeIngredient(
                    recipe_id=recipe.id,
                    catalog_item_id=catalog.get(ing.name.lower()),
                    name=ing.name,
                    quantity=ing.quantity,
                    unit=ing.unit,
                )
            )
    session.commit()
    return len(recipes)


def refresh_from_inventory(session: Session, inventory_names: list[str]) -> int:
    """Generate recipes for the current inventory and store them.

    Best-effort: on any failure the existing recipes are left untouched.
    """
    try:
        recipes = generate_recipes(inventory_names)
    except Exception:  # noqa: BLE001 — never let recipe search break ingest
        return 0
    return replace_recipes(session, recipes)
