import pytest
import redis.asyncio as aioredis
import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.middleware.rate_limiter import TokenBucketMiddleware

TEST_REDIS_URL = "redis://localhost:6379/15"


async def _make_redis() -> aioredis.Redis:
    r = aioredis.from_url(TEST_REDIS_URL, decode_responses=True)
    await r.flushdb()
    return r


def _make_app(capacity: int, window: int, redis_client) -> FastAPI:
    inner = FastAPI()

    @inner.get("/test")
    async def endpoint():
        return JSONResponse({"ok": True})

    inner.add_middleware(
        TokenBucketMiddleware,
        redis=redis_client,
        capacity=capacity,
        window_seconds=window,
    )
    return inner


@pytest.mark.asyncio
async def test_allows_within_limit():
    r = await _make_redis()
    app = _make_app(capacity=5, window=60, redis_client=r)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        for _ in range(5):
            resp = await c.get("/test")
            assert resp.status_code == 200
    await r.aclose()


@pytest.mark.asyncio
async def test_blocks_over_limit():
    r = await _make_redis()
    app = _make_app(capacity=3, window=60, redis_client=r)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        for _ in range(3):
            await c.get("/test")
        resp = await c.get("/test")
        assert resp.status_code == 429
        assert "Retry-After" in resp.headers
    await r.aclose()


@pytest.mark.asyncio
async def test_health_bypasses_rate_limit():
    r = await _make_redis()
    inner = FastAPI()

    @inner.get("/health")
    async def health():
        return {"ok": True}

    inner.add_middleware(TokenBucketMiddleware, redis=r, capacity=1, window_seconds=3600)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=inner), base_url="http://test") as c:
        for _ in range(5):
            resp = await c.get("/health")
            assert resp.status_code == 200
    await r.aclose()


@pytest.mark.asyncio
async def test_remaining_header_present():
    r = await _make_redis()
    app = _make_app(capacity=10, window=60, redis_client=r)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        resp = await c.get("/test")
        assert "X-RateLimit-Remaining" in resp.headers
        assert int(resp.headers["X-RateLimit-Remaining"]) == 9
    await r.aclose()
