"""Ingest endpoint — the entry point for a fridge capture (file or sample).

Each capture replaces the current inventory (a fridge camera reports the full
current contents), runs the configured vision provider, then fires the
post-ingest recompute hook — alerts, shopping list, and (when a Gemini key is
present) a fresh recipe search against the new inventory.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlmodel import Session, select

from ..db import get_session
from ..models.entities import CatalogItem
from ..models.schemas import DetectedItem, Envelope, IngestResult
from ..services import alerts, inventory, recipe_search, shopping
from ..vision import get_vision_provider
from ..vision.base import VisionError

router = APIRouter(prefix="/api", tags=["ingest"])


@router.post("/ingest", response_model=Envelope[IngestResult])
async def ingest(
    sample: str | None = Query(
        None, description="Name of a labeled SIMULATED sample scene to ingest."
    ),
    reset: bool = Query(True, description="Replace current inventory with this capture."),
    file: UploadFile | None = File(None),
    session: Session = Depends(get_session),
) -> Envelope[IngestResult]:
    if file is not None:
        image_bytes = await file.read()
    else:
        image_bytes = b""
        sample = sample or "fridge_full"  # default demo scene when nothing supplied

    catalog_names = [c.name for c in session.exec(select(CatalogItem))]
    provider = get_vision_provider(catalog_names)
    try:
        result = provider.analyze(image_bytes, sample_name=sample)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except VisionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    if reset:
        inventory.reset(session)
        shopping.clear_auto(session)

    rec = inventory.reconcile(session, result.detections, result.source)

    # Post-ingest recompute hook — keep derived state in sync with the capture.
    alerts.regenerate_alerts(session)
    shopping.auto_populate(session)
    if recipe_search.search_enabled():
        names = [i.name for i in inventory.list_items(session) if i.quantity > 0]
        recipe_search.refresh_from_inventory(session, names)

    return Envelope(
        data=IngestResult(
            source=result.source,
            simulated=result.simulated,
            detections=rec.detections,
            items_created=rec.items_created,
            items_updated=rec.items_updated,
            items_depleted=rec.items_depleted,
            detected_items=[
                DetectedItem(
                    name=d.name,
                    category=d.category,
                    count=d.count,
                    confidence=round(d.confidence, 2),
                    freshness=int(d.freshness_score) if d.freshness_score is not None else None,
                )
                for d in rec.merged_detections
            ],
        ),
        meta={"sample": sample, "simulated": result.simulated},
    )
