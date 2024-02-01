from datetime import datetime
from uuid import UUID

import orjson
from pydantic import BaseModel, EmailStr


class AbstractModel(BaseModel):
    id: UUID
    created: datetime

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson.dumps


class UserModel(AbstractModel):
    name: str | None = None
    surname: str | None = None
    birthday: datetime | None = None
    email: EmailStr
    password: str
    created_at: datetime
    updated_at: datetime


class UserHistoryModel(BaseModel):
    finger_print: str
    time: datetime
    action: str
