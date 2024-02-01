from typing import Any, Tuple

from psycopg2 import errors
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .base import BaseBackoffSettings, BaseDNS


class PostgresDNS(BaseDNS):
    dbname: str = Field(alias='DB_NAME')
    user: str
    password: str
    options: str = Field('-c search_path=content')

    model_config = SettingsConfigDict(env_prefix='DB_')


class PostgresSettings(BaseSettings):
    datetime_format: str
    modified_field: str

    model_config = SettingsConfigDict(env_prefix='DB_')


class PGBackoffSettings(BaseBackoffSettings):
    exception: Tuple[Any, ...] = Field(
        (
            errors.ConnectionException,
            errors.CannotConnectNow,
            errors.ConnectionDoesNotExist,
            errors.ConnectionFailure,
        )
    )
