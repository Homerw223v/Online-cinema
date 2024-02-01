from functools import wraps
from typing import Annotated

from exceptions.auth_request import AuthRequest
from fastapi import Depends, HTTPException, Request, status
from pydantic import ValidationError
from schemas.user import UserRoles, UserShirt
from service.auth_servise import AuthService, get_service


def roles_required(roles: list[str]):
    """Check user has permission according his roles
    :param roles: list of roles.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user: UserShirt = kwargs.get('request').custom_user
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Operation not permitted for you',
                )
            for role in user.roles:
                if role not in roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail='Operation not permitted for you',
                    )
            return await func(*args, **kwargs)

        return wrapper

    return decorator


class JWTBearer:
    async def __call__(
        self,
        request: Request,
        auth_service: Annotated[AuthService, Depends(get_service)],
    ):
        try:
            token = request.headers.get('Authorization').split()[1]
            payload = await auth_service.decode_jwt_token(token)
            return UserShirt(**payload)
        except (ValidationError, IndexError):
            return None


async def get_current_user_global(
    request: AuthRequest, user: UserShirt = Depends(JWTBearer())
):
    request.custom_user = user
