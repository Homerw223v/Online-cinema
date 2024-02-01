"""This module provides the configuration settings for the project, including logging and Elasticsearch."""
import os
from http import HTTPStatus

from core.logger import LOGGING
from fastapi import HTTPException
from pydantic import Field
from pydantic_settings import BaseSettings
from uvicorn.workers import UvicornWorker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def on_give_up(_):
    print(_)
    raise HTTPException(status_code=HTTPStatus.GATEWAY_TIMEOUT, detail='Something went wrong. Try again later')


class ElasticSettings(BaseSettings):
    es_host: str
    es_movies_index: str
    es_genres_index: str
    es_person_index: str


class RedisSettings(BaseSettings):
    host: str = Field(validation_alias='redis_host')
    port: int = Field(validation_alias='redis_port', default=6379)


class ProjectSettings(BaseSettings):
    project_name: str
    cache_expire: int

    elastic: ElasticSettings = ElasticSettings()
    redis: RedisSettings = RedisSettings()


class MoviesUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {
        "loop": "asyncio",
        "http": "h11",
        "log_config": LOGGING,
    }


project_settings = ProjectSettings()
