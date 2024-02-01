import asyncio
from asyncio.events import AbstractEventLoop
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Iterator, Tuple

import aiohttp
import pytest_asyncio
from jose import jwt
from pytest_asyncio.plugin import SimpleFixtureFunction
from redis.asyncio import Redis
from settings import redis_settings, service_settings

pytest_plugins = ['test_data.fixture']


@pytest_asyncio.fixture(scope='session')
def event_loop() -> Iterator[AbstractEventLoop]:
    """
    Yield event loop for testing purpose in session scope.
    Close before session termination.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name='aiohttp_session', scope='session')
async def aiohttp_session() -> Iterator[aiohttp.ClientSession]:
    """
    Yield aiohttp client session in testing session scope.
    Close before session termination.
    """
    session = aiohttp.ClientSession(headers=get_authorization_header())
    yield session
    await session.close()


def get_authorization_header() -> dict[str, str]:
    """
    Return authorization header for test environment.
    """
    data = {
        'email': 'erich.gamma@example.com',
        'roles': ['admin'],
        'exp': timedelta(minutes=service_settings.access_token_expire_minutes) + datetime.now(timezone.utc),
    }

    encoded_jwt = jwt.encode(data, service_settings.jwt_secret_key, algorithm=service_settings.jwt_algorithm)
    return {'Authorization': f'Bearer {encoded_jwt}'}


@pytest_asyncio.fixture(name='redis_client', scope='session')
async def redis_client() -> Iterator[Redis]:
    """
    Yield Redis client in testing session scope.
    Close before session termination.
    """
    redis = Redis(host=redis_settings.host, port=redis_settings.port)
    yield redis
    await redis.flushdb()
    await redis.aclose()


@pytest_asyncio.fixture(name='get_aiohttp_response')
async def get_aiohttp_response(aiohttp_session: SimpleFixtureFunction) -> Callable:
    """
    Return inner function.

    :param aiohttp_session: Fixture of this module, which yields aiohttp client session.
    """

    async def inner(postfix: str, query_data: dict[str : int | str] | None = None) -> Tuple[dict, int, dict]:
        """
        Return body, status, and headers of https request with postfix endpoint and query_data.

        :param postfix: Endpoint of API.
        :param query_data: Parameters of API request.
        """
        url = service_settings.service_url + postfix
        async with aiohttp_session.get(url, params=query_data) as response:
            body = await response.json()
            status = response.status
            headers = response.headers

            return body, status, headers

    return inner


@pytest_asyncio.fixture(name='delete_aiohttp_response')
async def delete_aiohttp_response(aiohttp_session: SimpleFixtureFunction) -> Callable:
    """
    Return inner function.

    :param aiohttp_session: Fixture of this module, which yields aiohttp client session.
    """

    async def inner(postfix: str, data: dict = None) -> Tuple[dict, int, dict]:
        """
        Return body, status, and headers of https request with postfix endpoint and query_data.

        :param postfix: Endpoint of API.
        :param data: Data to send in request body.
        """
        url = service_settings.service_url + postfix
        async with aiohttp_session.delete(url, json=data) as response:
            body = await response.json()
            status = response.status
            headers = response.headers

            return body, status, headers

    return inner


@pytest_asyncio.fixture(name='post_aiohttp_response')
async def post_aiohttp_response(aiohttp_session: SimpleFixtureFunction) -> Callable:
    """
    Return inner function.

    :param aiohttp_session: Fixture of this module, which yields aiohttp client session.
    """

    async def inner(postfix: str, data: dict[str : int | str] | None = None) -> Tuple[dict, int, dict]:
        """
        Return body, status, and headers of https request with postfix endpoint and query_data.

        :param postfix: Endpoint of API.
        :param data: Parameters of API request.
        """
        url = service_settings.service_url + postfix
        async with aiohttp_session.post(url, json=data) as response:
            body = await response.json()
            status = response.status
            headers = response.headers

            return body, status, headers

    return inner


@pytest_asyncio.fixture(name='put_aiohttp_request')
async def put_aiohttp_request(aiohttp_session: SimpleFixtureFunction) -> Callable:
    """
    Return inner function.

    :param aiohttp_session: Fixture of this module, which yields aiohttp client session.
    """

    async def inner(
        postfix: str, query_data: dict[str : int | str] | None = None, body: dict[str:Any] | None = None
    ) -> Tuple[dict, int, dict]:
        """
        Return body, status, and headers of https request with postfix endpoint and query_data.

        :param postfix: Endpoint of API.
        :param query_data: Parameters of API request.
        :param body: Body of the put request.
        """
        url = service_settings.service_url + postfix
        async with aiohttp_session.put(url, params=query_data, json=body) as response:
            body = await response.json()
            status = response.status
            headers = response.headers

            return body, status, headers

    return inner
