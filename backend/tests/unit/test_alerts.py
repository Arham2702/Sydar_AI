"""Unit tests for alert derivation, dedup, and acknowledgement."""
from __future__ import annotations

from app.models.enums import AlertType
from app.services import alerts, inventory
from app.vision.base import Detection


def _det(name, category, count, age=None):
    return Detection(name=name, category=category, count=count, sim_age_days=age)


def _types_for(alert_list, name):
    return {a.alert_type for a in alert_list if _item_name(a) == name}


def _item_name(alert):  # helper resolved via message prefix
    return alert.message.split(" is ")[0].split(" has ")[0]


def test_low_stock_alert(session):
    # Eggs threshold is 4; detecting 2 should trip LOW_STOCK.
    inventory.reconcile(session, [_det("Eggs", "dairy", 2)], None or _src())
    result = alerts.regenerate_alerts(session)
    assert AlertType.LOW_STOCK in _types_for(result, "Eggs")


def _src():
    from app.models.enums import DetectionSource

    return DetectionSource.MOCK_VISION


def test_out_of_stock_alert(session):
    inventory.reconcile(session, [_det("Milk", "dairy", 1)], _src())
    from sqlmodel import select

    from app.models.entities import FridgeItem

    milk = session.exec(select(FridgeItem).where(FridgeItem.name == "Milk")).one()
    inventory.adjust_item(session, milk, 0)
    result = alerts.regenerate_alerts(session)
    assert AlertType.OUT_OF_STOCK in _types_for(result, "Milk")


def test_expired_alert(session):
    # Spinach shelf life 5 days; age 7 -> expired.
    inventory.reconcile(session, [_det("Spinach", "produce", 2, age=7)], _src())
    result = alerts.regenerate_alerts(session)
    assert AlertType.EXPIRED in _types_for(result, "Spinach")


def test_expiring_alert(session):
    # Milk shelf life 10 days; age 9 -> ~10% remaining -> expiring.
    inventory.reconcile(session, [_det("Milk", "dairy", 2, age=9)], _src())
    result = alerts.regenerate_alerts(session)
    assert AlertType.EXPIRING in _types_for(result, "Milk")


def test_regenerate_is_deduped_and_idempotent(session):
    inventory.reconcile(session, [_det("Eggs", "dairy", 2)], _src())
    first = alerts.regenerate_alerts(session)
    second = alerts.regenerate_alerts(session)
    assert len(first) == len(second)  # no duplicate rows accumulate


def test_resolved_condition_removes_alert(session):
    inventory.reconcile(session, [_det("Eggs", "dairy", 2)], _src())
    alerts.regenerate_alerts(session)
    # Restock above threshold; the low-stock alert should disappear.
    inventory.reconcile(session, [_det("Eggs", "dairy", 12)], _src())
    result = alerts.regenerate_alerts(session)
    assert AlertType.LOW_STOCK not in _types_for(result, "Eggs")


def test_acknowledge_persists_across_regenerate(session):
    inventory.reconcile(session, [_det("Eggs", "dairy", 2)], _src())
    result = alerts.regenerate_alerts(session)
    alert = next(a for a in result if a.alert_type == AlertType.LOW_STOCK)
    alerts.acknowledge(session, alert)

    result2 = alerts.regenerate_alerts(session)
    same = next(a for a in result2 if a.id == alert.id)
    assert same.acknowledged is True
