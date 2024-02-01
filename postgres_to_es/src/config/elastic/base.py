import inspect
from typing import Type
from uuid import UUID

from psycopg2.extensions import cursor
from datetime import datetime

from pydantic_settings import BaseSettings
from src.elastic import es_models
from src.elastic.es_models import AbstractModel


class BaseESIndexSettings(BaseSettings):
    """
    Base class for ElasticSearch index settings.

    Prerequisite for an index:
    1) Model create.
    2) Mapping created.
    3) Data extraction query developed.
    """

    name: str
    model: Type[AbstractModel]
    index_path: str
    data_extraction_query: str

    def __init__(self, index_name: str) -> None:
        """
        Constructor.

        :param index_name: Name of ElasticSearch index.
        """
        data = dict(
            name=index_name,
            model=self._get_model_obj(index_name),
            index_path=f'src/assets/es_{index_name}_schema.json',
            data_extraction_query=self._get_data_extraction_query(),
        )
        super().__init__(**data)

    def _get_model_obj(self, index_name) -> Type[AbstractModel]:
        """
        Return class object of data model for ElasticSearch index index_name.
        For example, if index name == movies, MovieModel will be returned.

        :param index_name: Name of ElasticSearch index.

        :return: Subclass object of AbstractModel.
        """

        for name, obj in inspect.getmembers(es_models):
            if name == f"{index_name[:-1].capitalize()}Model":
                return obj

        raise ValueError(f'No model for index {index_name}.')

    def _get_data_extraction_query(self):
        """
        Return SQL query for data extraction for the ElasticSearch index.
        """
        raise NotImplementedError('The method _get_data_extraction_query is not implemented.')

    def get_modified_ids(self, cursor: cursor, break_point: datetime) -> set[UUID]:
        """
        Return ids of records in the database of cursor after the breakpoint.

        :param cursor: Cursor of the database.
        :param break_point: Point of time after which modified records should be returned.

        :return: Iterator with modified records.
        """
        raise NotImplementedError('The method get_modified_ids is not implemented.')
