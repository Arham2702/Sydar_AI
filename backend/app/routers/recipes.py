"""Recipe endpoints — ranked suggestions and detailed owned/missing view."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..db import get_session
from ..models.entities import Recipe
from ..models.schemas import Envelope, RecipeDetail, RecipeSuggestion, ShoppingItemRead
from ..services import recipes as recipes_service
from ..services import shopping

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


@router.get("/suggestions", response_model=Envelope[list[RecipeSuggestion]])
def list_suggestions(
    session: Session = Depends(get_session),
) -> Envelope[list[RecipeSuggestion]]:
    data = recipes_service.suggestions(session)
    return Envelope(data=data, meta={"count": len(data)})


@router.get("/{recipe_id}", response_model=Envelope[RecipeDetail])
def get_recipe(recipe_id: int, session: Session = Depends(get_session)) -> Envelope[RecipeDetail]:
    recipe = session.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return Envelope(data=recipes_service.detail(session, recipe))


@router.post("/{recipe_id}/add-missing", response_model=Envelope[list[ShoppingItemRead]])
def add_missing_to_shopping(
    recipe_id: int, session: Session = Depends(get_session)
) -> Envelope[list[ShoppingItemRead]]:
    """Add this recipe's missing ingredients to the shopping list."""
    recipe = session.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    detail = recipes_service.detail(session, recipe)
    added = [
        shopping.add_manual(session, m.name, int(m.quantity) or 1, m.unit)
        for m in detail.missing
    ]
    return Envelope(
        data=[shopping.to_read(i) for i in added], meta={"added": len(added)}
    )
