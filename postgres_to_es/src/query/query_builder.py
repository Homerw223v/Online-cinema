from datetime import datetime
from enum import Enum
from typing import Iterable
from uuid import UUID


class QueryBuilderTables(Enum):
    """
    Documents the names of tables that can be used in methods of the QueryBuilder class.
    """

    FILM_WORK = 'film_work'
    PERSON = 'person'
    GENRE = 'genre'


class QueryBuilder:
    """
    Returns SQL queries to retrieve data from the Filmwork, Person and Genre tables, as well as M2M tables.
    """

    @staticmethod
    def get_modified_records_ids_query(table: QueryBuilderTables, break_point: datetime) -> str:
        """
        Returns the id of records from the table that were changed after break_point.

        :param table: Table from the movies_database.
        :param break_point: Time after which changed records are selected.

        :return: SQL query to retrieve record ids from the database.
        """
        query = f"""
            SELECT id
            FROM content.{table.value}
            WHERE updated_at > '{break_point.strftime('%Y-%m-%d %H:%M:%S')}'
            ORDER BY updated_at;
        """
        return query

    @classmethod
    def get_modified_m2m_records_query(cls, table: QueryBuilderTables, records_ids: Iterable[UUID]) -> str:
        """
        Returns the ids of records from the film_work table, related through many-to-many relationships with records
        from the table and id records_ids.

        :param table: Table from the movies_database.
        :param records_ids: ID of records from the table.

        :return: SQL query to retrieve record ids from the database.
        """
        ids = cls.format_ids(records_ids)
        query = f"""
            SELECT fw.id
            FROM content.film_work fw
            LEFT JOIN content.{table.value}_film_work tfw ON tfw.film_work_id = fw.id
            WHERE tfw.{table.value}_id IN ('{ids}')
            ORDER BY fw.updated_at;
        """
        return query

    @classmethod
    def get_es_index_data_query(cls, record_ids: Iterable[UUID], query_template: str) -> str:
        """
        Returns an SQL query to retrieve information to be added to the ElasticSearch index according to the
        query template.

        :param record_ids: ID of records.
        :param query_template: Template of query to return data query.

        :return: SQL query to retrieve information.
        """
        ids = cls.format_ids(record_ids)
        return query_template.format(ids)

    @staticmethod
    def format_ids(record_ids: Iterable[UUID]) -> str:
        """
        Converts record_ids for insertion into an SQL query.

        :param record_ids: IDs of records from the film_work, genre, or person tables.

        :return: string with id in proper format.
        """
        return '\', \''.join(record_ids)
