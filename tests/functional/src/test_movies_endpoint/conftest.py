import json
from typing import Any, Callable, Iterator

import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from redis.asyncio import Redis
from settings import movies_test_settings
from test_data.movies_data import movies_data


@pytest_asyncio.fixture(name='es_write_movies_data', scope='session', autouse=True)
async def es_write_movies_data(es_client: AsyncElasticsearch) -> Iterator[None]:
    """
    Write movies index data to Elasticsearch via es_client.

    :param es_client: Asynchronous Elasticsearch client.
    """
    bulk_query = prepare_movies_data()
    await create_es_movies_index(es_client)
    updated, errors = await async_bulk(client=es_client, actions=bulk_query, refresh=True)

    if errors:
        raise Exception('Ошибка записи данных в Elasticsearch')

    yield None
    await es_client.indices.delete(index=movies_test_settings.es_index_name)


def prepare_movies_data() -> list[dict[str, Any]]:
    """
    Return movies index data for uploading to Elasticsearch index.
    """
    bulk_query: list[dict] = []
    for row in movies_data:
        data = {'_index': movies_test_settings.es_index_name, '_id': row['id'], '_source': row}
        bulk_query.append(data)

    return bulk_query


async def create_es_movies_index(es_client: AsyncElasticsearch) -> None:
    """
    Create index movies in Elasticsearch.

    :param es_client: Asynchronous Elasticsearch client.
    """
    if await es_client.indices.exists(index=movies_test_settings.es_index_name):
        await es_client.indices.delete(index=movies_test_settings.es_index_name)

    await es_client.indices.create(
        index=movies_test_settings.es_index_name,
        mappings=movies_test_settings.es_index_mapping,
        settings=movies_test_settings.es_index_settings,
    )


@pytest_asyncio.fixture(name='get_movies_from_cache')
async def get_movies_from_cache(redis_client: Redis) -> Callable:
    """
    Return inner function.

    :param redis_client: Fixture of this module, which yields redis client.
    """

    async def inner(key: str) -> list[str]:
        """
        Return list of movies names from cache by key.

        :param key: Redis key of cached data.
        """
        movies = await get_data_from_redis(redis_client, key)
        return [movie['_source'] for movie in movies['hits']['hits']]

    return inner


async def get_data_from_redis(redis_client: Redis, key: str) -> dict[str, Any]:
    """
    Return data from redis by key.

    :param key: Redis key of cached data.
    :param redis_client: Fixture of this module, which yields redis client.
    """
    response_raw = await redis_client.get(key)
    response = json.loads(response_raw)

    return response
