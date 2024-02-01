from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RoleList(BaseModel):
    name: str

    class Config:
        from_attributes = True


class Role(RoleList):
    id: UUID
    name: str
    created: datetime


class UserRoleList(RoleList):
    user_id: str
