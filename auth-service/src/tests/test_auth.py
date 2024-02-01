import uuid
from datetime import datetime, timezone, timedelta
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from passlib.context import CryptContext
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from db.redis import RedisCache
from db.refresh_session import RefreshSessionMethods
from db.user_db import UserMethods
from main import app
from db.base_bd import BaseDB, User, RefreshSession
from db.connection import engine, async_session
from schemas.auth import UserCreateSchema, UserSignInSchema
from exceptions import errors
from service.auth_servise import AuthService


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_create(event_loop):
    async with engine.begin() as conn:
        await conn.run_sync(BaseDB.metadata.drop_all)
        await conn.run_sync(BaseDB.metadata.create_all)


@pytest_asyncio.fixture(scope="session")
async def db_session(event_loop) -> AsyncSession:
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def client(db_create):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
        
        
@pytest_asyncio.fixture(scope="session")
async def auth_service(db_create, db_session):
    cache = RedisCache(Redis())
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    refr_session = RefreshSessionMethods(db_session)
    user_db = UserMethods(db_session)
    yield AuthService(pwd_context, cache, user_db, refr_session)
    




@pytest.mark.asyncio
@pytest.mark.parametrize(
    'data, status_code',
    [
        ({
             "email": "test@example.com",
             "password": "test",
             "password_confirm": "test",
             "name": "First",
             "surname": "string"
         }, 201),
        ({
             "email": "test@example.com",
             "password": "test",
             "password_confirm": "test",
             "name": "First",
             "surname": "string"
         }, 409),
        ({
             "email": "testexample.com",
             "password": "test",
             "password_confirm": "test",
             "name": "First",
             "surname": "string"
         }, 422),
        ({
             "email": "test@example.com",
             "password": "test",
             "password_confirm": "test1",
             "name": "First",
             "surname": "string"
         }, 409),
    
    ],
)
async def test_signup(client, data, status_code):
    response = await client.post("/api/v1/auth/signup", json=data)
    assert response.status_code == status_code


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'data, status_code, detail',
    [
        ({
             "email": "test1@example.com",
             "password": "test",
             "finger_print": "test_finger_print"
         }, 401, 'Invalid username or password'),
        ({
             "email": "test@example.com",
             "password": "test11",
             "finger_print": "test_finger_print"
         }, 401, 'Invalid username or password'),
    ]
)
async def test_signin_fail(client, data, status_code, detail):
    response = await client.post("/api/v1/auth/signin", json=data)
    assert response.status_code == status_code
    assert response.json() == {'detail': detail}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'data, status_code, expect_response',
    [
        ({"email": "test@example.com", "password": "test", "finger_print": "test_finger_print"},
         200,
         {"token_type": "bearer", "email": "test@example.com"}),
    ]
)
async def test_signin_success(client, data, status_code, expect_response):
    response = await client.post("/api/v1/auth/signin", json=data)
    assert response.status_code == status_code
    ac_response = response.json()
    assert ac_response['email'] == expect_response['email']
    assert ac_response['token_type'] == expect_response['token_type']


@pytest.mark.asyncio
async def test_refresh_session_success(client, db_session, auth_service):
    # get refresh token
    signin_data = {"email": "test@example.com", "password": "test", "finger_print": "test_finger_print"}
    signin_response = await client.post('/api/v1/auth/signin', json=signin_data)
    assert signin_response.status_code == 200
    signin_response_dict = signin_response.json()

    refresh_token = signin_response_dict['refresh_token']
    finger_print = signin_data['finger_print']
    refresh_data = {"refresh_token": refresh_token, "finger_print": finger_print}

    refresh_response = await client.post('/api/v1/auth/refresh', json=refresh_data)
    assert refresh_response.status_code == 200

    auth_session = await auth_service.refr_session.get_by_finger_print(signin_data['email'], signin_data['finger_print'])
    assert auth_session is not None
    assert refresh_response.json()['refresh_token'] == str(auth_session.refresh_token)


@pytest.mark.asyncio
async def test_refresh_session_fail_finger_print_wrong(client, db_session):
    signin_data = {"email": "test@example.com", "password": "test", "finger_print": "test_finger_print"}
    signin_response = await client.post('/api/v1/auth/signin', json=signin_data)
    assert signin_response.status_code == 200
    signin_response_dict = signin_response.json()

    refresh_token = signin_response_dict['refresh_token']

    refresh_data = {"refresh_token": refresh_token, "finger_print": 'other_finger_print'}
    refresh_response = await client.post('/api/v1/auth/refresh', json=refresh_data)
    assert refresh_response.status_code == 401
    assert refresh_response.json() == {'detail': 'Could validate credentials. Please sign in.'}


