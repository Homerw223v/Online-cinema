from http import HTTPStatus

from fastapi import HTTPException


class BaseDBException(HTTPException):
    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f'{class_name}(status_code={self.status_code.real}, detail={self.detail!r})'


class RoleDoesNotExists(BaseDBException):
    def __init__(
        self,
        detail: str = 'Role does not exist',
        status_code: int = HTTPStatus.BAD_REQUEST,
    ):
        super().__init__(status_code=status_code, detail=detail)


class RolesDoesNotExists(BaseDBException):
    def __init__(
        self,
        detail: str = 'Roles does not exists',
        status_code: int = HTTPStatus.BAD_REQUEST,
    ):
        super().__init__(status_code=status_code, detail=detail)


class RoleAlreadyExists(BaseDBException):
    def __init__(
        self,
        detail: str = 'Role already exist',
        status_code: int = HTTPStatus.CONFLICT,
    ):
        super().__init__(status_code=status_code, detail=detail)


class NoSuchRoleForUser(BaseDBException):
    def __init__(
        self,
        detail: str = 'User does not have such role.',
        status_code: int = HTTPStatus.BAD_REQUEST,
    ):
        super().__init__(status_code=status_code, detail=detail)


class UserDoesNotExists(BaseDBException):
    def __init__(
        self,
        detail: str = 'User does not exist.',
        status_code: int = HTTPStatus.BAD_REQUEST,
    ):
        super().__init__(status_code=status_code, detail=detail)


class OAuthServiceDoesNotExist(BaseDBException):
    def __init__(
        self,
        detail: str | None = None,
        status_code: int = HTTPStatus.BAD_REQUEST,
    ):
        super().__init__(status_code=status_code, detail=detail)
