import hashlib
import json
from typing import Any, Callable

from api_service.core.cache import cache_delete, cache_delete_pattern, cache_get, cache_set


def list_key(prefix: str, **filters) -> str:
    payload = json.dumps(filters, sort_keys=True, default=str)
    return f"{prefix}:list:{hashlib.sha256(payload.encode()).hexdigest()[:16]}"


def get_cached_item(prefix: str, entity_id, mapper: Callable[[dict], Any]) -> Any | None:
    raw = cache_get(f"{prefix}:{entity_id}")
    return mapper(raw) if raw else None


def set_cached_item(prefix: str, entity_id, value: dict, ttl: int | None = None) -> None:
    cache_set(f"{prefix}:{entity_id}", value, ttl)


def get_cached_list(prefix: str, filters: dict, mapper: Callable[[dict], Any]) -> list[Any] | None:
    raw = cache_get(list_key(prefix, **filters))
    return [mapper(item) for item in raw] if raw is not None else None


def set_cached_list(prefix: str, filters: dict, items: list[dict], ttl: int | None = None) -> None:
    cache_set(list_key(prefix, **filters), items, ttl)


def invalidate_item(prefix: str, entity_id) -> None:
    cache_delete(f"{prefix}:{entity_id}")
    cache_delete_pattern(f"{prefix}:list:*")


def invalidate_all(prefix: str) -> None:
    cache_delete_pattern(f"{prefix}:*")