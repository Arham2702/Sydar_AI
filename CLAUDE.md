# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

FreshKeep is the Phase-1 **software** platform for a smart-fridge Hardware-as-a-Service product: an image of a fridge is ingested, turned into structured inventory, and drives freshness scoring, alerts, recipe matching, and a shopping list. No physical device exists yet (image input is files or labeled **simulated** sample scenes) and there is no auth (single implicit session).

## Commands

Monorepo: Python backend in `backend/`, Next.js frontend in `frontend/`.

**Backend** (Python 3.11+, FastAPI + SQLModel). All commands run from `backend/`; the venv Python is `./.venv/bin/python`:
```bash
python3 -m venv .venv && ./.venv/bin/pip install -e ".[dev]"   # setup
./.venv/bin/python -m uvicorn app.main:app --reload --port 8000  # run (docs at /docs)
./.venv/bin/python -m pytest                                     # all tests
./.venv/bin/python -m pytest --cov=app --cov-report=term-missing # tests + coverage
./.venv/bin/python -m pytest tests/unit/test_freshness.py        # single file
./.venv/bin/python -m pytest -k "reconcile"                      # single test / pattern
```
The SQLite DB (`backend/fridge.db`) is created and seeded on startup; delete it to reset. Tests use in-memory SQLite and never touch it.

**Frontend** (Next.js App Router, TypeScript, Tailwind). From `frontend/`:
```bash
npm install
npm run dev     # http://localhost:3000 (expects backend on :8000; set NEXT_PUBLIC_API_URL to override)
npm run build   # also type-checks — run this to verify TS changes
```

## Architecture

Flow: `POST /api/ingest` (each capture replaces inventory by default — `inventory.reset` + `shopping.clear_auto`, override with `reset=false`) → **VisionProvider** produces `Detection`s → `services.inventory.reconcile` upserts `FridgeItem`s + writes an append-only `InventoryEvent` log → a **post-ingest recompute hook** regenerates alerts + shopping list, and (when a Gemini key is present) refreshes recipes from the new inventory → JSON API → Next.js pages fetch it client-side.

**Vision is pluggable and selected at runtime** (`app/vision/`). `get_vision_provider()` reads `config.get_settings().resolved_provider()`:
- Default `MockVisionProvider` — deterministic, offline, driven by fixtures in `backend/samples/*.expected.json`. Used by all tests and demos.
- `ClaudeVisionProvider` / `GeminiVisionProvider` — real multimodal models, activated by `ANTHROPIC_API_KEY` / `GOOGLE_API_KEY` (in `auto` mode Claude wins, then Gemini, else mock; force with `FRIDGE_VISION_PROVIDER=claude|gemini|mock`). Their network `analyze()` is excluded from the coverage gate, but their pure response-parsing helpers (e.g. `gemini_provider.parse_detections`) are unit-tested.

Everything downstream depends only on the `Detection` contract (`app/vision/base.py`), so providers are interchangeable. Real detections are **unconstrained** (any item, not just the catalog); catalog names are passed to real providers as a naming hint only.

**Domain logic lives in pure `app/services/` modules**, independent of FastAPI — routers are thin (parse → call service → wrap in `Envelope`). Key non-obvious behaviors:
- **Freshness** (`services/freshness.py`) is derived, not authored. `score_item` prefers a vision model's stored `visual_freshness` (0–100, judged from the item's appearance) when present; otherwise it's a pure function of age (now − `first_seen_at`) vs. shelf life shaped by `FreshnessProfile`. Catalog items use their authored shelf life; un-catalogued detections estimate it from the detected category, then a generic default.
- **Alerts and the shopping list are regenerated from current state, not persisted incrementally.** `alerts.regenerate_alerts` and `shopping.auto_populate` are idempotent (dedup by `(item, type)` / by name), and are re-run by the recompute hook after every ingest and manual inventory adjust (see `routers/ingest.py`, `routers/inventory.py`). Acknowledged alerts survive regeneration; manual shopping items are never overwritten by auto entries.
- **Recipes** (`services/recipes.py` = scoring; `services/recipe_search.py` = generation). An ingredient is "owned" via `catalog_item_id` or lowercased-name match against in-stock items; suggestions are sorted by owned-ingredient fraction. With a Gemini key, the ingest hook calls `recipe_search.refresh_from_inventory`, which asks Gemini for recipes matching current inventory and **replaces** the `Recipe`/`RecipeIngredient` tables (so the detail endpoint still works by id). With no key, the seeded recipes are the fallback.

**Data model** (`app/models/`): `entities.py` = SQLModel tables, `enums.py`, `schemas.py` = Pydantic API contracts (kept separate from tables; routers map entity→`*Read` via a service `to_read`). Seed data (curated catalog + recipes) is JSON in `app/seed/`, loaded by `db.init_db`.

**Simulated-data honesty:** sample scenes are labeled SIMULATED; API responses and the UI carry `simulated: true` / a "Simulated feed" badge. Fixtures use a `sim_age_days` field (a documented demo aid) so freshness decay is visible without waiting real days — reconciliation backdates `first_seen_at` from it. Real uploads have no `sim_age_days` and start fresh from now.

## Conventions (project skills)

Two skills in `skills/` codify repeated structured work — read them before the matching change:
- **`vision-pipeline`** — adding a `VisionProvider` or a labeled sample scene (the `Detection` schema, fixture format, determinism rule).
- **`api-schema`** — endpoint conventions: the `{data, meta}` `Envelope`, table/schema separation, the recompute-hook requirement on stock/freshness mutations, and a per-endpoint integration-test checklist.

## Testing expectations

Testing is a definition-of-done requirement, not a follow-up. Every `services/` module and the mock vision provider have unit tests (frozen `now` for determinism); `tests/integration/` drives the full ingest→inventory→freshness→alerts→recipes→shopping flow through the API. Coverage gate is **≥90% on `app/services/` and the mock provider**. Note: `config.get_settings()` is `lru_cache`d, so provider-selection tests must set env vars before the first settings access.
