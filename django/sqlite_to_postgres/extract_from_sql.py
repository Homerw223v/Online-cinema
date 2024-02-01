"""Import data from sqlite database."""

import sqlite3
from collections import namedtuple
from dataclasses import dataclass, fields

from log import logger


@dataclass
class SQLiteExtractor:
    """Class for extracting data from sqlite3 database."""

    conn: sqlite3.Connection
    batch_size: int = 1000

    def extract_movies_from(self, table: namedtuple) -> dict:
        """
        Extrack all tables from sqlite database.

        Args:
            table (namedtuple): Class with table name and columns names

        Yields:
            sqlite_data: Data from sqlite database
        """
        cur: sqlite3.Cursor = self.conn.cursor()
        cur.execute(self._create_query(table))
        try:
            while True:
                rows: list = cur.fetchmany(size=self.batch_size)
                if not rows:
                    break
                sqlite_data: dict = {table.table_name: [table.table_cls(**row) for row in rows]}
                yield sqlite_data
        except sqlite3.OperationalError as oe:
            logger.error(oe)
        except Exception as ex:
            logger.error(ex)
        finally:
            cur.close()

    @staticmethod
    def _create_query(table: namedtuple) -> str:
        """
        Create SQL query to get data from sqlite3.

        Args:
            table (namedtuple): Class with table name and columns names

        Returns:
            (str): Query string
        """
        fields_names: str = ', '.join([field.name for field in fields(table.table_cls)])
        return f'SELECT {fields_names} FROM {table.table_name}'
