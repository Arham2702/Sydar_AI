# Sample fridge scenes (SIMULATED)

The physical device / camera feed does not exist in Phase 1. These files are
**simulated captures**, not real photos. Each `<scene>.expected.json` describes
the detections a vision model *would* return for that fridge scene, and is
consumed by `app/vision/mock_provider.py`.

| Scene              | Purpose                                                        |
|--------------------|----------------------------------------------------------------|
| `fridge_full`      | Well-stocked fridge; exercises inventory + varied freshness.   |
| `fridge_low`       | Sparse fridge; triggers low-stock / out-of-stock shopping adds.|
| `fridge_expiring`  | Items past/near expiry; triggers expiring & expired alerts.    |

## Fixture format

```json
{
  "scene": "fridge_full",
  "detections": [
    {"name": "Milk", "category": "dairy", "count": 1, "confidence": 0.98, "sim_age_days": 3}
  ]
}
```

- `name` must match a `CatalogItem.name` in `app/seed/catalog.json`.
- `count` is an integer item count.
- `sim_age_days` is a **simulation-only** hint (days already in the fridge) so
  freshness decay is demonstrable without waiting real days. Real providers omit it.

See the `vision-pipeline` skill for the full convention when adding a scene.
