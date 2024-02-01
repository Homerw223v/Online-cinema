from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseTestSettings(BaseSettings):
    host: str
    port: str


class RedisSettings(BaseTestSettings):
    model_config = SettingsConfigDict(env_prefix='REDIS_')


class PostgresSettings(BaseTestSettings):
    dbname: str = Field(alias='POSTGRES_DB')
    user: str
    password: str

    model_config = SettingsConfigDict(env_prefix='POSTGRES_')


class ServiceSettings(BaseSettings):
    service_url: str
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int


redis_settings = RedisSettings()
postgres_settings = PostgresSettings()
service_settings = ServiceSettings()
