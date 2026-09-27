import pytest
from datetime import datetime, timedelta, timezone

from app.auth.session import save_session, load_session, delete_session
from app.schemas.auth import SessionData


@pytest.mark.asyncio
async def test_save_and_load_session(redis):
    sd = SessionData(
        session_id="abc123",
        github_token="token",
        username="user",
        email="u@example.com",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    await save_session(redis, "abc123", sd, 3600)
    loaded = await load_session(redis, "abc123")
    assert loaded is not None
    assert loaded.username == "user"
    assert loaded.github_token == "token"


@pytest.mark.asyncio
async def test_load_missing_session_returns_none(redis):
    result = await load_session(redis, "nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_delete_session(redis):
    sd = SessionData(
        session_id="del123",
        github_token="t",
        username="u",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    await save_session(redis, "del123", sd, 3600)
    await delete_session(redis, "del123")
    assert await load_session(redis, "del123") is None


@pytest.mark.asyncio
async def test_expired_session_returns_none(redis):
    sd = SessionData(
        session_id="exp123",
        github_token="t",
        username="u",
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    await save_session(redis, "exp123", sd, 3600)
    result = await load_session(redis, "exp123")
    assert result is None


@pytest.mark.asyncio
async def test_login_redirects_to_github(client):
    resp = await client.get("/auth/github/login", follow_redirects=False)
    assert resp.status_code in (302, 307)
    assert "github.com/login/oauth/authorize" in resp.headers["location"]


@pytest.mark.asyncio
async def test_me_unauthenticated(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(authed_client):
    resp = await authed_client.get("/auth/me")
    assert resp.status_code == 200
    assert resp.json()["username"] == "testuser"


@pytest.mark.asyncio
async def test_logout_clears_session(authed_client, redis, session_data):
    resp = await authed_client.get("/auth/logout")
    assert resp.status_code == 200
    # session gone from redis
    remaining = await load_session(redis, session_data.session_id)
    assert remaining is None
