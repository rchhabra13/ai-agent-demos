import pytest


@pytest.mark.asyncio
async def test_create_and_get_user(authed_client):
    r = await authed_client.post("/api/users", json={"name": "Alice", "email": "alice@example.com"})
    assert r.status_code == 201
    user = r.json()
    assert user["name"] == "Alice"
    assert user["id"] is not None

    r2 = await authed_client.get(f"/api/users/{user['id']}")
    assert r2.status_code == 200
    assert r2.json()["email"] == "alice@example.com"


@pytest.mark.asyncio
async def test_duplicate_email_returns_409(authed_client):
    await authed_client.post("/api/users", json={"name": "Bob", "email": "bob@dup.com"})
    r = await authed_client.post("/api/users", json={"name": "Bob2", "email": "bob@dup.com"})
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_get_nonexistent_user(authed_client):
    r = await authed_client.get("/api/users/99999")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_create_and_list_items(authed_client):
    user_r = await authed_client.post("/api/users", json={"name": "Carol", "email": "carol@example.com"})
    uid = user_r.json()["id"]

    r = await authed_client.post("/api/items", json={"name": "Widget", "description": "A widget", "owner_id": uid})
    assert r.status_code == 201
    assert r.json()["name"] == "Widget"

    list_r = await authed_client.get(f"/api/items?owner_id={uid}")
    assert list_r.status_code == 200
    assert any(i["name"] == "Widget" for i in list_r.json())


@pytest.mark.asyncio
async def test_create_item_missing_owner(authed_client):
    r = await authed_client.post("/api/items", json={"name": "Ghost", "description": "", "owner_id": 99999})
    assert r.status_code == 404