@pytest.mark.asyncio
async def test_refresh_session_fail_refresh_token_wrong(client, db_session):
    signin_data = {"email": "test@example.com", "password": "test", "finger_print": "test_finger_print"}
    signin_response = await client.post('/api/v1/auth/signin', json=signin_data)
    assert signin_response.status_code == 200

    refresh_data = {"refresh_token": str(uuid.uuid4()), "finger_print": signin_data['finger_print']}
    refresh_response = await client.post('/api/v1/auth/refresh', json=refresh_data)
    assert refresh_response.status_code == 401
    assert refresh_response.json() == {'detail': 'Could not find the refresh token. Please sign in.'}


@pytest.mark.asyncio
async def test_refresh_session_fail_refresh_token_expired(client, db_session, auth_service):
    signin_data = {"email": "test@example.com", "password": "test", "finger_print": "test_finger_print"}
    signin_response = await client.post('/api/v1/auth/signin', json=signin_data)
    assert signin_response.status_code == 200

    auth_session = await auth_service.refr_session.get_by_finger_print(signin_data['email'], signin_data['finger_print'])
    auth_session.expires_at = datetime.now(timezone.utc) - timedelta(hours=10)
    await db_session.commit()

    refresh_data = {"refresh_token": signin_response.json()['refresh_token'],
                    "finger_print": signin_data['finger_print']}
    refresh_response = await client.post('/api/v1/auth/refresh', json=refresh_data)
    assert refresh_response.status_code == 401
    assert refresh_response.json() == {'detail': 'Refresh token expired. Please sign in again.'}


@pytest.mark.asyncio
async def test_logout(client, db_session):
    signin_data = {"email": "test@example.com", "password": "test", "finger_print": "test_finger_print"}
    signin_response = await client.post('/api/v1/auth/signin', json=signin_data)
    assert signin_response.status_code == 200

    signin_response_dict = signin_response.json()
    logout_data = {'refresh_token': signin_response_dict['refresh_token'], 'finger_print': signin_data['finger_print']}

    logout_response = await client.post('/api/v1/auth/logout', json=logout_data)
    assert logout_response.status_code == 200
    assert logout_response.json() == {'message': 'Logout successful'}


@pytest.mark.asyncio
async def test_register_user_raises_user_exists_exc(db_session, auth_service):
    user_data = {'email': 'test@example.com', 'password': '12345', 'password_confirm': '12345'}
    user = UserCreateSchema(**user_data)
    with pytest.raises(errors.UserExistsInDBException):
        await auth_service.register_user(user)


@pytest.mark.asyncio
async def test_register_user_raises_passwords_not_match_exp(db_session, auth_service):
    user_data = {'email': 'test2@example.com', 'password': '12345', 'password_confirm': '12'}
    user = UserCreateSchema(**user_data)
    with pytest.raises(errors.PasswordsDontMatchException):
        await auth_service.register_user(user)


@pytest.mark.asyncio
async def test_user_saved_in_db(db_session, auth_service):
    user_data = {'email': 'test3@example.com', 'password': '12345', 'password_confirm': '12345'}
    user = UserCreateSchema(**user_data)
    saved_user = await auth_service.register_user(user)
    same_user = await auth_service.user_db.get_by_email(user.email)
    assert saved_user is same_user


@pytest.mark.asyncio
async def test_authenticate_user_raises_user_not_exc(db_session, auth_service):
    user_data = {'email': 'chushpan@example.com', 'password': '12345'}
    with pytest.raises(errors.UserNotExistsInDBException):
        await auth_service.authenticate_user(user_data['email'], user_data['password'])


@pytest.mark.asyncio
async def test_authenticate_user_raises_password_wrong_exc(db_session, auth_service):
    user_data = {'email': 'test@example.com', 'password': 'lalalala'}
    with pytest.raises(errors.PasswordNotVerified):
        await auth_service.authenticate_user(user_data['email'], user_data['password'])


@pytest.mark.asyncio
async def test_authenticate_user_success_return_user(db_session, auth_service):
    user_data = {'email': 'test@example.com', 'password': 'test'}
    auth_user = await auth_service.authenticate_user(user_data['email'], user_data['password'])
    same_user = await auth_service.user_db.get_by_email(user_data['email'])
    assert auth_user is same_user


@pytest.mark.asyncio
async def test_authenticate_user_auth_session_exists_and_updated(db_session, auth_service):
    user_data = {'email': 'test@example.com', 'password': 'test', 'finger_print': 'test_finger_print'}
    user_login_data = UserSignInSchema(**user_data)
    user = await auth_service.user_db.get_by_email(user_login_data.email)
    assert user is not None

    user_auth_session = await auth_service.refr_session.get_by_finger_print(user_data['email'],
                                                                 user_data['finger_print'])
    assert user_auth_session is not None

    old_refresh_token = user_auth_session.refresh_token
    old_expires_at = user_auth_session.expires_at

    await auth_service.create_auth_session(user, user_login_data)
    assert user_auth_session.refresh_token != old_refresh_token
    assert user_auth_session.expires_at != old_expires_at
