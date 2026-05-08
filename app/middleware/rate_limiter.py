import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Atomic token-bucket Lua script
_LUA_SCRIPT = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local cost = tonumber(ARGV[4])

local tokens = tonumber(redis.call('HGET', key, 'tokens'))
local last = tonumber(redis.call('HGET', key, 'last'))

if tokens == nil then tokens = capacity end
if last == nil then last = now end

local elapsed = now - last
local new_tokens = math.min(capacity, tokens + elapsed * rate)

if new_tokens < cost then
    local retry_after = math.ceil((cost - new_tokens) / rate)
    return {0, retry_after}
end

new_tokens = new_tokens - cost
redis.call('HMSET', key, 'tokens', new_tokens, 'last', now)
redis.call('EXPIRE', key, 120)
return {1, math.floor(new_tokens)}
"""

_SKIP_PREFIXES = ("/health", "/auth")


class TokenBucketMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis, capacity: int, window_seconds: int):
        super().__init__(app)
        self._redis_override = redis  # may be None; falls back to app.state.redis
        self._capacity = capacity
        self._rate = capacity / window_seconds  # tokens per second

    def _get_redis(self, request: Request):
        if self._redis_override is not None:
            return self._redis_override
        return request.app.state.redis

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if any(path.startswith(p) for p in _SKIP_PREFIXES):
            return await call_next(request)

        redis = self._get_redis(request)
        session_id = request.cookies.get("mcp_session")
        key = f"ratelimit:{session_id}" if session_id else f"ratelimit:ip:{request.client.host}"

        now = time.time()
        result = await redis.eval(
            _LUA_SCRIPT, 1, key,
            self._capacity, self._rate, now, 1
        )
        allowed, value = int(result[0]), int(result[1])

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers={"Retry-After": str(value)},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(value)
        response.headers["X-RateLimit-Limit"] = str(self._capacity)
        return response
