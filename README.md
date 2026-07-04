# FreshKeep — Smart Fridge Platform (Phase 1)

Software platform for a Hardware-as-a-Service product: a device that lives in a
fridge, captures images of its contents, and drives a platform for **food
inventory, freshness, alerts, recipes, and shopping lists**.

This is **Phase 1: software only**. There is no physical device yet — image
input arrives as files or labeled **simulated** sample scenes, clearly marked as
mock data throughout. There is no auth; a single implicit session is assumed.

## What it does

| Capability | Where |
|---|---|
| Fridge image → structured inventory + counts | `POST /api/ingest` → vision pipeline → reconciliation |
| Per-item freshness levels | computed on read (`services/freshness.py`) |
| Alerts for losing-freshness / expired / low / out | `GET /api/alerts` |
| Recipe suggestions from current inventory | `GET /api/recipes/suggestions` |
| Recipe detail — owned vs missing ingredients | `GET /api/recipes/{id}` |
| Auto-populating shopping list + manual adds | `GET/POST/PATCH/DELETE /api/shopping` |

## Architecture

```
Fridge image / sample ─▶ FastAPI /api/ingest ─▶ VisionProvider (mock | Claude)
                                                        │ detections
                                                        ▼
                          reconcile → FridgeItems + InventoryEvents (SQLite)
                                                        │
              freshness · alerts · recipe matching · shopping (pure Python)
                                                        │
                                     FastAPI JSON API  ─▶  Next.js frontend
```

- **Backend** (`backend/`) — Python-first: FastAPI + SQLModel. All domain logic
  lives in pure `services/` modules, independently unit-tested.
- **Frontend** (`frontend/`) — Next.js (App Router, TypeScript, Tailwind);
  polished, responsive, customer-facing.
- **Vision** — pluggable `VisionProvider`. Default `MockVisionProvider` is
  deterministic and offline (great for demos + tests); set `GOOGLE_API_KEY`
  (Gemini, `gemini-2.5-flash-lite`) or `ANTHROPIC_API_KEY` (Claude) to switch to
  a real multimodal model. Same downstream contract either way. Custom CV is out
  of scope for Phase 1. See `backend/README.md` → "Real vision" to test with a
  real image.
- **Skills** (`skills/`) — Claude Code skills capturing the repeated structured
  work: `vision-pipeline` (adding providers/samples) and `api-schema` (endpoint
  + response-envelope conventions).

## Run it

Two local dev servers.

**1. Backend** (`:8000`):

```bash
cd backend
python3 -m venv .venv && ./.venv/bin/pip install -e ".[dev]"
./.venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

**2. Frontend** (`:3000`):

```bash
cd frontend
npm install
npm run dev
# open http://localhost:3000
```

Click a **simulated scene** (Well-stocked / Running low / Items expiring) on the
Inventory page to run the pipeline, then explore Alerts, Recipes, and Shopping.

## Testing

Testing is a definition-of-done requirement.

```bash
cd backend && ./.venv/bin/python -m pytest --cov=app --cov-report=term-missing
```

- **Unit tests** — every service (freshness, inventory, alerts, recipes,
  shopping) and the mock vision provider, with frozen `now` for determinism.
- **Integration tests** — the full vertical slice through the HTTP API.
- **Coverage** — ≥90% on `services/` and the mock provider.

See `backend/README.md` for backend details and the real-vision path.

## Scope & honesty notes

- **No fabricated hardware.** Sample scenes in `backend/samples/` are labeled
  SIMULATED; API responses and the UI carry `simulated: true` / a "Simulated
  feed" badge. `sim_age_days` in fixtures is a documented demo aid so freshness
  decay is visible without waiting real days.
- **Constrained vertical slice** — a curated ~20-item catalog and ~12 recipes,
  handled deeply end-to-end, rather than a broad stubbed catalog.
