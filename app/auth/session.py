import json
from datetime import datetime, timezone
from redis.asyncio import Redis

from app.schemas.auth import SessionData


async def save_session(redis: Redis, session_id: str, data: SessionData, ttl: int) -> None:
    payload = data.model_dump()
    payload["expires_at"] = payload["expires_at"].isoformat()
    await redis.setex(f"session:{session_id}", ttl, json.dumps(payload))


async def load_session(redis: Redis, session_id: str) -> SessionData | None:
    raw = await redis.get(f"session:{session_id}")
    if not raw:
        return None
    payload = json.loads(raw)
    payload["expires_at"] = datetime.fromisoformat(payload["expires_at"])
    session = SessionData(**payload)
    if session.expires_at < datetime.now(timezone.utc):
        await redis.delete(f"session:{session_id}")
        return None
    return session


async def delete_session(redis: Redis, session_id: str) -> None:
    await redis.delete(f"session:{session_id}")
