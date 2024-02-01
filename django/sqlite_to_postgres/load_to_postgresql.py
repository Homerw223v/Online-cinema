"""Load data to PostgresSQL."""

from dataclasses import asdict, dataclass, fields

from log import logger
from psycopg2 import DataError, IntegrityError, OperationalError
from psycopg2.extensions import connection as _connection
from psycopg2.extras import execute_batch


@dataclass
class PostgresSaver:
    """Class for insert data to PostgresSQL database."""

    conn: _connection

    def save_all_data(self, sqlite_data: dict) -> None:
        """
        Save all data to Postgres database.

        Args:
            sqlite_data (dict): Data from SQLite3

        Returns:
            None
        """
        if not sqlite_data:
            logger.info('Nothing to copy.')
            return
        with self.conn.cursor() as cur:
            try:
                for table_name, records in sqlite_data.items():
                    query: str = self._create_sql_query(table_name, records[0])
                    rows: list = [asdict(record) for record in records]
                    execute_batch(cur, query, rows)
            except (OperationalError, DataError, IntegrityError) as ut:
                logger.error(ut)
            except Exception as ex:
                logger.error(ex)
            else:
                self.conn.commit()

    @staticmethod
    def _create_sql_query(table_name: str, row: dataclass) -> str:
        """
        Create SQL query to insert rows in Postgres.

        Args:
            table_name (str): Name of table in database
            row (dataclass): Class with column names

        Returns:
            query (str): Query string
        """
        col_names: str = ', '.join([field.name for field in fields(row)])
        placeholders: str = ', '.join(f'%({field.name})s' for field in fields(row))
        return f'INSERT INTO content.{table_name} ({col_names}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING'
