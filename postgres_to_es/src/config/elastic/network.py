from typing import Tuple, Any

from elasticsearch import exceptions
from pydantic import Field
from pydantic_settings import SettingsConfigDict

from src.config.base import BaseDNS, BaseBackoffSettings


class ElasticSearchDNS(BaseDNS):
    protocol: str
    model_config = SettingsConfigDict(env_prefix='ES_')


class ESBackoffSettings(BaseBackoffSettings):
    exception: Tuple[Any, ...] = Field((exceptions.ConnectionError, exceptions.ConnectionTimeout))
