"""AttritionIQ — Rate Limiter Middleware"""

import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """In-memory IP rate limiter for API endpoints."""

    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.ip_store = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()

        # Clean timestamps older than 60 seconds
        timestamps = [ts for ts in self.ip_store[client_ip] if now - ts < 60]
        self.ip_store[client_ip] = timestamps

        if len(timestamps) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded. Please try again later."},
            )

        self.ip_store[client_ip].append(now)
        return await call_next(request)
