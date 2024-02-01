import asyncio
import os
import sys

import backoff
import psycopg
from psycopg import OperationalError
from redis import Redis

# see https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from settings import postgres_settings, redis_settings


@backoff.on_predicate(wait_gen=backoff.expo, max_time=120)
async def wait_for_redis() -> bool:
    return Redis(**redis_settings.model_dump()).ping()


@backoff.on_predicate(wait_gen=backoff.expo, max_time=120)
async def wait_for_postgres() -> bool:
    try:
        psycopg.connect(**postgres_settings.model_dump())
        return True
    except OperationalError:
        return False


if __name__ == '__main__':
    asyncio.run(wait_for_redis())
    asyncio.run(wait_for_postgres())
