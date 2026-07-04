"""Shopping list service.

Auto-populates from low/out-of-stock inventory (idempotent, deduped) and
supports manual additions, quantity edits, and mark-as-purchased. The
post-ingest recompute hook calls ``auto_populate`` so the list stays current.
"""
from __future__ import annotations

from sqlmodel import Session, select

from ..models.entities import CatalogItem, FridgeItem, ShoppingListItem
from ..models.enums import ItemStatus, ShoppingSource, ShoppingStatus
from ..models.schemas import ShoppingItemRead


def _needed_index(session: Session) -> dict[str, ShoppingListItem]:
    """Needed items keyed by lowercased name (dedup key across sources)."""
    stmt = select(ShoppingListItem).where(ShoppingListItem.status == ShoppingStatus.NEEDED)
    return {i.name.lower(): i for i in session.exec(stmt)}


def auto_populate(session: Session) -> list[ShoppingListItem]:
    """Add/refresh auto entries for every low or out-of-stock catalog item."""
    needed = _needed_index(session)
    stmt = select(FridgeItem).where(FridgeItem.status != ItemStatus.REMOVED)
    for item in session.exec(stmt):
        catalog = (
            session.get(CatalogItem, item.catalog_item_id) if item.catalog_item_id else None
        )
        threshold = catalog.low_stock_threshold if catalog else 1
        if item.quantity > threshold:
            continue

        source = ShoppingSource.AUTO_OUT if item.quantity <= 0 else ShoppingSource.AUTO_LOW_STOCK
        restock_qty = max(1, threshold - item.quantity + 1)
        existing = needed.get(item.name.lower())
        if existing is None:
            new_item = ShoppingListItem(
                catalog_item_id=item.catalog_item_id,
                name=item.name,
                quantity=restock_qty,
                unit=item.unit,
                source=source,
            )
            session.add(new_item)
            needed[item.name.lower()] = new_item
        elif existing.source != ShoppingSource.MANUAL:
            # Keep auto entries in sync (e.g. low_stock escalated to out).
            existing.source = source
            existing.quantity = restock_qty
            session.add(existing)

    session.commit()
    return list_items(session)


def clear_auto(session: Session) -> None:
    """Drop auto-generated needed entries (keep manual ones). Used on reset so a
    fresh capture re-derives the auto list from scratch."""
    stmt = select(ShoppingListItem).where(
        ShoppingListItem.status == ShoppingStatus.NEEDED,
        ShoppingListItem.source != ShoppingSource.MANUAL,
    )
    for item in session.exec(stmt).all():
        session.delete(item)
    session.commit()


def add_manual(
    session: Session, name: str, quantity: int = 1, unit: str = "count"
) -> ShoppingListItem:
    """Add a manual item, merging into an existing needed entry of the same name."""
    existing = _needed_index(session).get(name.lower())
    if existing is not None:
        existing.quantity += quantity
        existing.status = ShoppingStatus.NEEDED
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    catalog = session.exec(select(CatalogItem).where(CatalogItem.name == name)).first()
    item = ShoppingListItem(
        catalog_item_id=catalog.id if catalog else None,
        name=name,
        quantity=max(1, quantity),
        unit=unit,
        source=ShoppingSource.MANUAL,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def update_item(
    session: Session,
    item: ShoppingListItem,
    status: ShoppingStatus | None = None,
    quantity: int | None = None,
) -> ShoppingListItem:
    if status is not None:
        item.status = status
    if quantity is not None:
        item.quantity = max(1, quantity)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def remove_item(session: Session, item: ShoppingListItem) -> None:
    session.delete(item)
    session.commit()


def list_items(session: Session) -> list[ShoppingListItem]:
    return list(
        session.exec(
            select(ShoppingListItem).order_by(
                ShoppingListItem.status, ShoppingListItem.source, ShoppingListItem.name
            )
        )
    )


def to_read(item: ShoppingListItem) -> ShoppingItemRead:
    return ShoppingItemRead(
        id=item.id,
        name=item.name,
        quantity=item.quantity,
        unit=item.unit,
        source=item.source,
        status=item.status,
        created_at=item.created_at,
    )
