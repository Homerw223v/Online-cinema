import json
from http import HTTPStatus

import pytest
from settings import settings
from test_data.movies_data import FilmsData
from test_data.persons_data import PersonsData, person_1, persons_endpoint


@pytest.mark.parametrize(
    'person, expected',
    [
        (
                {'id': person_1['id']},
                {
                    'status': HTTPStatus.OK,
                    'full_name': person_1['full_name'],
                },
        ),
        ({'id': 'ab840476-c926-48d3-aa7c-0bd0a02eec1c'},
         {'status': HTTPStatus.NOT_FOUND, 'detail': 'Person not found'}),
    ],
)
@pytest.mark.asyncio
async def test_person_get_by_id_found(es_write_data, create_session_request, person, expected):
    await es_write_data(PersonsData.one_person(), 'persons', settings)
    response = await create_session_request(f'{persons_endpoint}/{person["id"]}', params=None, settings=settings)
    assert response.status == expected['status']
    if response.status == HTTPStatus.OK:
        assert response.body['id'] == person['id']
        assert response.body['full_name'] == expected.get('full_name')
    else:
        assert response.body['detail'] == expected['detail']


@pytest.mark.asyncio
async def test_get_person_films(es_write_data, create_session_request):
    await es_write_data(FilmsData.films(), 'movies', settings)
    await es_write_data(PersonsData.one_person(), 'persons', settings)
    person_id = person_1['id']
    response = await create_session_request(f'/api/v1/persons/{person_id}/films', params=None, settings=settings)
    assert response.status == HTTPStatus.OK
    films = response.body.get('results')
    assert FilmsData.raw_films[0]['id'] in [film['id'] for film in films]


@pytest.mark.asyncio
async def test_get_person_films_from_cache(es_write_data, create_session_request, redis_client):
    await es_write_data(FilmsData.films(), 'movies', settings)
    await es_write_data(PersonsData.one_person(), 'persons', settings)
    person_id = person_1['id']
    response = await create_session_request(f'/api/v1/persons/{person_id}/films', params=None, settings=settings)
    assert response.status == HTTPStatus.OK
    key = f'index=movies_query=None_page=1_size=10_sort=None_person_id={person_id}'
    cached = await redis_client.get(key)
    cached_result = json.loads(cached)
    assert FilmsData.raw_films[0]['id'] in [record['_source']['id'] for record in cached_result['hits']['hits']]


@pytest.mark.asyncio
async def test_person_get_from_cache(es_write_data, create_session_request, redis_client):
    await es_write_data(PersonsData.one_person(), 'persons', settings)
    person_id = person_1['id']
    resource = await create_session_request(f'/api/v1/persons/{person_id}', params=None, settings=settings)
    assert resource.status == HTTPStatus.OK
    cached = await redis_client.get(person_id)
    cached_person = json.loads(cached)
    assert cached_person['id'] == person_id
    assert cached_person['full_name'] == person_1['full_name']
