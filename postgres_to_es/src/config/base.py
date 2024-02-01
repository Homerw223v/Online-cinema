from typing import Callable

import backoff
from pydantic import Field
from pydantic_settings import BaseSettings


class BaseAppSettings(BaseSettings):
    batch_size: int
    state_path: str


class BaseDNS(BaseSettings):
    host: str
    port: int


class BaseBackoffSettings(BaseSettings):
    wait_gen: Callable = Field(backoff.expo)
    max_time: int = Field(60, alias='BACKOFF_MAX_TIME')
