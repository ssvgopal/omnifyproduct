"""
Idempotency middleware for POST endpoints.

Honors the `Idempotency-Key` header. Stores a short-lived cache of responses
keyed by (method, path, key, body_hash). Suitable for single-instance use.
For multi-instance, replace storage with Redis.
"""

import asyncio
import hashlib
import json
import time
from typing import Dict, Tuple

from starlette.requests import Request
from starlette.responses import Response, JSONResponse


class InMemoryIdempotencyStore:
    def __init__(self, ttl_seconds: int = 600) -> None:
        self._store: Dict[str, Tuple[float, Dict]] = {}
        self._ttl = ttl_seconds
        self._lock = asyncio.Lock()

    async def get(self, key: str):
        async with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            ts, data = entry
            if time.time() - ts > self._ttl:
                self._store.pop(key, None)
                return None
            return data

    async def set(self, key: str, data: Dict):
        async with self._lock:
            self._store[key] = (time.time(), data)


idempotency_store = InMemoryIdempotencyStore()


async def idempotency_middleware(request: Request, call_next):
    if request.method != "POST":
        return await call_next(request)

    key = request.headers.get("Idempotency-Key")
    if not key:
        return await call_next(request)

    body_bytes = await request.body()
    body_hash = hashlib.sha256(body_bytes).hexdigest()
    cache_key = f"{request.method}:{request.url.path}:{key}:{body_hash}"

    cached = await idempotency_store.get(cache_key)
    if cached is not None:
        return JSONResponse(status_code=cached.get("status_code", 200), content=cached.get("body", {}))

    # Recreate request with consumed body
    async def receive_gen():
        yield {"type": "http.request", "body": body_bytes, "more_body": False}

    new_scope = dict(request.scope)
    new_request = Request(new_scope, receive_gen())
    response: Response = await call_next(new_request)

    try:
        # Only cache JSON bodies
        if "application/json" in response.headers.get("content-type", ""):
            body = json.loads((response.body or b"{}")) if hasattr(response, "body") else {}
        else:
            body = {"cached": True}
        await idempotency_store.set(cache_key, {"status_code": response.status_code, "body": body})
    except Exception:
        pass

    return response


