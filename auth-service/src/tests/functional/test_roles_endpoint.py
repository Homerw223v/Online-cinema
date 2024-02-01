from http import HTTPStatus

import pytest
from test_data.auth_service_data import TEST_DATA, post_roles


@pytest.mark.parametrize(
    'role_name, user_id, expected_answer, http_status',
    [
        ({"name": "Registered"}, TEST_DATA['user_table'][2]['id'], HTTPStatus.OK, HTTPStatus.OK),
        ({"name": "Registered"}, TEST_DATA['user_table'][0]['id'], HTTPStatus.OK, HTTPStatus.OK),
        ({"name": "Admin"}, TEST_DATA['user_table'][0]['id'], HTTPStatus.OK, HTTPStatus.OK),
        ({"name": "Abracadabra"}, TEST_DATA['user_table'][0]['id'], {'detail': "Role does not exist"},
         HTTPStatus.BAD_REQUEST),
    ],
)
@pytest.mark.asyncio
async def test_assign_role_to_user(post_aiohttp_response, role_name, user_id, expected_answer, http_status):
    body, status, _ = await post_aiohttp_response(f'/api/v1/roles/assign/{user_id}', role_name)

    assert status == http_status
    assert body == expected_answer


@pytest.mark.asyncio
async def test_get_multiple_roles(get_aiohttp_response):
    body, status, _ = await get_aiohttp_response('/api/v1/roles/')

    assert status == HTTPStatus.OK
    for actual, expected in zip(body, TEST_DATA['role']):
        assert actual['name'] == expected['name']


@pytest.mark.parametrize(
    'role_name, expected_answer, http_status',
    [
        (TEST_DATA['role'][0]['name'], TEST_DATA['role'][0], HTTPStatus.OK),
        (TEST_DATA['role'][2]['name'], TEST_DATA['role'][2], HTTPStatus.OK),
        ('Abracadabra', {'detail': "Role does not exist"}, HTTPStatus.BAD_REQUEST),
    ],
)
@pytest.mark.asyncio
async def test_get_role(get_aiohttp_response, role_name, expected_answer, http_status):
    body, status, _ = await get_aiohttp_response(f'/api/v1/roles/{role_name}')

    assert status == http_status
    assert body == expected_answer


@pytest.mark.parametrize(
    'user_id, expected_answer, status_code',
    [
        (TEST_DATA['user_table'][0]['id'], ['Registered', 'Admin'], HTTPStatus.OK),
        (TEST_DATA['user_table'][1]['id'], ['Subscribed', 'Moderator'], HTTPStatus.OK),
        (TEST_DATA['user_table'][2]['id'], ['Admin', 'Registered'], HTTPStatus.OK),
    ],
)
@pytest.mark.asyncio
async def test_users_role(get_aiohttp_response, user_id, expected_answer, status_code):
    body, status, _ = await get_aiohttp_response(f'/api/v1/roles/user_role/{user_id}')

    assert status == status_code
    assert body['roles'] == expected_answer


@pytest.mark.parametrize(
    'test_data, expected_answer, http_status',
    [
        (post_roles[0], None, HTTPStatus.OK),
        (post_roles[1], None, HTTPStatus.OK),
        (post_roles[0], {'detail': "Role already exist"}, HTTPStatus.CONFLICT),
    ],
)
@pytest.mark.asyncio
async def test_create_role(post_aiohttp_response, test_data, expected_answer, http_status):
    body, status, _ = await post_aiohttp_response(f'/api/v1/roles', test_data)

    assert status == http_status
    assert body == expected_answer


@pytest.mark.parametrize(
    'role_name, new_data, expected_answer, http_status',
    [
        (post_roles[0].get('name'), {"name": "Program"}, None, HTTPStatus.OK),
        (post_roles[1].get('name'), {"name": "Brother"}, None, HTTPStatus.OK),
    ],
)
@pytest.mark.asyncio
async def test_update_role(put_aiohttp_request, role_name, new_data, expected_answer, http_status):
    body, status, _ = await put_aiohttp_request(f'/api/v1/roles/{role_name}', body=new_data)

    assert status == http_status
    assert body == expected_answer


@pytest.mark.parametrize(
    'test_name, http_status, expected_answer',
    [
        ('Anonymous', HTTPStatus.OK, None),
        ('Subscribed', HTTPStatus.OK, None),
        ('Moderator', HTTPStatus.OK, None),
        ('Program', HTTPStatus.OK, None),
        ('Nothing', HTTPStatus.BAD_REQUEST, {'detail': 'Role does not exist'}),
    ],
)
@pytest.mark.asyncio
async def test_delete_role(delete_aiohttp_response, test_name, http_status, expected_answer):
    body, status, _ = await delete_aiohttp_response(f'/api/v1/roles/{test_name}')

    assert status == http_status
    assert body == expected_answer


@pytest.mark.parametrize(
    'role_name, user_id, expected_answer, http_status',
    [
        ({"name": "Registered"}, TEST_DATA['user_table'][2]['id'], HTTPStatus.OK, HTTPStatus.OK),
        ({"name": "Registered"}, TEST_DATA['user_table'][0]['id'], HTTPStatus.OK, HTTPStatus.OK),
        ({"name": "Admin"}, TEST_DATA['user_table'][0]['id'], HTTPStatus.OK, HTTPStatus.OK),
        ({"name": "Abracadabra"}, TEST_DATA['user_table'][0]['id'], {'detail': "User does not have such role."},
         HTTPStatus.BAD_REQUEST),
    ],
)
@pytest.mark.asyncio
async def test_delete_role_from_user(delete_aiohttp_response, role_name, user_id, expected_answer, http_status):
    body, status, _ = await delete_aiohttp_response(f'/api/v1/roles/assign/{user_id}', role_name)

    assert status == http_status
    assert body == expected_answer
