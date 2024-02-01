from uuid import UUID

from db.base_bd import RoleTable
from pydantic import BaseModel


class UserRoles(BaseModel):
    id: UUID
    name: str | None
    email: str
    roles: list


class UserShirt(BaseModel):
    email: str
    roles: list[str]
