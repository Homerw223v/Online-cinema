import asyncio

import backoff
import psycopg
from psycopg import OperationalError
from redis import Redis

from src.core.config import settings


@backoff.on_predicate(wait_gen=backoff.expo, max_time=120)
async def wait_for_redis() -> bool:
    return Redis(**settings.redis.model_dump()).ping()


@backoff.on_predicate(wait_gen=backoff.expo, max_time=120)
async def wait_for_postgres() -> bool:
    try:
        psycopg.connect(**settings.postgres.model_dump())
        return True
    except OperationalError:
        return False


if __name__ == '__main__':
    asyncio.run(wait_for_redis())
    asyncio.run(wait_for_postgres())
