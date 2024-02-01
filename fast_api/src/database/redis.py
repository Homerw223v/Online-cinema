from typing import Awaitable

from core.config import project_settings
from models.abstract_models.abstract_cache import AbstractCache
from redis.asyncio import Redis

redis: Redis | None = None


class RedisCache(AbstractCache):

    def __init__(self, redis_client: Redis, expired_time: int = 100):
        self._redis = redis_client
        self._expired = expired_time

    async def get(self, key: str):
        result = await self._redis.get(key)
        return result

    async def set(self, key: str, value: str | int | float, expired: int | None = None):
        await self._redis.set(key, value, expired or self._expired)

    async def exists(self, key: str) -> Awaitable[bool]:
        """Check whether the key exists or not."""

        result = await self._redis.exists(key)
        return result

    async def delete(self, keys: list[str]):
        """Delete key from cache"""
        for k in keys:
            await self._redis.delete(k)

    async def flush(self):
        """Erase cache"""
        await self._redis.flushdb(asynchronous=True)


async def get_cache() -> RedisCache:
    return RedisCache(redis, expired_time=project_settings.cache_expire)
