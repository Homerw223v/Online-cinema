from datetime import datetime
from typing import Iterator
from uuid import UUID

from psycopg2.extensions import cursor

from .query_builder import QueryBuilder, QueryBuilderTables


class QueryExecutor:
    """
    Extract data form Postgres database.
    """

    @classmethod
    def get_modified_records_ids(
        cls, table: QueryBuilderTables, cursor: cursor, break_point: datetime
    ) -> Iterator[UUID] | None:
        """
        Returns the ids of records from the table through the database cursor.

        :param table: Name of the table from the database.
        :param cursor: Database cursor.
        :param break_point: Time, after which the modified records should be extracted from database.

        :return: Iterator with modified records IDs.
        """
        query = QueryBuilder.get_modified_records_ids_query(table, break_point)
        cursor.execute(query)
        for row in cursor.fetchall():
            yield row[0]

    @classmethod
    def get_modified_m2m_records(
        cls, table: QueryBuilderTables, cursor: cursor, break_point: datetime
    ) -> Iterator[UUID | None]:
        """
        Returns the ids of records whose associated records have been modified.

        :param table: Name of the table from the database.
        :param cursor: Database cursor.
        :param break_point: Time, after which the modified records should be extracted from database.

        :return: Iterator with modified records IDs.
        """
        ids = set(cls.get_modified_records_ids(table, cursor, break_point))

        if len(ids):
            query = QueryBuilder.get_modified_m2m_records_query(table, ids)
            cursor.execute(query)
            for row in cursor.fetchall():
                yield row[0]
        else:
            return iter(())
