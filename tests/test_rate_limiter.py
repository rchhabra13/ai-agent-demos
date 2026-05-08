import pytest
import fakeredis.aioredis as fakeredis
import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.middleware.rate_limiter import TokenBucketMiddleware


def _make_app(capacity: int, window: int, fake_redis):
    inner = FastAPI()

    @inner.get("/test")
    async def endpoint():
        return JSONResponse({"ok": True})

    inner.add_middleware(
        TokenBucketMiddleware,
        redis=fake_redis,
        capacity=capacity,
        window_seconds=window,
    )
    return inner


@pytest.mark.asyncio
async def test_allows_within_limit():
    fake = fakeredis.FakeRedis(decode_responses=True)
    app = _make_app(capacity=5, window=60, fake_redis=fake)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        for _ in range(5):
            r = await c.get("/test")
            assert r.status_code == 200


@pytest.mark.asyncio
async def test_blocks_over_limit():
    fake = fakeredis.FakeRedis(decode_responses=True)
    app = _make_app(capacity=3, window=60, fake_redis=fake)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        for _ in range(3):
            await c.get("/test")
        r = await c.get("/test")
        assert r.status_code == 429
        assert "Retry-After" in r.headers


@pytest.mark.asyncio
async def test_health_bypasses_rate_limit():
    fake = fakeredis.FakeRedis(decode_responses=True)
    inner = FastAPI()

    @inner.get("/health")
    async def health():
        return {"ok": True}

    inner.add_middleware(TokenBucketMiddleware, redis=fake, capacity=1, window_seconds=3600)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=inner), base_url="http://test") as c:
        for _ in range(5):
            r = await c.get("/health")
            assert r.status_code == 200


@pytest.mark.asyncio
async def test_remaining_header_present():
    fake = fakeredis.FakeRedis(decode_responses=True)
    app = _make_app(capacity=10, window=60, fake_redis=fake)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/test")
        assert "X-RateLimit-Remaining" in r.headers
        assert int(r.headers["X-RateLimit-Remaining"]) == 9
