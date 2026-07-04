"""FastAPI application: wires routers, CORS, and DB initialization.

Serves the fridge platform JSON API under /api. Vision defaults to the offline
mock provider; set ANTHROPIC_API_KEY to switch to the real Claude vision path.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db import init_db
from .routers import alerts, ingest, inventory, recipes, shopping


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(seed=True)
    yield


app = FastAPI(
    title="Fridge HaaS Platform API",
    version="0.1.0",
    description="Phase 1 software platform for a smart-fridge Hardware-as-a-Service product.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(inventory.router)
app.include_router(alerts.router)
app.include_router(recipes.router)
app.include_router(shopping.router)


@app.get("/api/health", tags=["health"])
def health() -> dict:
    return {"status": "ok", "vision_provider": get_settings().resolved_provider()}
