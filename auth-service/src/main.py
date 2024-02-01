"""
This module initializes auth application and includes .
It establishes a connection to Postgres and Redis on application startup and closes the connection on shutdown.
"""
import logging
from contextlib import asynccontextmanager

from api.v1 import auth, roles, user
from core.config import settings
from db import redis
from db.base_bd import BaseDB
from db.connection import engine
from exceptions.auth import get_current_user_global
from fastapi import Depends, FastAPI
from fastapi.responses import ORJSONResponse
from starlette.middleware.sessions import SessionMiddleware
from redis.asyncio import Redis

logger = logging.getLogger('auth_service')


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(BaseDB.metadata.drop_all)
        await conn.run_sync(BaseDB.metadata.create_all)


@asynccontextmanager
async def lifespan(_):
    """
    Event handler for application startup.
    Establishes a connection to Redis.
    """
    if settings.debug:
        await init_models()
    redis.redis = Redis(**settings.redis.model_dump())
    logger.info('Redis have been configured')

    yield

    await redis.redis.close()


app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)
app.add_middleware(SessionMiddleware, secret_key=settings.secret)

app.include_router(auth.router, prefix='/api/v1/auth', tags=['auth'])
app.include_router(
    roles.router,
    prefix='/api/v1/roles',
    tags=['roles'],
    dependencies=[Depends(get_current_user_global)],
)
app.include_router(
    user.router,
    prefix='/api/v1/users',
    tags=['users'],
    dependencies=[Depends(get_current_user_global)],
)
