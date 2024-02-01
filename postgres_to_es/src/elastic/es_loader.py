import json
import logging
from typing import Iterator

import backoff
from elasticsearch import Elasticsearch, helpers

from src.config import BaseAppSettings, ElasticSearchDNS, ESBackoffSettings
from src.config.elastic import BaseESIndexSettings


class ElasticSearchLoader:
    """
    Transfer data from Postgres to Elastic search.
    """

    SETTINGS_PATH = 'src/assets/settings.json'

    def __init__(self, es_index_settings: BaseESIndexSettings) -> None:
        """
        Constructor.

        :param es_index_settings: Name of ES index.
        """
        self.es_settings = ElasticSearchDNS()
        self.es = Elasticsearch(f'{self.es_settings.protocol}://{self.es_settings.host}:{self.es_settings.port}')
        self.es_index_settings = es_index_settings
        self.create()

    @backoff.on_exception(**ESBackoffSettings().model_dump())
    def load(self, data_generator: Iterator[dict | None]) -> None:
        """
        Load data from database to ElasticSearch.

        :param data_generator: Generator for data loading in ES.
        """
        helpers.bulk(
            client=self.es,
            actions=data_generator,
            index=self.es_index_settings.name,
            chunk_size=BaseAppSettings().batch_size,
        )
        self.es.close()

    @property
    def index_mappings(self) -> dict:
        """
        Return ElasticSearch index mappings.
        """
        with open(self.es_index_settings.index_path, 'r') as fp:
            return json.load(fp)['mappings']

    @property
    def index_settings(self) -> dict:
        """
        Return ElasticSearch index settings.
        """
        with open(self.SETTINGS_PATH, 'r') as fp:
            return json.load(fp)['settings']

    def create(self) -> None:
        """
        Create new elastic search index, if not exists.
        """
        if self.es.indices.exists(index=self.es_index_settings.name):
            logging.info(f'Index {self.es_index_settings.name} exists.')
        else:
            logging.info(f'New index {self.es_index_settings.name} has been created.')
            self.es.indices.create(
                index=self.es_index_settings.name,
                mappings=self.index_mappings,
                settings=self.index_settings,
            )
