import string
import uuid
from datetime import datetime, timedelta, timezone
from random import choice
from typing import Annotated

from core.config import settings
from db.base_bd import RefreshSession, User
from db.redis import get_cache
from db.refresh_session import get_refresh_session_db
from db.social_auth_db import SocialAuthMethods, get_social_auth_db
from db.user_db import UserMethods, get_user_db
from exceptions import errors
from fastapi import Depends
from jose import jwt
from models.abstract_models.abstract_cache import AbstractCache
from passlib.context import CryptContext
from schemas.auth import (
    DataForRefreshTokensSchema,
    RefreshTokenSchema,
    TokensSchema,
    UserCreateSchema,
)
from schemas.social_auth import SocialOAuthUserModel
from starlette.requests import Request


class AuthService:
    def __init__(
        self,
        pwd_context: CryptContext,
        cache: AbstractCache,
        user_db: UserMethods,
        refr_session,
        social_auth: SocialAuthMethods,
    ):
        self._pwd_context = pwd_context
        self._cache = cache
        self.user_db = user_db
        self.refr_session = refr_session
        self.social_auth = social_auth

    async def register_user(self, user: UserCreateSchema):
        """Register a new user. Save to the database. If the user does not exist.

        :param user: User to register
        :return: None

        """

        same_user = await self.user_db.get_by_email(user.email)
        if same_user is not None:
            raise errors.UserExistsInDBException('User already exists')

        if user.password != user.password_confirm:
            raise errors.PasswordsDontMatchException('Passwords do not match')

        user_dto = user.model_dump()
        user_dto['password'] = self._pwd_context.hash(user_dto['password'])
        del user_dto['password_confirm']
        saved_user = await self.user_db.add(**user_dto)

        return saved_user

    async def authenticate_user(
        self, email: str, password: str
    ) -> User | None:
        """Authenticate a user by email and password.

        :param email: User email.
        :param password: User password.

        :return: User or None
        """

        user = await self.user_db.get_by_email(email)
        if user is None:
            raise errors.UserNotExistsInDBException('User not exists')

        if not self._pwd_context.verify(password, user.password):
            raise errors.PasswordNotVerified('Wrong password')
        return user

    @staticmethod
    def generate_password() -> str:
        """
        Generate a random password.

        Returns:
            str: The generated password.
        """
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(choice(characters) for _ in range(30))

    async def authenticate_social_user(
        self, social_user: SocialOAuthUserModel, request: Request
    ) -> TokensSchema:
        """
        Authenticate a user using social login.

        If the social user already exists in the system,
         retrieve the corresponding user and create an authentication session.
        If the social user is new, register the user,
         add social authentication information, and create an authentication session.

        Args:
            social_user (SocialOAuthUserModel): The social user information.
            request (Request): The request object.

        Returns:
            TokensSchema: The authentication tokens.
        """
        if await self.social_auth.get_row_by_social_id(social_user.social_id, social_user.social_name):
            user: User = await self.user_db.get_by_email(social_user.email)
        else:
            password: str = self.generate_password()
            create_user = UserCreateSchema(
                email=social_user.email,
                password=password,
                password_confirm=password,
                name=social_user.first_name,
                surname=social_user.last_name,
            )
            user: User = await self.register_user(create_user)
            await self.social_auth.add_social_auth_user(social_user, user)
        return await self.create_auth_session(
            user, request.headers.get('user-agent')
        )

    @staticmethod
    async def decode_jwt_token(token: str) -> dict | None:
        """Decode a JWT access token and return the data

        :param token: JWT access token
        :return: JWT data (dict) or None

        """
        try:
            payload = jwt.decode(
                token,
                key=settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
        except jwt.JWTError:
            return None
        return payload

    async def create_auth_session(
        self,
        user: User,
        finger_print: str,
    ) -> TokensSchema:

        """Creates a new auth session for the user with given client finger_print

        :param user: User who create auth session.
        :param finger_print: User fingerprint.

        :return: None
        """

        access_token_expires_delta = timedelta(
            minutes=settings.access_token_expire_minutes
        )
        token_data = {'email': user.email, 'roles': ['admin']}
        access_token = self._create_token(
            token_data, access_token_expires_delta
        )

        refresh_token = self._create_refresh_token(
            settings.refresh_token_expire_minutes
        )

        await self._cache.set(
            access_token,
            finger_print,
            expired=access_token_expires_delta.seconds,
        )

        existed_refresh_session = await self.refr_session.get_by_finger_print(
            user.email, finger_print
        )

        # If refresh session exists in DB, so update only
        if existed_refresh_session is not None:
            existed_refresh_session.refresh_token = refresh_token.refresh_token
            existed_refresh_session.expires_at = refresh_token.expires_at
            await self.refr_session.session.commit()

        # otherwise create a new one
        else:
            refresh_session_dict = dict(
                user_id=user.id,
                refresh_token=refresh_token.refresh_token,
                finger_print=finger_print,
                expires_at=refresh_token.expires_at,
            )

            await self.refr_session.add(**refresh_session_dict)

        return TokensSchema(
            access_token=access_token,
            refresh_token=refresh_token.refresh_token,
            token_type='bearer',
            email=user.email,
        )

    def _create_token(
        self,
        data: dict,
        expires_delta: timedelta,
    ) -> str:
        """Create a new token with the given data and expiration

        :param data: The data to be stored in the token.
        :param expires_delta: Period after which the token has expired.

        :return: The created token.
        """

        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({'exp': expire})
        to_encode.update(data)
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
        return encoded_jwt

    async def verify_refresh_token_get_new(
        self,
        token_data: DataForRefreshTokensSchema,
    ):
        """Check the refresh token in DB and verify user_agent or finger_print

        :param token_data: The data for refresh session.
        :return: None

        """

        existed_refresh_session = await self.refr_session.get_by_refresh_token(
            token_data.refresh_token
        )

        if existed_refresh_session is None:
            raise errors.RefreshTokenNotExists('Refresh Token does not exists')

        # Check token not expired
        if existed_refresh_session.expires_at < datetime.now(timezone.utc):
            raise errors.RefreshTokenExpired('Refresh Token expired')

        # In case of stolen refresh token we will delete auth session
        if not existed_refresh_session.finger_print == token_data.finger_print:
            raise errors.FingerprintNotMatch('Fingerprint not match')

        new_refresh_token = self._create_refresh_token(
            settings.refresh_token_expire_minutes
        )

        existed_refresh_session.refresh_token = new_refresh_token.refresh_token
        existed_refresh_session.expires_at = new_refresh_token.expires_at
        await self.refr_session.session.commit()

        user_roles = [r.name for r in existed_refresh_session.user.roles]
        token_data = {
            'email': existed_refresh_session.user.email,
            'roles': user_roles,
        }
        access_token_expires = timedelta(
            minutes=settings.access_token_expire_minutes
        )
        new_access_token = self._create_token(
            data=token_data, expires_delta=access_token_expires
        )

        output_token = TokensSchema(
            access_token=new_access_token,
            refresh_token=new_refresh_token.refresh_token,
            token_type='bearer',
            email=existed_refresh_session.user.email,
        )

        return output_token

    async def logout_user(self, refresh_data):
        """Logout the user

        :param refresh_data: Data which needs to log out user.
        :return: None

        """

        saved_refresh_session: RefreshSession = (
            await self.refr_session.get_by_refresh_token(
                refresh_data.refresh_token,
            )
        )
        if saved_refresh_session is None:
            raise errors.RefreshTokenNotExists

        if saved_refresh_session.expires_at < datetime.now(timezone.utc):
            raise errors.RefreshTokenExpired
        else:
            token_expires_in = (
                datetime.now(timezone.utc) - saved_refresh_session.expires_at
            )
            await self._cache.set(
                key=str(saved_refresh_session.refresh_token),
                value=str(saved_refresh_session.user_id),
                expired=token_expires_in.seconds,
            )

        # update saved_refresh_session
        saved_refresh_session.refresh_token = None
        saved_refresh_session.expires_at = None
        await self.refr_session.session.commit()

    @staticmethod
    def _create_refresh_token(expires_in_min: int) -> RefreshTokenSchema:
        """Create a new refresh token with expiration after specified in minutes"""
        refresh_token = uuid.uuid4()
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=expires_in_min
        )
        return RefreshTokenSchema(
            refresh_token=refresh_token, expires_at=expires_at
        )


def get_service(
    cache: Annotated[AbstractCache, Depends(get_cache)],
    user_db=Depends(get_user_db),
    refr_session=Depends(get_refresh_session_db),
    social_auth=Depends(get_social_auth_db),
):
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    service = AuthService(
        pwd_context=pwd_context,
        cache=cache,
        user_db=user_db,
        refr_session=refr_session,
        social_auth=social_auth,
    )
    return service
