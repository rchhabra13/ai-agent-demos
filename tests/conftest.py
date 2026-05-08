import pytest
import fakeredis.aioredis as fakeredis
import httpx
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from app.main import create_app
from app.mcp_server.server import mcp, register_tools, set_app_state
from app.schemas.auth import SessionData
from app.auth.session import save_session


@pytest.fixture
async def redis():
    r = fakeredis.FakeRedis(decode_responses=True)
    yield r
    await r.aclose()


@pytest.fixture
def app(redis):
    application = create_app()
    application.state.redis = redis
    application.state.http_client = httpx.AsyncClient()
    return application


@pytest.fixture
async def client(app):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@pytest.fixture
async def session_data(redis):
    sd = SessionData(
        session_id="test-session-123",
        github_token="ghs_test_token",
        username="testuser",
        email="test@example.com",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    await save_session(redis, sd.session_id, sd, 3600)
    return sd


@pytest.fixture
async def authed_client(app, redis, session_data):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
        cookies={"mcp_session": session_data.session_id},
    ) as c:
        yield c
