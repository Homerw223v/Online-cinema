import asyncio

from core.config import settings
from db.redis import get_cache
from db.refresh_session import get_refresh_session_db
from db.role_db import get_role_db
from db.user_db import get_user_db
from exceptions.db_error import RoleAlreadyExists
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from service.auth_servise import AuthService
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

dsn = (f"postgresql+asyncpg://{settings.postgres.user}:{settings.postgres.password}@"
       f"{settings.postgres.host}:{settings.postgres.port}/{settings.postgres.db}")

engine = create_async_engine(dsn, echo=True, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str
    password_confirm: str


async def create_admin():
    async with async_session() as session:
        try:
            role_db = await get_role_db(sessions=session)
            await role_db.create_role({"name": "Admin"})
        except RoleAlreadyExists:
            await session.rollback()
        user_dict = {
            'email': str(input('Email: ')),
            'password': str(input('Password: ')),
            'password_confirm': str(input('Confirm password: '))
        }
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        user_db = await get_user_db(session)
        cache = await get_cache()
        refr_session = await get_refresh_session_db(session)
        auth_service = AuthService(pwd_context=pwd_context, user_db=user_db, cache=cache, refr_session=refr_session)
        user = await auth_service.register_user(UserCreateSchema(**user_dict))
        print(user, 'created.')


if __name__ == "__main__":
    asyncio.run(create_admin())
    del async_session
