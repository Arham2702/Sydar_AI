"""Inventory endpoints — list items with freshness, and manual adjustments."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..db import get_session
from ..models.entities import FridgeItem
from ..models.schemas import Envelope, InventoryAdjust, InventoryItemRead
from ..services import alerts, inventory, shopping

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.get("", response_model=Envelope[list[InventoryItemRead]])
def list_inventory(session: Session = Depends(get_session)) -> Envelope[list[InventoryItemRead]]:
    items = [inventory.to_read(session, i) for i in inventory.list_items(session)]
    return Envelope(data=items, meta={"count": len(items)})


@router.get("/{item_id}", response_model=Envelope[InventoryItemRead])
def get_inventory_item(
    item_id: int, session: Session = Depends(get_session)
) -> Envelope[InventoryItemRead]:
    item = session.get(FridgeItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return Envelope(data=inventory.to_read(session, item))


@router.patch("/{item_id}", response_model=Envelope[InventoryItemRead])
def adjust_inventory_item(
    item_id: int, body: InventoryAdjust, session: Session = Depends(get_session)
) -> Envelope[InventoryItemRead]:
    item = session.get(FridgeItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    item = inventory.adjust_item(session, item, body.quantity)
    # A manual quantity change can trigger new alerts / shopping needs.
    alerts.regenerate_alerts(session)
    shopping.auto_populate(session)
    return Envelope(data=inventory.to_read(session, item))
