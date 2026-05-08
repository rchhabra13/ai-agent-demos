from contextlib import asynccontextmanager
from dataclasses import dataclass

import httpx
from redis.asyncio import Redis


@dataclass
class AppContext:
    redis: Redis
    http_client: httpx.AsyncClient


@asynccontextmanager
async def mcp_lifespan(server):
    # MCP server gets its own context; shared clients injected via app.state at mount time
    # This lifespan is a no-op placeholder — actual clients come from the FastAPI app state.
    yield AppContext(redis=None, http_client=None)
