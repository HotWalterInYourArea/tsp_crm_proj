import json
import logging
from typing import Any

import redis

from api_service.core.config import settings

logger = logging.getLogger(__name__)

_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    max_connections=20,
)

redis_client: redis.Redis = redis.Redis(connection_pool=_pool)


def cache_get(key: str) -> Any | None:
    try:
        raw = redis_client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except redis.RedisError as e:
        logger.warning("cache_get failed for %s: %s", key, e)
        return None


def cache_set(key: str, value: Any, ttl: int | None = None) -> None:
    try:
        redis_client.set(
            key,
            json.dumps(value, default=str),
            ex=ttl or settings.CACHE_TTL_SECONDS,
        )
    except redis.RedisError as e:
        logger.warning("cache_set failed for %s: %s", key, e)


def cache_delete(*keys: str) -> None:
    if not keys:
        return
    try:
        redis_client.delete(*keys)
    except redis.RedisError as e:
        logger.warning("cache_delete failed: %s", e)


def cache_delete_pattern(pattern: str) -> None:
    try:
        keys = redis_client.scan_iter(match=pattern, count=500)
        batch = []
        for k in keys:
            batch.append(k)
            if len(batch) >= 500:
                redis_client.delete(*batch)
                batch.clear()
        if batch:
            redis_client.delete(*batch)
    except redis.RedisError as e:
        logger.warning("cache_delete_pattern failed: %s", e)