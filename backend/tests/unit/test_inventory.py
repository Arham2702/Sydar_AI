"""Unit tests for inventory reconciliation, event log, and manual adjust."""
from __future__ import annotations

from sqlmodel import select

from app.models.entities import Alert, FridgeItem, InventoryEvent
from app.models.enums import DetectionSource, EventType, ItemStatus
from app.services import alerts, inventory
from app.vision.base import Detection, merge_detections


def _det(name, category, count, age=None, freshness=None):
    return Detection(
        name=name, category=category, count=count, sim_age_days=age, freshness_score=freshness
    )


def test_reconcile_creates_items_and_events(session):
    dets = [_det("Milk", "dairy", 1), _det("Eggs", "dairy", 6)]
    result = inventory.reconcile(session, dets, DetectionSource.MOCK_VISION)

    assert result.items_created == 2
    assert result.items_updated == 0
    items = {i.name: i for i in session.exec(select(FridgeItem))}
    assert items["Milk"].quantity == 1
    assert items["Eggs"].quantity == 6
    # An event was logged per created item.
    events = session.exec(select(InventoryEvent)).all()
    assert len(events) == 2
    assert all(e.event_type == EventType.DETECTED for e in events)


def test_reconcile_updates_existing_item_quantity(session):
    inventory.reconcile(session, [_det("Milk", "dairy", 1)], DetectionSource.MOCK_VISION)
    result = inventory.reconcile(session, [_det("Milk", "dairy", 3)], DetectionSource.MOCK_VISION)

    assert result.items_created == 0
    assert result.items_updated == 1
    milk = session.exec(select(FridgeItem).where(FridgeItem.name == "Milk")).one()
    assert milk.quantity == 3
    # Delta recorded: 3 - 1 = 2.
    last_event = session.exec(select(InventoryEvent).order_by(InventoryEvent.id.desc())).first()
    assert last_event.quantity_delta == 2


def test_sim_age_backdates_first_seen(session):
    inventory.reconcile(
        session, [_det("Spinach", "produce", 1, age=4)], DetectionSource.MOCK_VISION
    )
    spinach = session.exec(select(FridgeItem).where(FridgeItem.name == "Spinach")).one()
    age_days = (spinach.last_seen_at - spinach.first_seen_at).total_seconds() / 86400
    assert 3.9 < age_days < 4.1


def test_deplete_missing_marks_absent_items(session):
    inventory.reconcile(
        session,
        [_det("Milk", "dairy", 1), _det("Eggs", "dairy", 6)],
        DetectionSource.MOCK_VISION,
    )
    # Second capture omits Eggs, with depletion enabled.
    result = inventory.reconcile(
        session, [_det("Milk", "dairy", 1)], DetectionSource.MOCK_VISION, deplete_missing=True
    )
    assert result.items_depleted == 1
    eggs = session.exec(select(FridgeItem).where(FridgeItem.name == "Eggs")).one()
    assert eggs.status == ItemStatus.DEPLETED
    assert eggs.quantity == 0


def test_missing_items_kept_by_default(session):
    inventory.reconcile(
        session,
        [_det("Milk", "dairy", 1), _det("Eggs", "dairy", 6)],
        DetectionSource.MOCK_VISION,
    )
    inventory.reconcile(session, [_det("Milk", "dairy", 1)], DetectionSource.MOCK_VISION)
    eggs = session.exec(select(FridgeItem).where(FridgeItem.name == "Eggs")).one()
    assert eggs.status == ItemStatus.ACTIVE  # not wiped by a partial capture


def test_redetecting_depleted_item_restocks(session):
    inventory.reconcile(session, [_det("Milk", "dairy", 1)], DetectionSource.MOCK_VISION)
    milk = session.exec(select(FridgeItem).where(FridgeItem.name == "Milk")).one()
    inventory.adjust_item(session, milk, 0)
    assert milk.status == ItemStatus.DEPLETED

    inventory.reconcile(session, [_det("Milk", "dairy", 2)], DetectionSource.MOCK_VISION)
    session.refresh(milk)
    assert milk.status == ItemStatus.ACTIVE
    assert milk.quantity == 2


def test_adjust_item_logs_manual_event(session):
    inventory.reconcile(session, [_det("Milk", "dairy", 3)], DetectionSource.MOCK_VISION)
    milk = session.exec(select(FridgeItem).where(FridgeItem.name == "Milk")).one()
    inventory.adjust_item(session, milk, 1)

    assert milk.quantity == 1
    event = session.exec(select(InventoryEvent).order_by(InventoryEvent.id.desc())).first()
    assert event.event_type == EventType.MANUAL_ADJUST
    assert event.source == DetectionSource.MANUAL


def test_merge_detections_collapses_same_item():
    # Mirrors the real failure: one aggregate row + pristine per-item rows.
    dets = [
        Detection(name="Tomatoes", category="produce", count=4, freshness_score=30),
        Detection(name="Tomatoes", category="produce", count=1, freshness_score=80),
        Detection(name="tomatoes", category="produce", count=1, freshness_score=90),
        Detection(name="Milk", category="dairy", count=1, freshness_score=95),
    ]
    merged = merge_detections(dets)
    assert len(merged) == 2  # tomatoes collapsed (case-insensitive)
    tomato = next(m for m in merged if m.name.lower() == "tomatoes")
    assert tomato.count == 4  # largest count wins
    assert tomato.freshness_score == 30  # worst freshness wins


def test_reconcile_merges_duplicate_detections(session):
    result = inventory.reconcile(
        session,
        [
            _det("Tomatoes", "produce", 4, freshness=30),
            _det("Tomatoes", "produce", 1, freshness=90),
        ],
        DetectionSource.GEMINI_VISION,
    )
    assert result.items_created == 1
    assert len(result.merged_detections) == 1
    item = session.exec(select(FridgeItem).where(FridgeItem.name == "Tomatoes")).one()
    assert item.quantity == 4
    assert item.visual_freshness == 30


def test_reset_clears_items_events_and_alerts(session):
    inventory.reconcile(session, [_det("Eggs", "dairy", 2)], DetectionSource.MOCK_VISION)
    alerts.regenerate_alerts(session)  # creates a low-stock alert
    assert session.exec(select(FridgeItem)).all()
    assert session.exec(select(Alert)).all()

    inventory.reset(session)

    assert session.exec(select(FridgeItem)).all() == []
    assert session.exec(select(InventoryEvent)).all() == []
    assert session.exec(select(Alert)).all() == []


def test_reconcile_stores_visual_freshness(session):
    inventory.reconcile(
        session, [_det("Tomatoes", "produce", 3, freshness=30)], DetectionSource.GEMINI_VISION
    )
    item = session.exec(select(FridgeItem).where(FridgeItem.name == "Tomatoes")).one()
    assert item.visual_freshness == 30
    # Freshness view reflects the visual estimate, not time-based.
    assert inventory.to_read(session, item).freshness.score == 30


def test_to_read_includes_freshness(session):
    inventory.reconcile(
        session, [_det("Milk", "dairy", 1, age=1)], DetectionSource.MOCK_VISION
    )
    milk = session.exec(select(FridgeItem).where(FridgeItem.name == "Milk")).one()
    view = inventory.to_read(session, milk)
    assert view.freshness.level is not None
    assert 0 <= view.freshness.score <= 100
