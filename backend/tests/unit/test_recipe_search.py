"""Unit tests for dynamic recipe search (pure parsing + DB replacement).

The live Gemini call (`generate_recipes`) is monkeypatched so these run offline.
"""
from __future__ import annotations

import json

from sqlmodel import select

from app.models.entities import Recipe, RecipeIngredient
from app.services import recipe_search


def test_parse_recipes_array_and_wrapped():
    data = [
        {
            "name": "Omelette",
            "cuisine": "Breakfast",
            "prep_minutes": 10,
            "ingredients": [{"name": "Eggs", "quantity": 3, "unit": "count"}],
        }
    ]
    assert len(recipe_search.parse_recipes(json.dumps(data))) == 1
    assert len(recipe_search.parse_recipes(json.dumps({"recipes": data}))) == 1


def test_parse_recipes_skips_incomplete():
    data = [
        {"name": "No ingredients"},  # no ingredients -> skipped
        {"ingredients": [{"name": "Eggs"}]},  # no name -> skipped
    ]
    assert recipe_search.parse_recipes(json.dumps(data)) == []


def test_parse_recipes_empty():
    assert recipe_search.parse_recipes("") == []


def test_replace_recipes_swaps_tables_and_links_catalog(session):
    # Seeded DB starts with the 12 seed recipes.
    assert len(session.exec(select(Recipe)).all()) == 12

    generated = recipe_search.parse_recipes(
        json.dumps(
            [
                {
                    "name": "Quick Scramble",
                    "cuisine": "Breakfast",
                    "prep_minutes": 8,
                    "steps": ["Whisk", "Cook"],
                    "ingredients": [
                        {"name": "Eggs", "quantity": 3, "unit": "count"},  # in catalog
                        {"name": "Chives", "quantity": 1, "unit": "sprig"},  # not in catalog
                    ],
                }
            ]
        )
    )
    count = recipe_search.replace_recipes(session, generated)
    assert count == 1

    recipes = session.exec(select(Recipe)).all()
    assert len(recipes) == 1
    assert recipes[0].name == "Quick Scramble"

    ings = {i.name: i for i in session.exec(select(RecipeIngredient)).all()}
    assert ings["Eggs"].catalog_item_id is not None  # linked to catalog
    assert ings["Chives"].catalog_item_id is None  # free-form, unlinked


def test_replace_recipes_noop_on_empty(session):
    before = len(session.exec(select(Recipe)).all())
    assert recipe_search.replace_recipes(session, []) == 0
    assert len(session.exec(select(Recipe)).all()) == before


def test_refresh_from_inventory_uses_generator(session, monkeypatch):
    fake = recipe_search.parse_recipes(
        json.dumps([{"name": "Toast", "ingredients": [{"name": "Bread"}]}])
    )
    monkeypatch.setattr(recipe_search, "generate_recipes", lambda names: fake)
    assert recipe_search.refresh_from_inventory(session, ["Bread"]) == 1
    assert session.exec(select(Recipe)).one().name == "Toast"


def test_refresh_from_inventory_survives_failures(session, monkeypatch):
    def boom(names):
        raise RuntimeError("gemini down")

    monkeypatch.setattr(recipe_search, "generate_recipes", boom)
    before = len(session.exec(select(Recipe)).all())
    assert recipe_search.refresh_from_inventory(session, ["Bread"]) == 0
    assert len(session.exec(select(Recipe)).all()) == before  # unchanged
