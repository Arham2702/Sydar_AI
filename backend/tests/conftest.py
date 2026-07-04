"""Shared pytest fixtures: in-memory SQLite engine, session, and API client."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

from app import db
from app.main import app


@pytest.fixture
def engine():
    """A fresh in-memory SQLite DB per test, seeded with catalog + recipes.

    StaticPool keeps the single in-memory connection alive across the app's
    sessions so seeded data is visible to every request in the test.
    """
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    db.set_engine(eng)
    db.init_db(seed=True)
    yield eng
    db.set_engine(None)
    eng.dispose()


@pytest.fixture
def session(engine) -> Session:
    with Session(engine) as s:
        yield s


@pytest.fixture
def client(engine) -> TestClient:
    with TestClient(app) as c:
        yield c
