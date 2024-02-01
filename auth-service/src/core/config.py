"""This module provides the configuration settings for the auth-service, including logging, postgres and redis."""
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from uvicorn.workers import UvicornWorker

from .logger import LOGGING

load_dotenv()


class MoviesUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {
        'loop': 'asyncio',
        'http': 'h11',
        'log_config': LOGGING,
    }


class PostgresDB(BaseSettings):
    dbname: str = Field(alias='POSTGRES_DB')
    user: str
    password: str
    host: str
    port: int

    model_config = SettingsConfigDict(env_prefix='POSTGRES_')


class RedisDB(BaseSettings):
    host: str
    port: int = Field(default=6379)

    model_config = SettingsConfigDict(env_prefix='REDIS_')


class SocialYandex(BaseSettings):
    id: str
    secret: str
    redirect_uri: str

    model_config = SettingsConfigDict(env_prefix='YANDEX_CLIENT_')


class AuthSettings(BaseSettings):
    secret: str
    project_name: str
    cache_expire: int
    debug: bool = Field(default=True)
    postgres: PostgresDB = PostgresDB()
    redis: RedisDB = RedisDB()
    yandex: SocialYandex = SocialYandex()

    access_token_expire_minutes: int = 10
    refresh_token_expire_minutes: int = 60
    jwt_secret_key: str
    jwt_algorithm: str = 'HS256'


settings = AuthSettings()
