from fastapi import Request

from schemas.user import UserShirt


class AuthRequest(Request):
    custom_user: UserShirt
