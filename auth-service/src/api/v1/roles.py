from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from exceptions.auth import roles_required
from exceptions.auth_request import AuthRequest
from models.roles import UserRole
from schemas.roles import Role, RoleList
from schemas.user import UserRoles
from service.role_service import RoleService, get_role_service

router = APIRouter()


@router.get(
    '',
    response_model=list[RoleList],
    description='Returns all available roles. If there are no roles, it will return None.',
)
async def roles(role_service: RoleService = Depends(get_role_service)):
    """Retrieve all existing roles.
    Args:
        role_service (RoleService): An instance of RoleService.

    Returns:
        list[RoleList]: A list of all roles
    Raises:
        HTTPException: If no roles in database
    """
    return await role_service.all_roles()


@router.get(
    '/{role_name}',
    response_model=Role,
    description='Return information about single role',
)
async def role_information(
    role_name: str, role_service: RoleService = Depends(get_role_service)
):
    """Retrieve information about given role.
    Args:
        role_name (str): Name of the role
        role_service (RoleService): An instance of RoleService.

    Returns:
        Role: Information about role.
    Raises:
        HTTPException: If no such role in database
    """
    return await role_service.single_role(role_name)


@router.post('', description='Create new role')
@roles_required([UserRole.admin])
async def create_role(
    request: AuthRequest,
    role: Role,
    role_service: RoleService = Depends(get_role_service),
):
    """Create new role.
    Args:
        request (AuthRequest): Request object.
        role (Role): Class with new role
        role_service (RoleService): An instance of RoleService.
    """
    return await role_service.create_new_role(role.model_dump())


@router.put('/{role_name}', description='Update existing role')
@roles_required([UserRole.admin])
async def update_role(
    request: AuthRequest,
    role_name: str,
    new_info: dict,
    role_service: RoleService = Depends(get_role_service),
):
    """Update existing role.
    Args:
        request (AuthRequest): Request object.
        role_name (str): Name of the role
        new_info (dict): Dictionary with new information
        role_service (RoleService): An instance of RoleService.
    Returns:
        Role: Updated role
    """
    return await role_service.update_role(role_name, new_info)


@router.delete('/{role_name}', description='Delete existing role')
@roles_required([UserRole.admin])
async def delete_role(
    request: AuthRequest,
    role_name: str,
    role_service: RoleService = Depends(get_role_service),
):
    """Delete existing role.
    Args:
        request (AuthRequest): Request object.
        role_name (str): Name of the role
        role_service (RoleService): An instance of RoleService.
    Returns:
        dict: Dictionary, containing helpful information.
    """
    return await role_service.delete_role(role_name)


@router.post(
    '/assign/{user_id}',
    response_model=HTTPStatus,
    description='Assign role to user. Request role name in body request',
)
@roles_required([UserRole.admin])
async def assign_role_to_user(
    request: AuthRequest,
    user_id: str,
    role: RoleList,
    service: RoleService = Depends(get_role_service),
):
    """
    Assigns a role to a user.

    Args:
        request (AuthRequest): Request object
        user_id (str): The ID of the user.
        role (RoleList): The role to be assigned to the user.
        service (RoleService, optional): The RoleService dependency.

    Returns:
        HTTPStatus: The HTTP status code indicating the success of the operation,
        or raise HTTP Exception if role or user does not exist.
    """
    await service.assign_role(user_id, role.name)
    return HTTPStatus.OK


@router.delete(
    '/assign/{user_id}',
    response_model=HTTPStatus,
    description='Remove role from user. Request role name in body request',
)
@roles_required(UserRole.admin)
async def remove_role_to_user(
    request: AuthRequest,
    user_id: str,
    role: RoleList,
    service: RoleService = Depends(get_role_service),
):
    """
    Removes a role from a user.

    Args:
        request (AuthRequest): Request object.
        user_id (str): The ID of the user.
        role (RoleList): The role to be removed from the user.
        service (RoleService, optional): The RoleService dependency.

    Returns:
        HTTPStatus: The HTTP status code indicating the success of the operation,
        or raise HTTPException if role or user does not exist.
    """
    await service.remove_role_from_user(user_id, role.name)
    return HTTPStatus.OK


@router.get(
    '/user_role/{user_id}',
    response_model=UserRoles,
    description="Get all user's roles.",
)
async def get_all_user_roles(
    user_id: str, service: RoleService = Depends(get_role_service)
) -> UserRoles | HTTPException:
    """
    Retrieves all roles of a user.

    Args:
        user_id (str): The ID of the user.
        service (RoleService, optional): The RoleService dependency. Defaults to Depends(get_role_service).

    Returns:
        Union[UserRoles, HTTPException]: The UserRoles object containing the user's roles,
        or an HTTPException if the user is not found.
    """
    return await service.all_users_role(user_id)
