import json
from typing import Iterator, Callable, Any

import pytest_asyncio
from redis.asyncio import Redis

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from settings import genres_test_settings
from test_data.genres_data import es_genres_data


@pytest_asyncio.fixture(name='es_write_genres_data', scope='session', autouse=True)
async def es_write_genres_data(es_client: AsyncElasticsearch) -> Iterator[None]:
    """
    Write genres index data to Elasticsearch via es_client.

    :param es_client: Asynchronous Elasticsearch client.
    """
    bulk_query = prepare_genres_data()
    await create_es_genres_index(es_client)
    updated, errors = await async_bulk(client=es_client, actions=bulk_query, refresh=True)

    if errors:
        raise Exception('Ошибка записи данных в Elasticsearch')

    yield None
    await es_client.indices.delete(index=genres_test_settings.es_index_name)


def prepare_genres_data() -> dict[str:Any]:
    """
    Return genres index data for uploading to Elasticsearch index.
    """
    bulk_query: list[dict] = []
    for row in es_genres_data:
        data = {'_index': genres_test_settings.es_index_name, '_id': row['id']}
        data.update({'_source': row})
        bulk_query.append(data)

    return bulk_query


async def create_es_genres_index(es_client: AsyncElasticsearch) -> None:
    """
    Create index genres in Elasticsearch.

    :param es_client: Asynchronous Elasticsearch client.
    """
    if await es_client.indices.exists(index=genres_test_settings.es_index_name):
        await es_client.indices.delete(index=genres_test_settings.es_index_name)

    await es_client.indices.create(
        index=genres_test_settings.es_index_name,
        mappings=genres_test_settings.es_index_mapping,
        settings=genres_test_settings.es_index_settings,
    )


@pytest_asyncio.fixture(name='get_genres_from_cache')
async def get_genres_from_cache(redis_client: Redis) -> Callable:
    """
    Return inner function.

    :param redis_client: Fixture of this module, which yields redis client.
    """

    async def inner(key: str) -> list[str]:
        """
        Return list of genres names from cache by key.

        :param key: Redis key of cached data.
        """
        genres = await get_data_from_redis(redis_client, key)
        return [genre['_source']['name'] for genre in genres['hits']['hits']]

    yield inner


@pytest_asyncio.fixture(name='get_genre_from_cache')
async def get_genre_from_cache(redis_client: Redis) -> Callable:
    """
    Return inner function.

    :param redis_client: Fixture of this module, which yields redis client.
    """

    async def inner(key: str) -> dict[str:Any]:
        """
        Return genre from cache by key.

        :param key: Redis key of cached data.
        """
        return await get_data_from_redis(redis_client, key)

    return inner


async def get_data_from_redis(redis_client: Redis, key: str) -> dict[str:Any]:
    """
    Return data from redis by key.

    :param key: Redis key of cached data.
    :param redis_client: Fixture of this module, which yields redis client.
    """
    response_raw = await redis_client.get(key)
    response = json.loads(response_raw)

    return response
