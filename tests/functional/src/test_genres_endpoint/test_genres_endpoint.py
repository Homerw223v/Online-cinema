from http import HTTPStatus

import pytest
from test_data.genres_data import TESTING_UUID, genres_endpoint, genres_name


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        ({'page': 1, 'size': 10}, genres_name[:10]),
        ({'page': 1, 'size': 10, 'sort': '-name', 'filt': 'A'}, genres_name[0:3][::-1]),
        ({'page': 2, 'size': 10}, genres_name[10:20]),
        ({'page': 1, 'size': 40}, genres_name),
    ]
)
@pytest.mark.asyncio
async def test_genres_positive_responses(get_aiohttp_response, query_data, expected_answer):
    """
    Test positive case of API calls to '/api/v1/genres' endpoint with parameters query_data.
    """
    body, status, _ = await get_aiohttp_response(genres_endpoint, query_data)

    assert status == HTTPStatus.OK
    assert [genre['name'] for genre in body['results']] == expected_answer


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        ({'page': -1, 'size': 10}, 'Page number should be positive, -1 instead.'),
        ({'page': 1, 'size': 0}, 'Size of the page should be positive, 0 instead.'),
        ({'page': 5, 'size': 10}, 'Page number exceeds maximum possible page, which is 3.'),
    ]
)
@pytest.mark.asyncio
async def test_genres_negative_responses(get_aiohttp_response, query_data, expected_answer):
    """
    Test negative case of API calls to '/api/v1/genres' endpoint with parameters query_data.
    """
    body, status, _ = await get_aiohttp_response(genres_endpoint, query_data)

    assert status == HTTPStatus.BAD_REQUEST
    assert body['detail'] == expected_answer


@pytest.mark.asyncio
async def test_cache_list_of_genres(get_genres_from_cache):
    """
    Test extraction of list of genres from the cache.
    """
    genres = await get_genres_from_cache("index=genres_query=None_page=1_size=10_sort=None")

    assert genres == genres_name[:10]


@pytest.mark.parametrize(
    'testing_uuid, expected_answer',
    [
        (TESTING_UUID, {'status': HTTPStatus.OK, 'body': {'id': TESTING_UUID, 'name': 'Action'}}),
        (TESTING_UUID[1:], {'status': HTTPStatus.NOT_FOUND, 'body': {'detail': 'genre not found'}}),
    ]
)
@pytest.mark.asyncio
async def test_single_genre_endpoint(get_aiohttp_response, testing_uuid, expected_answer):
    """
    Test positive and negative responses from /api/v1/genres/<UUID> endpoint.
    """
    body, status, _ = await get_aiohttp_response(genres_endpoint + testing_uuid)

    assert status == expected_answer['status']
    assert body == expected_answer['body']


@pytest.mark.asyncio
async def test_cache_single_genre(get_genre_from_cache, redis_client):
    """
    Test extraction of single genre from the cache.
    """
    genre = await get_genre_from_cache(TESTING_UUID)

    assert genre == {'id': TESTING_UUID, 'name': 'Action'}
