# Fridge Platform — Backend (FastAPI)

Python-first platform logic for the smart-fridge Hardware-as-a-Service product:
image → inventory pipeline, freshness scoring, alerts, recipe matching, and
shopping-list logic, exposed over a JSON API.

## Stack

- **FastAPI** — REST API (`/api/*`), auto docs at `/docs`.
- **SQLModel + SQLite** — persistence (`fridge.db`); tests use in-memory SQLite.
- **Pluggable vision** — `MockVisionProvider` (default, offline) or
  `ClaudeVisionProvider` (real, when `ANTHROPIC_API_KEY` is set).

## Setup

```bash
cd backend
python3 -m venv .venv
./.venv/bin/pip install -e ".[dev]"
```

## Run

```bash
./.venv/bin/python -m uvicorn app.main:app --reload --port 8000
# open http://localhost:8000/docs
```

The database is created and seeded (curated catalog + recipes) on startup.

### Try it

```bash
curl -X POST "http://localhost:8000/api/ingest?sample=fridge_full"   # simulated capture
curl http://localhost:8000/api/inventory
curl http://localhost:8000/api/alerts
curl http://localhost:8000/api/recipes/suggestions
curl http://localhost:8000/api/shopping
```

Sample scenes: `fridge_full`, `fridge_low`, `fridge_expiring` (all **simulated**
— see `samples/README.md`).

## Real vision (optional)

The vision engine is pluggable. Set a key and the provider switches from the
offline mock to a real model — everything downstream is identical.

**Gemini** (`gemini-2.5-flash-lite` by default):

```bash
export GOOGLE_API_KEY=...              # or GEMINI_API_KEY
export FRIDGE_VISION_PROVIDER=gemini   # optional; auto-detected from the key
./.venv/bin/python -m uvicorn app.main:app --reload --port 8000
# confirm it's active:
curl http://localhost:8000/api/health   # -> {"vision_provider":"gemini"}
# upload a real fridge photo and see the detections:
curl -F "file=@fridge.jpg" http://localhost:8000/api/ingest
```

Override the model with `FRIDGE_GEMINI_MODEL=...`. The `/api/ingest` response
includes `detected_items` (name, count, confidence) so you can see exactly what
the model returned; the frontend renders these under the upload button.

**Claude** (`claude-opus-4-8`): set `ANTHROPIC_API_KEY` instead (takes
precedence in auto mode).

## Tests

```bash
./.venv/bin/python -m pytest --cov=app --cov-report=term-missing
```

Unit tests cover every service (`freshness`, `inventory`, `alerts`, `recipes`,
`shopping`) and the mock vision provider; integration tests drive the full
`ingest → inventory → freshness → alerts → recipes → shopping` flow through the
API. Coverage is ≥90% on `services/` and the mock provider (definition of done).

## Layout

```
app/
  config.py          # settings + provider resolution
  db.py              # engine, init, seeding
  models/            # enums, SQLModel tables, API schemas
  vision/            # VisionProvider ABC + mock + claude adapters
  services/          # pure domain logic (freshness/inventory/alerts/recipes/shopping)
  routers/           # thin FastAPI endpoints
  seed/              # curated catalog.json + recipes.json
samples/             # labeled SIMULATED fridge scenes
tests/               # unit/ + integration/
```

Conventions are captured as Claude Code skills in `../skills/` (`vision-pipeline`,
`api-schema`).
