import asyncio
from asyncio.events import AbstractEventLoop
from typing import Iterator, Tuple, Callable

import aiohttp
import pytest_asyncio
from elasticsearch.helpers import async_bulk
from pytest_asyncio.plugin import SimpleFixtureFunction
from redis.asyncio import Redis

from elasticsearch import AsyncElasticsearch

from settings import base_test_settings, BaseTestSettings
from models import SessionResponse

pytest_plugins = [
    'src.test_genres_endpoint.fixtures',
    'src.test_movies_endpoint.conftest',
    'src.test_persons_endpoints.conftest',
]


@pytest_asyncio.fixture(scope='session')
def event_loop() -> Iterator[AbstractEventLoop]:
    """
    Yield event loop for testing purpose in session scope.
    Close before session termination.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name='es_client', scope='session')
async def es_client() -> Iterator[AsyncElasticsearch]:
    """
    Yield asynchronous ElasticSearch client in session scope.
    Close before session termination.
    """
    es_client = AsyncElasticsearch(hosts=base_test_settings.es_host, verify_certs=False)
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(name='aiohttp_session', scope='session')
async def aiohttp_session() -> Iterator[aiohttp.ClientSession]:
    """
    Yield aiohttp client session in testing session scope.
    Close before session termination.
    """
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(name='redis_client', scope='session')
async def redis_client() -> Iterator[Redis]:
    """
    Yield Redis client in testing session scope.
    Close before session termination.
    """
    redis = Redis(host=base_test_settings.redis_host, port=base_test_settings.redis_port)
    yield redis
    await redis.flushdb()
    await redis.aclose()


@pytest_asyncio.fixture(name='get_aiohttp_response')
async def get_aiohttp_response(aiohttp_session: SimpleFixtureFunction) -> Callable:
    """
    Return inner function.

    :param aiohttp_session: Fixture of this module, which yields aiohttp client session.
    """

    async def inner(postfix: str, query_data: dict[str: int | str] | None = None) -> Tuple[dict, int, dict]:
        """
        Return body, status, and headers of https request with postfix endpoint and query_data.

        :param postfix: Endpoint of API.
        :param query_data: Parameters of API request.
        """
        url = base_test_settings.service_url + postfix
        async with aiohttp_session.get(url, params=query_data) as response:
            body = await response.json()
            status = response.status
            headers = response.headers

            return body, status, headers

    return inner


@pytest_asyncio.fixture(scope='module')
async def es_write_data_for_module(es_client, redis_client):
    async def inner(bulk_query: list[dict], index_name: str, settings: BaseTestSettings):
        if await es_client.indices.exists(index=index_name):
            await es_client.indices.delete(index=index_name)
        await es_client.indices.create(
            index=index_name, settings=settings.get_settings(), mappings=settings.get_index_mapping(index_name)
        )

        updated, errors = await async_bulk(client=es_client, actions=bulk_query, refresh=True)
        if errors:
            raise Exception(errors)

    yield inner


@pytest_asyncio.fixture(scope='session')
async def create_session_request(aiohttp_session):
    """
    Make request via http client and return response
    """

    async def inner(url_path: str, params: dict | None, settings: BaseTestSettings) -> SessionResponse:
        url = settings.service_url + url_path
        async with aiohttp_session.get(url, params=params) as response:
            body = await response.json()
            return SessionResponse(
                headers=response.headers,
                status=response.status,
                body=body,
            )

    yield inner
