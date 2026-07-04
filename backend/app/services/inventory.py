"""Inventory service — reconcile detections into tracked fridge items.

Provider-agnostic: it consumes ``Detection`` objects (from any VisionProvider)
plus manual adjustments, upserts ``FridgeItem`` rows, and writes an append-only
``InventoryEvent`` log. Freshness is layered on at read time via
``services.freshness``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from sqlmodel import Session, select

from ..models.entities import Alert, CatalogItem, FridgeItem, InventoryEvent, utcnow
from ..models.enums import DetectionSource, EventType, ItemStatus
from ..models.schemas import InventoryItemRead
from ..vision.base import Detection, merge_detections
from .freshness import score_item


@dataclass
class ReconcileResult:
    source: DetectionSource
    detections: int
    items_created: int
    items_updated: int
    items_depleted: int
    merged_detections: list[Detection] = field(default_factory=list)


def _catalog_by_name(session: Session) -> dict[str, CatalogItem]:
    return {c.name: c for c in session.exec(select(CatalogItem)).all()}


def _find_item(session: Session, name: str) -> FridgeItem | None:
    return session.exec(select(FridgeItem).where(FridgeItem.name == name)).first()


def _log_event(
    session: Session,
    item: FridgeItem,
    event_type: EventType,
    delta: int,
    source: DetectionSource,
    detection: Detection | None = None,
) -> None:
    session.add(
        InventoryEvent(
            fridge_item_id=item.id,
            event_type=event_type,
            quantity_delta=delta,
            source=source,
            raw_detection=detection.model_dump() if detection else None,
        )
    )


def reconcile(
    session: Session,
    detections: list[Detection],
    source: DetectionSource,
    now: datetime | None = None,
    deplete_missing: bool = False,
) -> ReconcileResult:
    """Upsert a capture's detections into inventory.

    A capture's ``count`` is treated as authoritative for each detected item.
    Re-detecting a previously depleted item restocks it and resets its freshness
    clock. When ``deplete_missing`` is True, active items absent from this
    capture are marked depleted (off by default so partial captures don't wipe
    inventory — see the depletion-policy assumption in the plan).
    """
    now = now or utcnow()
    detections = merge_detections(detections)  # collapse duplicate same-item rows
    catalog = _catalog_by_name(session)
    seen: set[str] = set()
    created = updated = depleted = 0

    for det in detections:
        seen.add(det.name)
        cat = catalog.get(det.name)
        first_seen = now - timedelta(days=det.sim_age_days) if det.sim_age_days else now
        item = _find_item(session, det.name)

        visual = int(det.freshness_score) if det.freshness_score is not None else None

        if item is None:
            item = FridgeItem(
                name=det.name,
                category=det.category,
                quantity=det.count,
                unit=cat.unit if cat else "count",
                catalog_item_id=cat.id if cat else None,
                first_seen_at=first_seen,
                last_seen_at=now,
                added_at=now,
                status=ItemStatus.ACTIVE,
                visual_freshness=visual,
            )
            session.add(item)
            session.flush()  # assign id for the event FK
            _log_event(session, item, EventType.DETECTED, det.count, source, det)
            created += 1
        else:
            old_qty = item.quantity
            if item.status != ItemStatus.ACTIVE:
                item.first_seen_at = first_seen  # restock resets freshness clock
                item.status = ItemStatus.ACTIVE
            item.quantity = det.count
            item.last_seen_at = now
            if visual is not None:
                item.visual_freshness = visual  # refresh from the new capture
            session.add(item)
            _log_event(session, item, EventType.DETECTED, det.count - old_qty, source, det)
            updated += 1

    if deplete_missing:
        actives = session.exec(
            select(FridgeItem).where(FridgeItem.status == ItemStatus.ACTIVE)
        ).all()
        for item in actives:
            if item.name not in seen:
                _log_event(session, item, EventType.REMOVED, -item.quantity, source)
                item.quantity = 0
                item.status = ItemStatus.DEPLETED
                session.add(item)
                depleted += 1

    session.commit()
    return ReconcileResult(
        source=source,
        detections=len(detections),
        items_created=created,
        items_updated=updated,
        items_depleted=depleted,
        merged_detections=detections,
    )


def reset(session: Session) -> None:
    """Clear all tracked inventory (items, event log, alerts).

    Used when a fresh capture should replace prior state — the fridge camera
    reports the current full contents, so each upload starts clean. Alerts are
    deleted first (they reference items); the shopping list's manual entries are
    left intact (see ``shopping.clear_auto``).
    """
    for alert in session.exec(select(Alert)).all():
        session.delete(alert)
    for event in session.exec(select(InventoryEvent)).all():
        session.delete(event)
    for item in session.exec(select(FridgeItem)).all():
        session.delete(item)
    session.commit()


def adjust_item(session: Session, item: FridgeItem, quantity: int) -> FridgeItem:
    """Manually set an item's quantity (e.g. user correction)."""
    old = item.quantity
    item.quantity = max(0, quantity)
    item.status = ItemStatus.DEPLETED if item.quantity == 0 else ItemStatus.ACTIVE
    item.last_seen_at = utcnow()
    session.add(item)
    _log_event(
        session, item, EventType.MANUAL_ADJUST, item.quantity - old, DetectionSource.MANUAL
    )
    session.commit()
    session.refresh(item)
    return item


def list_items(session: Session, include_removed: bool = False) -> list[FridgeItem]:
    stmt = select(FridgeItem)
    if not include_removed:
        stmt = stmt.where(FridgeItem.status != ItemStatus.REMOVED)
    return list(session.exec(stmt))


def to_read(session: Session, item: FridgeItem, now: datetime | None = None) -> InventoryItemRead:
    """Build the API view of an item, including computed freshness."""
    catalog = session.get(CatalogItem, item.catalog_item_id) if item.catalog_item_id else None
    freshness = score_item(item, catalog, now)
    return InventoryItemRead(
        id=item.id,
        name=item.name,
        category=item.category,
        quantity=item.quantity,
        unit=item.unit,
        status=item.status,
        first_seen_at=item.first_seen_at,
        last_seen_at=item.last_seen_at,
        freshness=freshness,
    )
