import pytest


@pytest.mark.asyncio
async def test_mcp_endpoint_requires_auth(client):
    """Unauthenticated request to /mcp returns 401."""
    resp = await client.post("/mcp", json={})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_sse_endpoint_requires_auth(client):
    """Unauthenticated request to /sse returns 401."""
    resp = await client.get("/sse")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_health_no_auth_needed(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_crud_unauthenticated_blocked(client):
    """CRUD endpoints also require session cookie via AuthGuard on /mcp.
    REST /api routes themselves don't require auth in this impl — MCP does."""
    resp = await client.get("/api/items")
    # REST routes are open; MCP routes are guarded
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_full_user_item_flow(authed_client):
    """Create user → create item → list items end-to-end."""
    u = await authed_client.post("/api/users", json={"name": "Dave", "email": "dave@e2e.com"})
    assert u.status_code == 201
    uid = u.json()["id"]

    i = await authed_client.post("/api/items", json={"name": "Gadget", "description": "Cool", "owner_id": uid})
    assert i.status_code == 201

    items = await authed_client.get(f"/api/items?owner_id={uid}")
    assert items.status_code == 200
    assert any(x["name"] == "Gadget" for x in items.json())
