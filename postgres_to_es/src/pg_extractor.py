import logging
from contextlib import closing
from datetime import datetime, timedelta
from typing import Iterator, Tuple

import backoff
import psycopg2
from psycopg2.extras import DictCursor

from .config import BaseAppSettings, PGBackoffSettings, PostgresDNS, PostgresSettings
from .config.elastic import BaseESIndexSettings
from src.query.query_builder import QueryBuilder
from .state import State


class PostgresExtractor:
    """
    Extract data form Postgres database.
    """

    def __init__(self, es_index_settings: BaseESIndexSettings) -> None:
        """
        Constructor.

        :param es_index_settings: Settings of ElasticSearch index that should be updated.

        """
        self.state = State()
        self.settings = PostgresSettings()
        self.es_index_settings = es_index_settings

    @backoff.on_exception(**PGBackoffSettings().model_dump())
    def _extract(self) -> Iterator[dict] | None:
        """
        Extract data from the database with format corresponding to self.es_index_settings.name.
        """
        with closing(psycopg2.connect(**PostgresDNS().model_dump(), cursor_factory=DictCursor)) as conn:
            with conn.cursor() as curs:
                ids = self.es_index_settings.get_modified_ids(curs, self._get_breakpoint())
                if ids:
                    query = QueryBuilder.get_es_index_data_query(ids, self.es_index_settings.data_extraction_query)
                    curs.execute(query)

                    while rows := curs.fetchmany(BaseAppSettings().batch_size):
                        yield rows
                else:
                    logging.info(f'No records for update of index {self.es_index_settings.name} were identified.')

    def _get_breakpoint(self) -> datetime:
        """
        Return time, after which the modified records should be extracted from database.
        """
        break_point = self.state.get_state(f'{self.es_index_settings.name}_last_modified')
        return (
            datetime.strptime(break_point, self.settings.datetime_format)
            if break_point
            else datetime(year=1900, month=1, day=1)
        )

    def get_es_data_generator(self) -> Iterator[dict | None]:
        """
        Return iterator with modified records with format corresponding to self.es_index_settings.name.
        If no records were identified, returned empty iterator.
        """
        try:
            for batch in self._extract():
                for row in batch:
                    record, modified = self._transform(row)
                    yield record
                self._set_state(modified)
        except TypeError:
            return iter(())

    def _transform(self, record: dict) -> Tuple[dict, datetime]:
        """
        Transform record from database for ElasticSearch processing.

        :param record: Record to be modified. .

        :return: modified record and time of modification.
        """
        record = dict(record)
        modified: datetime = record[self.settings.modified_field]

        del record[self.settings.modified_field]

        record = self.es_index_settings.model(**record).model_dump()
        record['_id'] = record['id']

        return record, modified

    def _set_state(self, modified: datetime) -> None:
        """
        Save time of last modified record of ElasticSearch index in the state.

        :param modified: Time of record modification.
        """
        if modified.microsecond >= 1:
            modified += timedelta(seconds=1)
        self.state.set_state(
            f'{self.es_index_settings.name}_last_modified', modified.strftime(self.settings.datetime_format)
        )
