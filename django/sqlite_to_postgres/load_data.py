"""Transferring data from sqlite3 to postgres."""

import sqlite3
from contextlib import contextmanager

import psycopg2
from extract_from_sql import SQLiteExtractor
from load_to_postgresql import PostgresSaver
from log import logger
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from settings import BATCH_SIZE, DSN, sqlite_bd
from tables import tables


@contextmanager
def conn_context_sqlite(db_path: str):
    """
    Connect to sqlite3 database.

    Args:
        db_path (str): Database path

    Yields:
        conn: Connection object
    """
    conn: sqlite3.Connection = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@contextmanager
def conn_context_postgres(dsn: dict):
    """
    Connect to postgres database.

    Args:
        dsn (dict): Data source name

    Yields:
        conn: Connection object
    """
    conn: _connection = psycopg2.connect(**dsn, cursor_factory=DictCursor)
    yield conn
    conn.close()


def load_from_sqlite(sql_conn: sqlite3.Connection, pg_conn: _connection) -> None:
    """
    Transfer data from SQLite to Postgres.

    Args:
        sql_conn (sqlite3.Connection): Connection to sqlite3 object
        pg_conn (_connection): Connection to postgres object

    Returns: None
    """
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_extractor = SQLiteExtractor(sql_conn, BATCH_SIZE)
    for table in tables:
        sqlite_data: dict = sqlite_extractor.extract_movies_from(table)
        logger.info(f'Coping "{table.table_name}" table.')
        for batch in sqlite_data:
            postgres_saver.save_all_data(batch)


if __name__ == '__main__':
    try:
        with (
            conn_context_sqlite(sqlite_bd) as sqlite_conn,
            conn_context_postgres(DSN) as postgres_conn,
        ):
            logger.info('Connections to databases is open.')
            load_from_sqlite(sqlite_conn, postgres_conn)
    except psycopg2.OperationalError as ex:
        logger.error(ex)
    finally:
        logger.info('Connections closed.')
