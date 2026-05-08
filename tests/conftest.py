import os

# Set test DB to in-memory BEFORE any app modules are imported
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

import pytest
import fakeredis as _fakeredis
import fakeredis.aioredis as fakeredis
import httpx
from datetime import datetime, timedelta, timezone

from app.crud.database import create_db_tables
from app.main import create_app
from app.schemas.auth import SessionData
from app.auth.session import save_session


@pytest.fixture
async def redis():
    # FakeServer auto-enables Lua when lupa is installed
    server = _fakeredis.FakeServer()
    r = fakeredis.FakeRedis(server=server, decode_responses=True)
    yield r
    await r.aclose()


@pytest.fixture
async def app(redis):
    application = create_app()
    application.state.redis = redis
    application.state.http_client = httpx.AsyncClient()
    # Create tables (lifespan not run in tests)
    await create_db_tables()
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
