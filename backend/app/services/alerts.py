"""Alerts service — derive freshness/stock alerts from current inventory.

Alerts are regenerated from state (not authored). Each recompute reconciles the
desired set against what's stored: stale alerts are removed, surviving ones keep
their acknowledged flag, and new conditions are inserted. Dedup key is
``(fridge_item_id, alert_type)``.
"""
from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, select

from ..models.entities import Alert, CatalogItem, FridgeItem, utcnow
from ..models.enums import AlertSeverity, AlertType, FreshnessLevel, ItemStatus
from ..models.schemas import AlertRead
from .freshness import score_item

_Desired = tuple[FridgeItem, AlertType, AlertSeverity, str]


def _desired_alerts(session: Session, now: datetime) -> list[_Desired]:
    out: list[_Desired] = []
    for item in session.exec(select(FridgeItem).where(FridgeItem.status != ItemStatus.REMOVED)):
        catalog = (
            session.get(CatalogItem, item.catalog_item_id) if item.catalog_item_id else None
        )
        threshold = catalog.low_stock_threshold if catalog else 1

        # Stock alerts.
        if item.quantity <= 0:
            out.append((item, AlertType.OUT_OF_STOCK, AlertSeverity.CRITICAL,
                        f"{item.name} is out of stock"))
        elif item.quantity <= threshold:
            out.append((item, AlertType.LOW_STOCK, AlertSeverity.WARNING,
                        f"{item.name} is running low ({item.quantity} {item.unit} left)"))

        # Freshness alerts only make sense while some stock exists.
        if item.quantity > 0:
            fresh = score_item(item, catalog, now)
            if fresh.level == FreshnessLevel.EXPIRED:
                out.append((item, AlertType.EXPIRED, AlertSeverity.CRITICAL,
                            f"{item.name} has expired"))
            elif fresh.level == FreshnessLevel.EXPIRING:
                out.append((item, AlertType.EXPIRING, AlertSeverity.WARNING,
                            f"{item.name} is expiring soon (~{fresh.days_remaining}d left)"))
    return out


def regenerate_alerts(session: Session, now: datetime | None = None) -> list[Alert]:
    now = now or utcnow()
    desired = _desired_alerts(session, now)
    desired_keys = {(item.id, atype) for item, atype, _, _ in desired}
    existing = {
        (a.fridge_item_id, a.alert_type): a for a in session.exec(select(Alert)).all()
    }

    for key, alert in existing.items():
        if key not in desired_keys:
            session.delete(alert)

    for item, atype, severity, message in desired:
        key = (item.id, atype)
        if key in existing:
            alert = existing[key]
            alert.severity = severity
            alert.message = message
            session.add(alert)
        else:
            session.add(
                Alert(
                    fridge_item_id=item.id,
                    alert_type=atype,
                    severity=severity,
                    message=message,
                )
            )

    session.commit()
    return list_alerts(session)


def list_alerts(session: Session) -> list[Alert]:
    return list(session.exec(select(Alert).order_by(Alert.severity, Alert.id)))


def acknowledge(session: Session, alert: Alert) -> Alert:
    alert.acknowledged = True
    session.add(alert)
    session.commit()
    session.refresh(alert)
    return alert


def to_read(session: Session, alert: Alert) -> AlertRead:
    item = session.get(FridgeItem, alert.fridge_item_id)
    return AlertRead(
        id=alert.id,
        fridge_item_id=alert.fridge_item_id,
        item_name=item.name if item else "unknown",
        alert_type=alert.alert_type,
        severity=alert.severity,
        message=alert.message,
        acknowledged=alert.acknowledged,
        created_at=alert.created_at,
    )
