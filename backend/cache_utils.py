"""TTL caches for public endpoints to reduce Mongo/AI load.
Simple in-memory caches - safe for single-process dev; consider Redis for multi-instance production.
"""
from cachetools import TTLCache

# Public listings - refresh frequently but avoid hitting DB on every visit
categories_cache = TTLCache(maxsize=1, ttl=60)  # 60s
featured_jobs_cache = TTLCache(maxsize=8, ttl=45)  # 45s

# AI responses cache (idempotent queries)
salary_cache = TTLCache(maxsize=512, ttl=3600)  # 1h (same role+location stable)
match_cache = TTLCache(maxsize=1024, ttl=300)  # 5min


def make_key(*parts) -> str:
    return "|".join(str(p) for p in parts)
