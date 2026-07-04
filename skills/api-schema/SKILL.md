---
name: api-schema
description: Conventions for the fridge platform's FastAPI endpoints — response envelope, schema/service separation, error shape, and the integration-test checklist. Use when adding or changing anything under backend/app/routers/ or backend/app/models/schemas.py.
---

# API schema & endpoint conventions

## Response envelope

Every successful response is wrapped in `Envelope` (`app/models/schemas.py`):

```json
{ "data": <payload>, "meta": { "count": 12 } }
```

- `data` holds the resource(s). Lists go in `data` as a JSON array, never at the
  top level.
- `meta` holds counts, flags, and context (`count`, `unacknowledged`,
  `simulated`, `sample`). Default `{}`.
- Declare it typed: `response_model=Envelope[SomeRead]` or
  `Envelope[list[SomeRead]]`.

## Schema vs table separation

- SQLModel **tables** live in `app/models/entities.py` — never returned directly
  from an endpoint.
- API **request/response** models live in `app/models/schemas.py` (plain
  Pydantic). Routers map entities → `*Read` schemas via a service `to_read(...)`
  helper, so the HTTP contract is decoupled from storage.

## Router rules

- Prefix per resource: `APIRouter(prefix="/api/<resource>", tags=["<resource>"])`.
- Routers are **thin**: parse input, call a `services/*` function, wrap in
  `Envelope`. No business logic in routers.
- Get the DB session via `Depends(get_session)`.
- Errors: raise `HTTPException(status_code=404, detail="...")` for missing
  resources; `422` is automatic from Pydantic validation.
- Mutations that change stock/freshness must call the post-change recompute hook
  (`alerts.regenerate_alerts` + `shopping.auto_populate`) — see
  `routers/ingest.py` and `routers/inventory.py`.
- Anything derived from simulated vision must carry `simulated`/`source` through
  to the response so the UI can label it honestly.

## Integration-test checklist (add to `backend/tests/integration/`)

For every new endpoint:
1. Happy path returns 200/201 and the `data`/`meta` envelope shape.
2. 404 path for a bad id.
3. 422 path for an invalid body (if it takes one).
4. Any recompute side effect is asserted (e.g. ingesting updates `/api/alerts`).

Use the `client` + in-memory-SQLite fixtures in `tests/conftest.py`.
