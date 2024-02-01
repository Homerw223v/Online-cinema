from http import HTTPStatus

import pytest
from settings import settings
from test_data.movies_data import FilmsData, films
from test_data.persons_data import PersonsData, persons_endpoint


@pytest.mark.parametrize(
    'query, expected', [
        (
                {'query': 'Man'},
                {'status': HTTPStatus.OK, 'id': films[0].get('id'), 'length': 3, 'page': 1, 'size': 3,
                 'total_pages': 1}
        ),
        (
                {'query': 'Man', 'page': 1, 'size': 1},
                {'status': HTTPStatus.OK, 'id': films[0].get('id'), 'length': 1, 'page': 1, 'size': 1,
                 'total_pages': 3}
        ),
        (
                {'query': 'Man', 'page': 2, 'size': 1},
                {'status': HTTPStatus.OK, 'id': films[1].get('id'), 'length': 1, 'page': 2, 'size': 1,
                 'total_pages': 3}
        ),

        (
                {'query': 'Unexpected'},
                {'status': HTTPStatus.OK, 'id': films[0].get('id'), 'length': 2, 'page': 1, 'size': 2,
                 'total_pages': 1}
        ),
        (
                {'query': 'men'},
                {'status': HTTPStatus.OK, 'id': films[2].get('id'), 'length': 3, 'page': 1, 'size': 3,
                 'total_pages': 1}
        ),
        (
                {'query': 'Spam'},
                {'status': HTTPStatus.BAD_REQUEST}
        )
    ]
)
@pytest.mark.asyncio
async def test_search_films(es_write_data_for_module, create_session_request, query, expected):
    # prepare films
    films_query = FilmsData.films()
    await es_write_data_for_module(films_query, 'movies', settings)
    response = await create_session_request('/api/v1/films/search', params=query, settings=settings)
    assert response.status == expected['status']
    if response.status == HTTPStatus.OK:
        assert len(response.body['results']) == expected['length']
        assert response.body['results'][0]['id'] == expected['id']
        assert response.body['page'] == expected['page']
        assert response.body['size'] == expected['size']
        assert response.body['total_pages'] == expected['total_pages']


@pytest.mark.asyncio
async def test_persons(es_client, aiohttp_session, es_write_data_for_module, create_session_request):
    await es_write_data_for_module(PersonsData.one_person(), 'persons', settings)

    query_params = {'query': 'user'}
    response = await create_session_request(f'{persons_endpoint}/search', query_params, settings)

    assert response.status == HTTPStatus.OK
    assert len(response.body['results']) == 1


@pytest.mark.parametrize(
    'query_data, expected',
    [
        (
                {'query': 'Alex'},
                {'status': HTTPStatus.OK, 'persons': 10, 'total': 20}
        ),
        (
                {'query': 'Polina'},
                {'status': HTTPStatus.OK, 'persons': 10, 'total': 10}
        ),
        (
                {'query': 'Alex', 'size': 5, 'page': 2},
                {'status': HTTPStatus.OK, 'persons': 5, 'total': 20}
        ),
        (
                {'query': 'Polina', 'size': 2, 'page': 3},
                {'status': HTTPStatus.OK, 'persons': 2, 'total': 10}
        ),

    ]
)
@pytest.mark.asyncio
async def test_persons_search(es_write_data_for_module, create_session_request, query_data, expected):
    await es_write_data_for_module(PersonsData.persons_40_alex_10_poline(), 'persons', settings)

    response = await create_session_request(f'{persons_endpoint}/search', query_data, settings=settings)

    assert response.status == expected['status']
    assert len(response.body['results']) == expected['persons']
    assert response.body['total'] == expected['total']


@pytest.mark.parametrize(
    'query_data, expected',
    [
        ({'query': 'Zara'},
         {'status': HTTPStatus.BAD_REQUEST,
                             'body': 'Page number exceeds maximum possible page, which is 0.'}),
        (
            {'query': 'Alex', 'size': 20, 'page': 100},
            {'status': HTTPStatus.BAD_REQUEST,
             'body': 'Page number exceeds maximum possible page, which is 1.'},
        ),
    ],
)
@pytest.mark.asyncio
async def test_persons_search_negative_results(
    aiohttp_session, es_write_data_for_module, create_session_request, query_data, expected
):
    await es_write_data_for_module(PersonsData.persons_40_alex_10_poline(), 'persons', settings)

    response = await create_session_request(f'{persons_endpoint}/search', query_data, settings)

    assert response.status == expected['status']
    assert response.body['detail'] == expected['body']
