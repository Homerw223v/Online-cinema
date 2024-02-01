from http import HTTPStatus

from db.base_bd import User
from exceptions.auth import roles_required
from exceptions.auth_request import AuthRequest
from fastapi import APIRouter, Depends, HTTPException
from models.models import UserHistoryModel, UserModel
from models.params.paginated import PaginatedParams, get_paginated_params
from models.roles import UserRole
from service.user_history_service import (
    UserHistoryService,
    get_user_history_service,
)
from service.user_service import UserService, get_user_service

router = APIRouter()


@router.get(
    '/',
    response_model=list[UserModel],
    description='Retrieve a subset of users with pagination.',
)
@roles_required(roles=[UserRole.admin])
async def get_multiple_users(
    request: AuthRequest,
    service: UserService = Depends(get_user_service),
) -> list[User]:
    """
    Retrieve a subset of users with pagination.

    :param service: Instance of UserService.
    :param request: Request object

    :return: A list of users with pagination.
    """
    users = await service.get_multiple_users()
    if not users:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Users not found'
        )
    return users


@router.get(
    '/{user_id}',
    response_model=UserModel,
    description='Retrieve a user by its ID',
)
@roles_required(roles=[UserRole.admin])
async def get_user(
    request: AuthRequest,
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> User:
    """
    Retrieve user by its id.

    :param request: Request object.
    :param user_id: The id of the user.
    :param service: An instance of UserService.

    :return: The user information.
    """
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='User not found'
        )
    return user


@router.get(
    '/email/{email}',
    response_model=UserModel,
    description='Retrieve a user by its email',
)
@roles_required(roles=[UserRole.admin])
async def get_user_by_email(
    request: AuthRequest,
    email: str,
    service: UserService = Depends(get_user_service),
) -> User:
    """
    Retrieve user by its email.

    :param request: Request object.
    :param email: The email of the user.
    :param service: An instance of UserService.

    :return: The user information.
    """
    user = await service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='User not found'
        )
    return user


@router.put(
    '/{user_id}',
    description='Update user with provided body.',
)
@roles_required(roles=[UserRole.admin])
async def update_user(
    request: AuthRequest,
    user_id: str,
    body: dict,
    service: UserService = Depends(get_user_service),
) -> None:
    """
    Update user information.

    :param user_id: The id of the user.
    :param body: The body with the data to be updated for the user.
    :param service: An instance of UserService.

    :return: HTTP status or HTTP Exception if something was wrong.
    """
    try:
        await service.update_user(user_id, body)
    except ValueError as err:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=str(err)
        )


@router.get(
    '/{user_id}/history',
    response_model=dict[str, int | list[UserHistoryModel]],
    description='Retrieve history of user login/logout in paginated format.',
)
@roles_required(roles=[UserRole.admin])
async def get_user_history(
    request: AuthRequest,
    user_id: str,
    params: PaginatedParams = Depends(get_paginated_params),
    service: UserHistoryService = Depends(get_user_history_service),
) -> dict[str, int | list[UserHistoryModel]]:
    """
    Retrieve user's login/logout history.

    :param request: The request object.
    :param user_id: The id of the user.
    :param params: Parameters of pagination (page and size).
    :param service: An instance of UserService.

    :return: A list of user's login/logout history with pagination.
    """
    try:
        history = await service.get_user_history(
            user_id, params.page, params.size
        )
    except ValueError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='History not found'
        )
    return history
