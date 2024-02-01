from http import HTTPStatus

import pytest
from test_data.auth_service_data import TEST_DATA


@pytest.mark.asyncio
async def test_get_multiple_users(get_aiohttp_response):
    body, status, _ = await get_aiohttp_response('/api/v1/users/')

    assert status == HTTPStatus.OK
    for actual, expected in zip(body, TEST_DATA['user_table']):
        assert actual['email'] == expected['email']


@pytest.mark.parametrize(
    'test_id, expected_answer, http_status',
    [
        (TEST_DATA['user_table'][0]['id'], TEST_DATA['user_table'][0], HTTPStatus.OK),
        ('8330971b-88c7-4e7e-927f-a3776ee33b4d', {'detail': 'User not found'}, HTTPStatus.BAD_REQUEST),
    ],
)
@pytest.mark.asyncio
async def test_get_user(get_aiohttp_response, test_id, expected_answer, http_status):
    body, status, _ = await get_aiohttp_response(f'/api/v1/users/{test_id}')

    assert status == http_status
    assert body == expected_answer


@pytest.mark.parametrize(
    'test_email, expected_answer, http_status',
    [
        (TEST_DATA['user_table'][0]['email'], TEST_DATA['user_table'][0], HTTPStatus.OK),
        ('random.user@example.com', {'detail': 'User not found'}, HTTPStatus.BAD_REQUEST),
    ],
)
@pytest.mark.asyncio
async def test_get_user_by_email(get_aiohttp_response, test_email, expected_answer, http_status):
    body, status, _ = await get_aiohttp_response(f'/api/v1/users/email/{test_email}')

    assert status == http_status
    assert body == expected_answer


@pytest.mark.parametrize(
    'test_id, body, http_status',
    [
        (TEST_DATA['user_table'][2]['id'], {'name': 'John', 'surname': 'Vlissides'}, HTTPStatus.OK),
    ],
)
@pytest.mark.asyncio
async def test_update_user_positive_case(put_aiohttp_request, get_aiohttp_response, test_id, body, http_status):
    body, status, _ = await put_aiohttp_request(f'/api/v1/users/{test_id}', body=body)

    assert status == http_status

    test_user = dict(TEST_DATA['user_table'][2])
    test_user['name'] = 'John'
    test_user['surname'] = 'Vlissides'

    body, status, _ = await get_aiohttp_response(f'/api/v1/users/{test_id}')

    assert body == test_user


@pytest.mark.parametrize(
    'test_id, body, http_status',
    [
        ('8330971b-88c7-4e7e-927f-a3776ee33b4d', {'name': 'John', 'surname': 'Vlissides'}, HTTPStatus.BAD_REQUEST),
    ],
)
@pytest.mark.asyncio
async def test_update_user_negative_case(put_aiohttp_request, test_id, body, http_status):
    body, status, _ = await put_aiohttp_request(f'/api/v1/users/{test_id}', body=body)

    assert status == http_status
    assert body == {
        'detail': 'Update of user with id 8330971b-88c7-4e7e-927f-a3776ee33b4d is not possible. No user with such id.'
    }


@pytest.mark.parametrize(
    'test_id, expected_answer, http_status',
    [
        (
            TEST_DATA['user_table'][0]['id'],
            [
                {'action': 'login', 'finger_print': 'desktop_user_1', 'time': '2023-02-03T00:00:00'},
                {'action': 'logout', 'finger_print': 'desktop_user_1', 'time': '2023-03-03T00:00:00'},
                {'action': 'login', 'finger_print': 'mobile_user_1', 'time': '2023-04-03T00:00:00'},
            ],
            HTTPStatus.OK,
        ),
        (
            TEST_DATA['user_table'][1]['id'],
            [{'action': 'login', 'finger_print': 'desktop_user_2', 'time': '2023-05-03T00:00:00'}],
            HTTPStatus.OK,
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_user_history_positive_case(get_aiohttp_response, test_id, expected_answer, http_status):
    body, status, _ = await get_aiohttp_response(f'/api/v1/users/{test_id}/history', query_data={'page': 1, 'size': 4})

    assert http_status == status
    assert body['results'] == expected_answer


@pytest.mark.parametrize(
    'test_id, expected_answer, http_status',
    [('8330971b-88c7-4e7e-927f-a3776ee33b4d', {'detail': 'History not found'}, HTTPStatus.BAD_REQUEST)],
)
@pytest.mark.asyncio
async def test_get_user_history_negative_case(get_aiohttp_response, test_id, expected_answer, http_status):
    body, status, _ = await get_aiohttp_response(f'/api/v1/users/{test_id}/history', query_data={'page': 1, 'size': 4})

    assert http_status == status
    assert body == expected_answer
