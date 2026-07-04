"""Unit tests for recipe matching and owned/missing detail."""
from __future__ import annotations

from sqlmodel import select

from app.models.entities import Recipe
from app.models.enums import DetectionSource
from app.services import inventory, recipes
from app.vision.base import Detection

SRC = DetectionSource.MOCK_VISION


def _det(name, category, count, age=None):
    return Detection(name=name, category=category, count=count, sim_age_days=age)


def _suggestion(session, name):
    return next(s for s in recipes.suggestions(session) if s.name == name)


def test_empty_inventory_scores_zero(session):
    grilled = _suggestion(session, "Grilled Cheese Sandwich")
    assert grilled.match_score == 0.0
    assert grilled.owned_count == 0


def test_full_ownership_scores_one(session):
    # Grilled Cheese needs Cheddar Cheese + Butter.
    inventory.reconcile(
        session,
        [_det("Cheddar Cheese", "dairy", 1), _det("Butter", "dairy", 1)],
        SRC,
    )
    grilled = _suggestion(session, "Grilled Cheese Sandwich")
    assert grilled.match_score == 1.0
    assert grilled.owned_count == grilled.required_count == 2


def test_partial_ownership_fraction(session):
    inventory.reconcile(session, [_det("Butter", "dairy", 1)], SRC)
    grilled = _suggestion(session, "Grilled Cheese Sandwich")
    assert grilled.match_score == 0.5  # 1 of 2 required


def test_optional_ingredient_not_counted_as_required(session):
    # Garden Salad: lettuce, tomatoes, carrots required; bell peppers optional.
    inventory.reconcile(
        session,
        [
            _det("Lettuce", "produce", 1),
            _det("Tomatoes", "produce", 2),
            _det("Carrots", "produce", 1),
        ],
        SRC,
    )
    salad = _suggestion(session, "Garden Salad")
    assert salad.required_count == 3
    assert salad.match_score == 1.0


def test_uses_expiring_flag(session):
    # Lettuce shelf life 6; age 5 -> expiring, and Garden Salad uses it.
    inventory.reconcile(session, [_det("Lettuce", "produce", 1, age=5)], SRC)
    salad = _suggestion(session, "Garden Salad")
    assert salad.uses_expiring is True


def test_suggestions_sorted_by_score(session):
    inventory.reconcile(session, [_det("Butter", "dairy", 1)], SRC)
    scores = [s.match_score for s in recipes.suggestions(session)]
    assert scores == sorted(scores, reverse=True)


def test_detail_owned_and_missing(session):
    inventory.reconcile(session, [_det("Butter", "dairy", 1)], SRC)
    grilled = session.exec(
        select(Recipe).where(Recipe.name == "Grilled Cheese Sandwich")
    ).one()
    detail = recipes.detail(session, grilled)
    owned = {i.name for i in detail.ingredients if i.owned}
    missing = {m.name for m in detail.missing}
    assert "Butter" in owned
    assert "Cheddar Cheese" in missing
