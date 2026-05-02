"""Simple in-memory token-bucket rate limiter for public AI endpoints.
Avoid abuse without needing Redis. Per-identity (IP+user_id) keyed.
"""
import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import HTTPException, Request, Depends

# Bucket: { key -> (tokens, last_refill_ts) }
_buckets: Dict[str, Tuple[float, float]] = defaultdict(lambda: (0.0, 0.0))


def _get_key(request: Request) -> str:
    # Best-effort IP (trust X-Forwarded-For from ingress)
    fwd = request.headers.get("x-forwarded-for", "")
    ip = fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "unknown")
    # Include auth token tail if present to distinguish same-IP users
    auth = request.headers.get("authorization", "")
    tail = auth[-16:] if auth else "anon"
    return f"{ip}:{tail}"


def rate_limit(capacity: int = 10, refill_per_sec: float = 0.25):
    """Token bucket dependency. Defaults: 10 tokens, refill 1 every 4s (~15/min)."""

    async def _dep(request: Request):
        key = _get_key(request)
        now = time.time()
        tokens, last = _buckets[key]
        if last == 0.0:
            tokens = float(capacity)
            last = now
        else:
            elapsed = max(0.0, now - last)
            tokens = min(capacity, tokens + elapsed * refill_per_sec)
            last = now
        if tokens < 1.0:
            _buckets[key] = (tokens, last)
            retry_after = int((1.0 - tokens) / max(refill_per_sec, 1e-9)) + 1
            raise HTTPException(
                status_code=429,
                detail=f"Terlalu banyak permintaan AI. Coba lagi dalam {retry_after} detik.",
            )
        tokens -= 1.0
        _buckets[key] = (tokens, last)
        return True

    return _dep
