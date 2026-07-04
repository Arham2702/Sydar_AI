"""Shopping list endpoints — list, manual add, update (purchase/qty), remove."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..db import get_session
from ..models.entities import ShoppingListItem
from ..models.schemas import (
    Envelope,
    ShoppingItemCreate,
    ShoppingItemRead,
    ShoppingItemUpdate,
)
from ..services import shopping as shopping_service

router = APIRouter(prefix="/api/shopping", tags=["shopping"])


@router.get("", response_model=Envelope[list[ShoppingItemRead]])
def list_shopping(session: Session = Depends(get_session)) -> Envelope[list[ShoppingItemRead]]:
    items = shopping_service.list_items(session)
    return Envelope(
        data=[shopping_service.to_read(i) for i in items], meta={"count": len(items)}
    )


@router.post("", response_model=Envelope[ShoppingItemRead], status_code=201)
def add_shopping_item(
    body: ShoppingItemCreate, session: Session = Depends(get_session)
) -> Envelope[ShoppingItemRead]:
    item = shopping_service.add_manual(session, body.name, body.quantity, body.unit)
    return Envelope(data=shopping_service.to_read(item))


@router.patch("/{item_id}", response_model=Envelope[ShoppingItemRead])
def update_shopping_item(
    item_id: int, body: ShoppingItemUpdate, session: Session = Depends(get_session)
) -> Envelope[ShoppingItemRead]:
    item = session.get(ShoppingListItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Shopping item not found")
    item = shopping_service.update_item(session, item, body.status, body.quantity)
    return Envelope(data=shopping_service.to_read(item))


@router.delete("/{item_id}", status_code=204)
def delete_shopping_item(item_id: int, session: Session = Depends(get_session)) -> None:
    item = session.get(ShoppingListItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Shopping item not found")
    shopping_service.remove_item(session, item)
