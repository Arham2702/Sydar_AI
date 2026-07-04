"""Unit tests for shopping list auto-population and manual management."""
from __future__ import annotations

from app.models.enums import DetectionSource, ShoppingSource, ShoppingStatus
from app.services import inventory, shopping
from app.vision.base import Detection

SRC = DetectionSource.MOCK_VISION


def _det(name, category, count):
    return Detection(name=name, category=category, count=count)


def _by_name(items, name):
    return next(i for i in items if i.name == name)


def test_auto_populate_adds_low_stock(session):
    inventory.reconcile(session, [_det("Eggs", "dairy", 2)], SRC)  # threshold 4
    items = shopping.auto_populate(session)
    eggs = _by_name(items, "Eggs")
    assert eggs.source == ShoppingSource.AUTO_LOW_STOCK
    assert eggs.quantity >= 1


def test_auto_populate_marks_out_of_stock(session):
    inventory.reconcile(session, [_det("Milk", "dairy", 1)], SRC)
    from sqlmodel import select

    from app.models.entities import FridgeItem

    milk = session.exec(select(FridgeItem).where(FridgeItem.name == "Milk")).one()
    inventory.adjust_item(session, milk, 0)
    items = shopping.auto_populate(session)
    assert _by_name(items, "Milk").source == ShoppingSource.AUTO_OUT


def test_auto_populate_is_idempotent(session):
    inventory.reconcile(session, [_det("Eggs", "dairy", 2)], SRC)
    shopping.auto_populate(session)
    items = shopping.auto_populate(session)
    assert len([i for i in items if i.name == "Eggs"]) == 1


def test_well_stocked_item_not_added(session):
    inventory.reconcile(session, [_det("Eggs", "dairy", 12)], SRC)
    items = shopping.auto_populate(session)
    assert all(i.name != "Eggs" for i in items)


def test_manual_add(session):
    item = shopping.add_manual(session, "Coffee", 2, "bag")
    assert item.source == ShoppingSource.MANUAL
    assert item.quantity == 2


def test_manual_add_merges_duplicates(session):
    shopping.add_manual(session, "Coffee", 1)
    merged = shopping.add_manual(session, "Coffee", 2)
    assert merged.quantity == 3
    assert len([i for i in shopping.list_items(session) if i.name == "Coffee"]) == 1


def test_mark_purchased(session):
    item = shopping.add_manual(session, "Coffee", 1)
    updated = shopping.update_item(session, item, status=ShoppingStatus.PURCHASED)
    assert updated.status == ShoppingStatus.PURCHASED


def test_remove_item(session):
    item = shopping.add_manual(session, "Coffee", 1)
    shopping.remove_item(session, item)
    assert all(i.name != "Coffee" for i in shopping.list_items(session))


def test_manual_item_not_overwritten_by_auto(session):
    # Manually add Eggs, then run auto-populate for a low Eggs stock.
    shopping.add_manual(session, "Eggs", 5)
    inventory.reconcile(session, [_det("Eggs", "dairy", 2)], SRC)
    items = shopping.auto_populate(session)
    eggs = _by_name(items, "Eggs")
    assert eggs.source == ShoppingSource.MANUAL
    assert eggs.quantity == 5  # untouched
