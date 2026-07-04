"""Alert endpoints — list derived alerts and acknowledge them."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from ..db import get_session
from ..models.entities import Alert
from ..models.schemas import AlertRead, Envelope
from ..services import alerts as alerts_service

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=Envelope[list[AlertRead]])
def list_alerts(
    unacknowledged_only: bool = Query(False),
    session: Session = Depends(get_session),
) -> Envelope[list[AlertRead]]:
    items = alerts_service.list_alerts(session)
    if unacknowledged_only:
        items = [a for a in items if not a.acknowledged]
    data = [alerts_service.to_read(session, a) for a in items]
    unack = sum(1 for a in items if not a.acknowledged)
    return Envelope(data=data, meta={"count": len(data), "unacknowledged": unack})


@router.post("/{alert_id}/ack", response_model=Envelope[AlertRead])
def acknowledge_alert(
    alert_id: int, session: Session = Depends(get_session)
) -> Envelope[AlertRead]:
    alert = session.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert = alerts_service.acknowledge(session, alert)
    return Envelope(data=alerts_service.to_read(session, alert))
