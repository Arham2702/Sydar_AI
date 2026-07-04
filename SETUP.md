# FreshKeep — Setup & Run Guide

Everything needed to get the FreshKeep prototype running locally: a Python
FastAPI **backend** and a Next.js **frontend**. The app runs fully offline out
of the box (no API keys required); adding a Gemini or Claude key upgrades the
vision pipeline from the deterministic mock to a real multimodal model.

> **TL;DR:** run the backend on `:8000`, the frontend on `:3000`, done. Keys are
> optional and only needed for real fridge-photo analysis.

---

## Prerequisites

| Tool | Version | Check |
|---|---|---|
| Python | 3.11+ | `python3 --version` |
| Node.js | 18+ (20 LTS recommended) | `node --version` |
| npm | bundled with Node | `npm --version` |
| git | any recent | `git --version` |

---

## 1. Clone

```bash
git clone <this-repo-url> freshkeep
cd freshkeep
```

---

## 2. Backend (`:8000`)

```bash
cd backend

# create + activate a virtual environment
python3 -m venv .venv

# install dependencies (recommended: installs the package + dev/test tools)
./.venv/bin/pip install -e ".[dev]"
#   — or, using the pinned requirements files —
# ./.venv/bin/pip install -r requirements.txt          # runtime only
# ./.venv/bin/pip install -r requirements-dev.txt      # + test tooling

# run the API
./.venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

- API docs (Swagger UI): <http://localhost:8000/docs>
- Health check: <http://localhost:8000/api/health>
- The SQLite database (`backend/fridge.db`) is created and seeded on first
  startup. **Delete it to reset** all state.

### Quick smoke test

```bash
curl -X POST "http://localhost:8000/api/ingest?sample=fridge_full"  # simulated capture
curl http://localhost:8000/api/inventory
curl http://localhost:8000/api/alerts
curl http://localhost:8000/api/recipes/suggestions
curl http://localhost:8000/api/shopping
```

Available simulated sample scenes: `fridge_full`, `fridge_low`, `fridge_expiring`.

---

## 3. Frontend (`:3000`)

In a **second terminal**:

```bash
cd frontend
npm install
npm run dev
# open http://localhost:3000
```

The frontend expects the backend on `http://localhost:8000`. To point it
elsewhere, copy the example env file and edit it:

```bash
cp .env.local.example .env.local
# then set NEXT_PUBLIC_API_URL=http://your-backend-host:8000
```

Type-check / production build:

```bash
npm run build
```

---

## 4. Enabling real vision (optional) — Gemini API key

By default the backend uses an offline **mock** vision provider — great for
demos and tests, no key needed. To analyze **real fridge photos**, add a Gemini
(or Claude) key.

### Get a Gemini key

1. Go to **<https://aistudio.google.com/apikey>**.
2. Sign in with a Google account and click **Create API key**.
3. Copy the key (starts with `AIza...`).

### Configure it

From `backend/`, create your local env file from the template:

```bash
cp .env.example .env
```

Then edit `backend/.env` and set:

```dotenv
GOOGLE_API_KEY=AIza...your-real-key...
FRIDGE_VISION_PROVIDER=gemini   # optional — auto-detected from the key
```

> `.env` is **git-ignored** and must never be committed. Only `.env.example`
> (with blank values) is tracked.

Alternatively, export it in the shell instead of using a file:

```bash
export GOOGLE_API_KEY=AIza...        # or GEMINI_API_KEY
export FRIDGE_VISION_PROVIDER=gemini # optional
```

Restart the backend, then confirm the provider switched:

```bash
curl http://localhost:8000/api/health          # -> {"vision_provider":"gemini", ...}
curl -F "file=@fridge.jpg" http://localhost:8000/api/ingest   # analyze a real photo
```

The `/api/ingest` response includes `detected_items` (name, count, confidence)
so you can see exactly what the model returned.

### Using Claude instead

Set `ANTHROPIC_API_KEY` (from <https://console.anthropic.com/>) instead of the
Google key. In `auto` mode Claude takes precedence over Gemini.

### All backend settings

| Env var | Default | Purpose |
|---|---|---|
| `FRIDGE_VISION_PROVIDER` | `auto` | `auto` \| `mock` \| `gemini` \| `claude` |
| `GOOGLE_API_KEY` / `GEMINI_API_KEY` | — | Enables Gemini vision |
| `FRIDGE_GEMINI_MODEL` | `gemini-2.5-flash-lite` | Gemini model id |
| `ANTHROPIC_API_KEY` | — | Enables Claude vision |
| `FRIDGE_CLAUDE_MODEL` | `claude-opus-4-8` | Claude model id |
| `FRIDGE_DATABASE_URL` | `sqlite:///./fridge.db` | Database location |
| `FRIDGE_EXPIRING_THRESHOLD` | `0.25` | Shelf-life fraction that flags "expiring" |

See `backend/.env.example` for the full annotated template.

---

## 5. Running the tests

```bash
cd backend
./.venv/bin/python -m pytest                                     # all tests
./.venv/bin/python -m pytest --cov=app --cov-report=term-missing # with coverage
```

Coverage gate is **≥90%** on `app/services/` and the mock provider. Tests use
in-memory SQLite and never touch `fridge.db`, and they run with the mock vision
provider (no network / keys required).

---

## 6. Troubleshooting

| Symptom | Fix |
|---|---|
| Frontend shows no data / network errors | Make sure the backend is running on `:8000` (or set `NEXT_PUBLIC_API_URL`). |
| `/api/health` shows `"mock"` after setting a key | Restart the backend — settings are read once at startup. Confirm the key is set in the same shell. |
| Want to reset all inventory/state | Stop the backend and delete `backend/fridge.db`; it re-seeds on next start. |
| `port already in use` | Change the port (`--port 8001`) or stop the other process. |

---

## Project layout

```
freshkeep/
├── README.md              # project overview
├── SETUP.md               # this file
├── CLAUDE.md              # architecture notes / dev guidance
├── backend/               # FastAPI + SQLModel (Python)
│   ├── .env.example       # copy to .env for keys
│   ├── requirements.txt   # pinned runtime deps
│   ├── pyproject.toml     # canonical dependency + tooling config
│   └── app/               # config, models, vision, services, routers, seed
├── frontend/              # Next.js (App Router, TypeScript, Tailwind)
│   └── .env.local.example # copy to .env.local to override the API URL
└── skills/                # Claude Code skills (vision-pipeline, api-schema)
```
