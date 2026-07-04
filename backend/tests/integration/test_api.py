"""Integration tests — full vertical slice through the HTTP API."""
from __future__ import annotations


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["vision_provider"] == "mock"


def test_ingest_sample_populates_inventory(client):
    resp = client.post("/api/ingest", params={"sample": "fridge_full"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["simulated"] is True
    assert body["data"]["items_created"] > 0
    assert body["meta"]["sample"] == "fridge_full"

    inv = client.get("/api/inventory").json()
    assert inv["meta"]["count"] == body["data"]["items_created"]
    # Every item carries computed freshness.
    assert all("freshness" in i and "level" in i["freshness"] for i in inv["data"])


def test_ingest_resets_inventory_by_default(client):
    client.post("/api/ingest", params={"sample": "fridge_full"})
    full = {i["name"] for i in client.get("/api/inventory").json()["data"]}
    assert "Carrots" in full  # in full scene, not in the low scene

    client.post("/api/ingest", params={"sample": "fridge_low"})
    low = {i["name"] for i in client.get("/api/inventory").json()["data"]}
    # Inventory now reflects ONLY the second capture.
    assert "Carrots" not in low
    assert low == {"Milk", "Eggs", "Tomatoes", "Butter", "Ketchup"}


def test_ingest_reset_false_accumulates(client):
    client.post("/api/ingest", params={"sample": "fridge_full"})
    client.post("/api/ingest", params={"sample": "fridge_low", "reset": "false"})
    names = {i["name"] for i in client.get("/api/inventory").json()["data"]}
    assert "Carrots" in names  # kept from first capture
    assert "Ketchup" in names  # added by second capture


def test_ingest_surfaces_vision_quota_error(client, monkeypatch):
    from app.routers import ingest as ingest_router
    from app.vision.base import VisionError

    class _Boom:
        def analyze(self, image_bytes, *, sample_name=None):
            raise VisionError("Gemini rate limit or quota exceeded.", status_code=429)

    monkeypatch.setattr(ingest_router, "get_vision_provider", lambda names: _Boom())
    resp = client.post("/api/ingest", params={"sample": "fridge_full"})
    assert resp.status_code == 429
    detail = resp.json()["detail"].lower()
    assert "quota" in detail or "rate limit" in detail


def test_ingest_unknown_sample_404(client):
    resp = client.post("/api/ingest", params={"sample": "nope"})
    assert resp.status_code == 404


def test_default_ingest_uses_full_scene(client):
    resp = client.post("/api/ingest")  # no sample, no file
    assert resp.status_code == 200
    assert resp.json()["meta"]["sample"] == "fridge_full"


def test_ingest_uploaded_file(client):
    resp = client.post(
        "/api/ingest", files={"file": ("frame.png", b"\x89PNG\r\n\x1a\nfake", "image/png")}
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["detections"] >= 0


def test_full_flow_expiring_scene(client):
    client.post("/api/ingest", params={"sample": "fridge_expiring"})

    alerts = client.get("/api/alerts").json()
    assert alerts["meta"]["count"] > 0
    types = {a["alert_type"] for a in alerts["data"]}
    assert "expired" in types or "expiring" in types

    suggestions = client.get("/api/recipes/suggestions").json()["data"]
    assert len(suggestions) == 12  # all seed recipes ranked
    # Sorted by match score descending.
    scores = [s["match_score"] for s in suggestions]
    assert scores == sorted(scores, reverse=True)

    shopping = client.get("/api/shopping").json()
    assert shopping["meta"]["count"] > 0  # low/out items auto-added


def test_recipe_detail_owned_vs_missing(client):
    client.post("/api/ingest", params={"sample": "fridge_full"})
    suggestions = client.get("/api/recipes/suggestions").json()["data"]
    recipe_id = suggestions[0]["id"]
    detail = client.get(f"/api/recipes/{recipe_id}").json()["data"]
    assert "ingredients" in detail
    assert detail["owned_count"] <= detail["required_count"]


def test_recipe_not_found(client):
    assert client.get("/api/recipes/9999").status_code == 404


def test_add_missing_to_shopping(client):
    client.post("/api/ingest", params={"sample": "fridge_low"})
    suggestions = client.get("/api/recipes/suggestions").json()["data"]
    # Pick a recipe with missing ingredients.
    target = next(s for s in suggestions if s["match_score"] < 1.0)
    resp = client.post(f"/api/recipes/{target['id']}/add-missing")
    assert resp.status_code == 200
    assert resp.json()["meta"]["added"] >= 1


def test_inventory_manual_adjust_updates_alerts(client):
    client.post("/api/ingest", params={"sample": "fridge_full"})
    inv = client.get("/api/inventory").json()["data"]
    item = next(i for i in inv if i["name"] == "Eggs")
    resp = client.patch(f"/api/inventory/{item['id']}", json={"quantity": 0})
    assert resp.status_code == 200
    assert resp.json()["data"]["quantity"] == 0
    # Out-of-stock alert now exists for Eggs.
    alerts = client.get("/api/alerts").json()["data"]
    assert any(a["item_name"] == "Eggs" and a["alert_type"] == "out_of_stock" for a in alerts)


def test_adjust_missing_item_404(client):
    assert client.patch("/api/inventory/9999", json={"quantity": 1}).status_code == 404


def test_acknowledge_alert(client):
    client.post("/api/ingest", params={"sample": "fridge_expiring"})
    alerts = client.get("/api/alerts").json()["data"]
    alert_id = alerts[0]["id"]
    resp = client.post(f"/api/alerts/{alert_id}/ack")
    assert resp.status_code == 200
    assert resp.json()["data"]["acknowledged"] is True

    unack = client.get("/api/alerts", params={"unacknowledged_only": True}).json()["data"]
    assert all(a["id"] != alert_id for a in unack)


def test_shopping_crud(client):
    created = client.post("/api/shopping", json={"name": "Coffee", "quantity": 2}).json()["data"]
    assert created["source"] == "manual"

    updated = client.patch(
        f"/api/shopping/{created['id']}", json={"status": "purchased"}
    ).json()["data"]
    assert updated["status"] == "purchased"

    assert client.delete(f"/api/shopping/{created['id']}").status_code == 204
    assert client.delete("/api/shopping/9999").status_code == 404


def test_shopping_validation_error(client):
    # Missing required 'name' field -> 422.
    assert client.post("/api/shopping", json={"quantity": 1}).status_code == 422
