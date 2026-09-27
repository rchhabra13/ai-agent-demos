# mcp-agentic-server

An enterprise-grade MCP (Model Context Protocol) server that lets LLM agents like Claude securely call real APIs as tools. Built this to explore how you can give agents actual capabilities — GitHub, internal databases, LLM calls — all behind proper auth and rate limiting.

## What it does

- Exposes GitHub API (list repos, create issues) and a mock internal CRUD API as MCP tools
- GitHub OAuth2 login to protect all MCP endpoints
- Token-bucket rate limiter backed by Redis (handles 500 req/min)
- Works with Claude Desktop out of the box via `mcp-remote`
- One-command spin-up with Docker Compose

## Architecture

```
Claude Desktop ──stdio──> mcp-remote ──HTTP POST /mcp──> FastAPI :8000
                                                               │
                                          ┌────────────────────┤
                                   TokenBucketMiddleware (Redis)
                                          │
                              ┌───────────┼───────────────┐
                           /auth       /mcp,/sse        /api
                        GitHub OAuth   MCP Tools       CRUD REST
                              │            │
                           Redis      github_tools ──> api.github.com
                          Sessions    crud_tools   ──> SQLite
                                      llm_tools    ──> LLM_BASE_URL
```

## Quick Start

**Prerequisites:** Docker, Docker Compose, a GitHub OAuth App

### 1. Create a GitHub OAuth App

Go to [GitHub Settings → Developer Settings → OAuth Apps](https://github.com/settings/developers) and create a new app:
- **Homepage URL:** `http://localhost:8000`
- **Authorization callback URL:** `http://localhost:8000/auth/github/callback`

### 2. Configure environment

```bash
cp .env.example .env
```

Fill in your values:
```env
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_client_secret
SESSION_SECRET_KEY=some-random-32-char-string

# Point to any OpenAI-compatible endpoint
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your_api_key
LLM_MODEL=gpt-4o
```

### 3. Start the server

```bash
docker-compose up --build
```

Server runs at `http://localhost:8000`. Check it:
```bash
curl http://localhost:8000/health
# {"status": "ok", "redis": true}
```

### 4. Authenticate

Open your browser → `http://localhost:8000/auth/github/login` → authorize with GitHub → you're in.

### 5. Connect Claude Desktop

Add this to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-agentic-server": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8000/mcp"]
    }
  }
}
```

Restart Claude Desktop. `mcp-remote` will open a browser window for GitHub OAuth on first connection, then cache the token. You should see the tools appear in Claude's tool picker.

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `list_github_repos` | List public repos for any GitHub user |
| `create_github_issue` | Create an issue in any repo you have access to |
| `create_user` | Add a user to the internal database |
| `get_user` | Look up a user by ID |
| `create_item` | Create an item owned by a user |
| `list_items` | List items, optionally filtered by owner |
| `ask_llm` | Send a prompt to your configured LLM endpoint |

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check (no auth needed) |
| `GET /auth/github/login` | Start OAuth flow |
| `GET /auth/github/callback` | OAuth callback |
| `GET /auth/me` | Get current user info |
| `GET /auth/logout` | Logout |
| `POST /mcp` | MCP Streamable HTTP transport |
| `GET /sse` | MCP legacy SSE transport |
| `POST /api/users` | Create user |
| `GET /api/users/{id}` | Get user |
| `POST /api/items` | Create item |
| `GET /api/items` | List items |

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v --cov=app --cov-report=term-missing
```

## Rate Limiting

Every authenticated user gets a token bucket of **500 requests/minute**. Unauthenticated requests are rate-limited by IP. Exceeded requests get `HTTP 429` with a `Retry-After` header. The `/health` and `/auth` paths are excluded.

Headers on each allowed response:
```
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 499
```

## Stack

- **FastAPI** + **uvicorn** — async Python web framework
- **MCP Python SDK** (`mcp[cli]`) — Anthropic's Model Context Protocol
- **Redis** — rate limiting + session storage
- **SQLite** + **SQLModel** + **aiosqlite** — async database for mock internal API
- **httpx** — async HTTP client for GitHub API and LLM calls
- **Docker Compose** — one-command deployment

## Results

### Test Suite

```
29 passed in 0.31s
```

| Module | Coverage |
|--------|----------|
| `middleware/rate_limiter.py` | **100%** |
| `auth/session.py` | **100%** |
| `schemas/` | **100%** |
| `config.py` | **100%** |
| `crud/database.py` | **100%** |
| Overall | **60%** |

### Performance (measured locally, Docker Compose)

| Metric | Result |
|--------|--------|
| Health check latency | **3.7ms** |
| API endpoint latency (p50) | **~5ms** |
| Concurrent throughput (20 workers, 100 req) | **~558 req/s** |
| Rate limiter | Correctly 429s after 500 req/min per IP |
| Docker cold start | ~15s (Redis health check gating app) |

### Rate Limiter in Action

```
x-ratelimit-limit: 500
x-ratelimit-remaining: 496
```

After 500 requests within 60s:
```json
{"detail": "Rate limit exceeded"}
// HTTP 429 + Retry-After header
```

### Docker Stack

```
CONTAINER    IMAGE              STATUS
mcp-app-1    mcp-app            Up (healthy)   :8000
mcp-redis-1  redis:7.4-alpine   Up (healthy)   :6379
```
