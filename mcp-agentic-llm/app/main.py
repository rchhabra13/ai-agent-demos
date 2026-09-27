import os
from contextlib import asynccontextmanager

import httpx
import redis.asyncio as aioredis
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.auth.router import router as auth_router
from app.auth.session import load_session
from app.config import settings
from app.crud.database import create_db_tables
from app.crud.router import router as crud_router
from app.middleware.rate_limiter import TokenBucketMiddleware
from app.mcp_server.server import mcp, register_tools, set_app_state


class AuthGuardMiddleware(BaseHTTPMiddleware):
    """Rejects unauthenticated requests to MCP endpoints."""

    _PROTECTED = ("/mcp", "/sse")

    async def dispatch(self, request: Request, call_next):
        if not any(request.url.path.startswith(p) for p in self._PROTECTED):
            return await call_next(request)

        session_id = request.cookies.get("mcp_session")
        if not session_id:
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required. Visit /auth/github/login"},
            )

        redis = request.app.state.redis
        session = await load_session(redis, session_id)
        if not session:
            return JSONResponse(
                status_code=401,
                content={"detail": "Session expired. Visit /auth/github/login"},
            )

        # Inject session into app state so MCP tools can read the GitHub token
        set_app_state({
            "session": session,
            "http_client": request.app.state.http_client,
            "redis": redis,
        })
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    os.makedirs("data", exist_ok=True)
    await create_db_tables()

    redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    http_client = httpx.AsyncClient(timeout=30.0)

    app.state.redis = redis
    app.state.http_client = http_client

    # Register MCP tools (done once at startup)
    register_tools()

    yield

    # Shutdown
    await redis.aclose()
    await http_client.aclose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="mcp-agentic-server",
        description="Enterprise MCP Server for Agentic LLMs",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Middleware (outermost first)
    app.add_middleware(
        TokenBucketMiddleware,
        redis=None,  # patched below — Redis not available at class-definition time
        capacity=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )
    app.add_middleware(AuthGuardMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(auth_router)
    app.include_router(crud_router)

    # MCP ASGI apps
    mcp_http_app = mcp.streamable_http_app()
    mcp_sse_app = mcp.sse_app()
    app.mount("/mcp", mcp_http_app)
    app.mount("/sse", mcp_sse_app)

    @app.get("/health", tags=["health"])
    async def health(request: Request):
        redis_ok = False
        try:
            redis_ok = await request.app.state.redis.ping()
        except Exception:
            pass
        return {"status": "ok", "redis": redis_ok}

    return app


app = create_app()
