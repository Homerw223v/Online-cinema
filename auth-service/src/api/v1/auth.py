from typing import Annotated
from http import HTTPStatus
from core.config import settings
from exceptions import errors
from fastapi import APIRouter, Depends, HTTPException, Response, status, Header
from starlette.requests import Request
from starlette.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from schemas.auth import (
    DataForRefreshTokensSchema,
    TokensSchema,
    UserCreateSchema,
    UserInDBSchema,
    UserSignInSchema,
)
from service.social_auth.yandex_social_auth import (
    YandexSocialAuth,
    SocialFactory,
)
from service.auth_servise import AuthService, get_service
from schemas.social_auth import SocialOAuthUserModel

oath2_schema = OAuth2PasswordBearer(tokenUrl='/auth/signin')

router = APIRouter()


@router.get(
    '/auth/{provider}',
    response_class=status.HTTP_302_FOUND,
    description='Redirects the user to a third-party authentication service. Services allowed: Yandex.',
)
async def login_with_social(provider: str, request: Request):
    """
    Handle authentication redirect for a specific provider.

    Args:
        provider (str): The provider name.
        request (Request): The request object.
    Returns:
        RedirectResponse: The redirect response.
    """
    oauth_service = SocialFactory.get_social_service(provider)
    return await oauth_service.get_social_auth_url(request)


@router.get(
    '/login/{provider}',
    response_model=TokensSchema,
    description='Authorizes the user based on access and refresh tokens'
    ' received from the third-party authentication service',
)
async def social_login(
    request: Request,
    provider: str,
    auth_service: Annotated[AuthService, Depends(get_service)],
):
    """
    Authenticate a user using provider social login.

    Args:
        request (Request): The request object.
        provider (str): The provider name.
        auth_service (AuthService): The authentication service.

    Returns:
        JSONResponse: The authentication tokens as a JSON response.

    Raises:
        HTTPException: If the authentication fails or an error occurs.
    """
    oauth_service = SocialFactory.get_social_service(provider)
    social_user: SocialOAuthUserModel = await oauth_service.get_user_info(
        request
    )
    return await auth_service.authenticate_social_user(social_user, request)


@router.post(
    '/signup',
    response_model=UserInDBSchema,
    status_code=status.HTTP_201_CREATED,
)
async def signin(
    user_create: UserCreateSchema,
    auth_service: Annotated[AuthService, Depends(get_service)],
) -> UserInDBSchema | None:
    """Save user in db with provided credentials

    :param user_create: User creation schema
    :param auth_service: Authentication service

    :raises HTTPException: if user already exists or invalid credentials

    :return UserInDBSchema: User in db with provided data
    """
    try:
        user = await auth_service.register_user(user_create)
    except errors.UserExistsInDBException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f'{e}'
        )
    except errors.PasswordsDontMatchException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f'{e}'
        )

    return user


@router.post('/signin', response_model=TokensSchema)
async def signin(
    user_signin_data: UserSignInSchema,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_service)],
):
    """Authenticate user in db with provided credentials

    :param user_signin_data: User signin schema.
    :param response: Response to set cookie for user.
    :param auth_service: Authentication service.

    :raises HTTPException: if user doesn't exist or invalid password

    :return: Tokens for user (TokensSchema)

    """
    try:
        user_from_db = await auth_service.authenticate_user(
            user_signin_data.email, user_signin_data.password
        )
    except (errors.UserNotExistsInDBException, errors.PasswordNotVerified):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
        )

    token_schema = await auth_service.create_auth_session(
        user_from_db, user_signin_data.finger_print
    )

    response.set_cookie(
        key='refresh_token',
        value=str(token_schema.refresh_token),
        httponly=True,
        max_age=settings.refresh_token_expire_minutes * 60,
        path='/auth',
    )

    return token_schema


@router.post('/refresh', response_model=TokensSchema)
async def refresh(
    token_data: DataForRefreshTokensSchema,
    auth_service: Annotated[AuthService, Depends(get_service)],
):
    """Refresh the access token.
    :param token_data: Token data to refresh.
    :param auth_service: Authentication service

    :raises HTTPException: If refresh token is invalid, or if refresh token is expired,
    or if refresh token does not exist, or fingerprint is invalid.

    :return: Tokens for user

    """
    try:
        output_token = await auth_service.verify_refresh_token_get_new(
            token_data
        )
    except errors.RefreshTokenExpired:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Refresh token expired. Please sign in again.',
        )
    except errors.RefreshTokenNotExists:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not find the refresh token. Please sign in.',
        )
    except errors.FingerprintNotMatch:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could validate credentials. Please sign in.',
        )

    return output_token


@router.post('/logout')
async def logout(
    refresh_data: DataForRefreshTokensSchema,
    auth_service: Annotated[AuthService, Depends(get_service)],
    response: Response,
):
    """
    Logout the user.

    :param refresh_data: Refresh token.
    :param auth_service: Authentication service.
    :param response: To delete user cookie and refresh token
    :raises HTTPException: If the refresh token does not exist or refresh token is expired
    """
    try:
        await auth_service.logout_user(refresh_data)
    except errors.RefreshTokenNotExists:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid refresh token.',
        )
    except errors.RefreshTokenExpired:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Refresh token expired.',
        )

    # Delete browser cookie
    response.delete_cookie(key='refresh_token')
    return {'message': 'Logout successful'}
