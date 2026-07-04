---
name: vision-pipeline
description: Conventions for the fridge image→inventory vision pipeline — how to add a VisionProvider, add a labeled sample scene, and keep the mock deterministic. Use when touching backend/app/vision/ or backend/samples/.
---

# Vision pipeline conventions

The fridge platform turns an image into structured `Detection`s through a
pluggable `VisionProvider`. Everything downstream (reconciliation, freshness,
alerts) depends only on the `Detection` contract, so providers are swappable.

## The Detection contract

`backend/app/vision/base.py` defines it. A detection is:

```python
Detection(name="Milk", category="dairy", count=1, confidence=0.98,
          bbox=None, sim_age_days=3)
```

- `name` **must** match a `CatalogItem.name` in `backend/app/seed/catalog.json`
  (case-sensitive). Unmatched names create catalog-less fridge items with no
  freshness profile — avoid.
- `count` is an integer item count (no weights/volumes in Phase 1).
- `confidence` is 0.0–1.0.
- `sim_age_days` is **simulation-only**: how long the item has already been in
  the fridge, so freshness decay is demonstrable without waiting real days.
  Real providers leave it `None`; only mock fixtures set it.

## Adding a provider

1. Subclass `VisionProvider` (`base.py`); set `source` (a `DetectionSource`)
   and `simulated` (bool).
2. Implement `analyze(image_bytes, *, sample_name=None) -> VisionResult`.
3. Register selection in `vision/__init__.py::get_vision_provider`.
4. Never make the mock/default path import the `anthropic` SDK or hit the
   network — keep heavy imports lazy inside the real provider.

## Adding a labeled sample scene

Each scene is a `backend/samples/<scene>.expected.json`:

```json
{
  "_note": "SIMULATED fridge scene — not a real capture.",
  "scene": "<scene>",
  "detections": [
    {"name": "Milk", "category": "dairy", "count": 1, "confidence": 0.98, "sim_age_days": 3}
  ]
}
```

- Always mark scenes as SIMULATED in `_note` — we don't fabricate hardware.
- `name`/`category` must match the catalog. Pick `sim_age_days` relative to the
  catalog `default_shelf_life_days` to hit the freshness level you want to demo
  (e.g. age ≥ shelf life → expired).
- Add a row to `backend/samples/README.md` describing the scene's purpose.
- Add/extend a unit test in `backend/tests/unit/test_mock_provider.py`.

## Determinism rule

The mock must be reproducible: given a `sample_name` it returns that fixture
verbatim; given raw bytes with no name it hashes the bytes to pick a scene.
Do not add un-seeded randomness — tests assert exact detection counts.
