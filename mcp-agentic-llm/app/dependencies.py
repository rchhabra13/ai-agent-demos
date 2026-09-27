from fastapi import Cookie, HTTPException, Request
from redis.asyncio import Redis

from app.auth.session import load_session
from app.schemas.auth import SessionData


async def get_redis(request: Request) -> Redis:
    return request.app.state.redis


async def get_current_user(
    request: Request,
    mcp_session: str | None = Cookie(default=None),
) -> SessionData:
    if not mcp_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    redis: Redis = request.app.state.redis
    session = await load_session(redis, mcp_session)
    if not session:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    return session
