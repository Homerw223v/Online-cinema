import json
from http import HTTPStatus

import pytest
from settings import settings
from test_data.movies_data import movies_data, movies_endpoint


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'query': 'Unexpected Man', 'page': 1},
                {
                    'status': HTTPStatus.OK,
                    'total': 2,
                    'page': 1,
                    'result': [
                        {'id': movie['id'], 'title': movie['title'], 'imdb_rating': movie['imdb_rating']}
                        for movie in movies_data[101:]
                    ],
                },
        ),
        (
                {'query': 'Movie Number', 'page': 1},
                {
                    'status': HTTPStatus.OK,
                    'total': 100,
                    'page': 1,
                    'result': [
                        {'id': movie['id'], 'title': movie['title'], 'imdb_rating': movie['imdb_rating']}
                        for movie in movies_data[:10]
                    ],
                },
        ),
        (
                {'query': 'Movie Number', 'page': 5},
                {
                    'status': HTTPStatus.OK,
                    'total': 100,
                    'page': 5,
                    'result': [
                        {'id': movie['id'], 'title': movie['title'], 'imdb_rating': movie['imdb_rating']}
                        for movie in movies_data[40:50]
                    ],
                },
        ),
    ],
)
@pytest.mark.asyncio()
async def test_search_movie_by_keyword(get_aiohttp_response, query_data, expected_answer):
    """
    Test searching films by keyword on api/v1/films/search endpoint.
    """
    body, status, _ = await get_aiohttp_response(f'{movies_endpoint}/search', query_data)

    assert status == expected_answer['status']
    assert body['page'] == expected_answer['page']
    assert body['total'] == expected_answer['total']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'page': 1, 'size': 10},
                {
                    'status': HTTPStatus.OK,
                    'total_pages': 11,
                    'size': 10,
                    'movies': [
                        {'id': movie['id'], 'title': movie['title'], 'imdb_rating': movie['imdb_rating']}
                        for movie in movies_data[:10]
                    ],
                },
        ),
        (
                {'page': 2, 'size': 10},
                {
                    'status': HTTPStatus.OK,
                    'total_pages': 11,
                    'size': 10,
                    'movies': [
                        {'id': movie['id'], 'title': movie['title'], 'imdb_rating': movie['imdb_rating']}
                        for movie in movies_data[10:20]
                    ],
                },
        ),
        (
                {'page': 2, 'size': 25},
                {
                    'status': HTTPStatus.OK,
                    'total_pages': 5,
                    'size': 25,
                    'movies': [
                        {'id': movie['id'], 'title': movie['title'], 'imdb_rating': movie['imdb_rating']}
                        for movie in movies_data[25:50]
                    ],
                },
        ),
        (
                {'page': 10, 'size': 10},
                {
                    'status': HTTPStatus.OK,
                    'total_pages': 11,
                    'size': 10,
                    'movies': [
                        {'id': movie['id'], 'title': movie['title'], 'imdb_rating': movie['imdb_rating']}
                        for movie in movies_data[90:100]
                    ],
                },
        ),
    ],
)
@pytest.mark.asyncio()
async def test_movies_positive_responses(get_aiohttp_response, query_data, expected_answer):
    """
    Test positive case of API calls to '/api/v1/films' endpoint.
    """
    body, status, _ = await get_aiohttp_response(f'{movies_endpoint}', query_data)

    assert status == expected_answer['status']
    assert body['total'] == 102
    assert body['size'] == expected_answer['size']
    assert body['total_pages'] == expected_answer['total_pages']
    assert body['results'] == expected_answer['movies']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        ({'page': -1, 'size': 10},
         {'status': HTTPStatus.BAD_REQUEST, 'body': 'Page number should be positive, -1 instead.'}),
        ({'page': 1, 'size': 0},
         {'status': HTTPStatus.BAD_REQUEST, 'body': 'Size of the page should be positive, 0 instead.'}),
        ({'page': 15, 'size': 10},
         {'status': HTTPStatus.BAD_REQUEST, 'body': 'Page number exceeds maximum possible page, which is 11.'}),
    ],
)
@pytest.mark.asyncio()
async def test_movies_negative_responses(get_aiohttp_response, query_data, expected_answer):
    """
    Test negative case of API calls to '/api/v1/films' endpoint with parameters query_data.
    """
    body, status, _ = await get_aiohttp_response(f'{movies_endpoint}', query_data)

    assert status == expected_answer['status']
    assert body['detail'] == expected_answer['body']


@pytest.mark.parametrize(
    'testing_uuid, expected_answer',
    [
        (
                movies_data[100].get('id'),
                {
                    'status': HTTPStatus.OK,
                    'body': movies_data[100],
                },
        ),
        (
                movies_data[101].get('id'),
                {
                    'status': HTTPStatus.OK,
                    'body': movies_data[101],
                },
        ),
        (
                '3b46f521-c1ee-4c33-9f73-2ee29808fgra',
                {'status': HTTPStatus.NOT_FOUND, 'body': {'detail': 'film not found'}}),
    ],
)
@pytest.mark.asyncio()
async def test_single_movie_endpoint(get_aiohttp_response, testing_uuid, expected_answer):
    """
    Test positive and negative responses from /api/v1/films/<UUID> endpoint.
    """
    body, status, _ = await get_aiohttp_response(f'{movies_endpoint}/{testing_uuid}')

    assert status == expected_answer['status']
    assert body == expected_answer['body']


@pytest.mark.parametrize(
    'redis_key, expected_answer',
    [
        # Testing api/v1/films endpoint cache.
        ('index=movies_query=None_page=1_size=10_sort=None', movies_data[:10]),
        ('index=movies_query=None_page=10_size=10_sort=None', movies_data[90:100]),
        ('index=movies_query=None_page=2_size=25_sort=None', movies_data[25:50]),
        # Testing api/v1/films/search endpoint cache.
        ('index=movies_query=Unexpected Man_page=1_size=10_sort=None', movies_data[100:]),
        ('index=movies_query=Movie Number_page=1_size=10_sort=None', movies_data[:10]),
    ],
)
@pytest.mark.asyncio()
async def test_cache_list_of_movies(get_movies_from_cache, redis_key, expected_answer):
    """
    Test extraction of list of films from the cache.
    """
    movies = await get_movies_from_cache(redis_key)

    assert movies == expected_answer


@pytest.mark.asyncio()
async def test_film_get_from_cache(create_session_request, redis_client):
    movie_id = movies_data[101].get('id')
    resource = await create_session_request(f'{movies_endpoint}/{movie_id}', params=None, settings=settings)
    assert resource.status == HTTPStatus.OK
    cached = await redis_client.get(movie_id)
    cached_person = json.loads(cached)
    assert cached_person['id'] == movie_id
    assert cached_person['title'] == movies_data[101].get('title')
