from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str
    password_confirm: str
    name: str | None = None
    surname: str | None = None
    birthday: str | None = None


class UserInDBSchema(BaseModel):
    id: UUID
    email: str
    name: str | None
    surname: str | None
    password: str

    class Config:
        from_attributes = True


class TokensSchema(BaseModel):
    access_token: str
    refresh_token: UUID
    token_type: str
    email: EmailStr


class UserSignInSchema(BaseModel):
    email: EmailStr
    password: str
    finger_print: str


class DataForRefreshTokensSchema(BaseModel):
    refresh_token: UUID
    finger_print: str


class RefreshTokenSchema(BaseModel):
    refresh_token: UUID
    expires_at: datetime
