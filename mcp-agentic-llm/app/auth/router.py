import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Cookie, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from redis.asyncio import Redis

from app.auth.github_oauth import (
    build_authorization_url,
    exchange_code_for_token,
    get_github_user,
)
from app.auth.session import delete_session, save_session
from app.config import settings
from app.schemas.auth import SessionData

router = APIRouter(prefix="/auth", tags=["auth"])

CSRF_STATE_TTL = 300  # 5 minutes


@router.get("/github/login")
async def github_login(request: Request):
    redis: Redis = request.app.state.redis
    state = secrets.token_urlsafe(32)
    await redis.setex(f"oauth_state:{state}", CSRF_STATE_TTL, "1")
    return RedirectResponse(url=build_authorization_url(state))


@router.get("/github/callback")
async def github_callback(request: Request, code: str, state: str):
    redis: Redis = request.app.state.redis

    # CSRF validation
    state_key = f"oauth_state:{state}"
    valid = await redis.get(state_key)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")
    await redis.delete(state_key)

    http_client = request.app.state.http_client
    token = await exchange_code_for_token(http_client, code)
    gh_user = await get_github_user(http_client, token)

    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.session_ttl_seconds)
    session_data = SessionData(
        session_id=session_id,
        github_token=token,
        username=gh_user.get("login", ""),
        email=gh_user.get("email"),
        expires_at=expires_at,
    )
    await save_session(redis, session_id, session_data, settings.session_ttl_seconds)

    response = RedirectResponse(url="/health")
    response.set_cookie(
        key="mcp_session",
        value=session_id,
        httponly=True,
        samesite="lax",
        max_age=settings.session_ttl_seconds,
    )
    return response


@router.get("/logout")
async def logout(request: Request, mcp_session: str | None = Cookie(default=None)):
    redis: Redis = request.app.state.redis
    if mcp_session:
        await delete_session(redis, mcp_session)
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("mcp_session")
    return response


@router.get("/me")
async def me(request: Request, mcp_session: str | None = Cookie(default=None)):
    if not mcp_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    from app.auth.session import load_session
    redis: Redis = request.app.state.redis
    session = await load_session(redis, mcp_session)
    if not session:
        raise HTTPException(status_code=401, detail="Session expired")
    return {"username": session.username, "email": session.email}
