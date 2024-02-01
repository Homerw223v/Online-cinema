import psycopg
import pytest_asyncio
from psycopg import cursor
from settings import postgres_settings

from .auth_service_data import TEST_DATA


@pytest_asyncio.fixture(name='fill_test_database', scope='module', autouse=True)
async def fill_test_database() -> None:
    """
    Fill test database with the test data.
    """
    with psycopg.connect(**postgres_settings.model_dump()) as conn:
        with conn.cursor() as curs:
            # await create_database_schema(curs)
            await add_data_to_database(curs)
            conn.commit()

            yield

            await clear_test_database(curs)
            conn.commit()


async def create_database_schema(curs: cursor):
    """
    Create database schema with database cursor curs.

    :param curs: Cursor of the database.
    """
    with open('test_data/test_data.ddl', 'r') as query:
        curs.execute(query.read())


async def add_data_to_database(curs: cursor) -> None:
    """
    Fill test data for table table_name with database cursor curs.

    :param curs: Cursor of the database.
    """

    for table in TEST_DATA.keys():
        for item in TEST_DATA[table]:
            curs.execute(
                f"""
                    INSERT INTO "{table}" ({', '.join(item.keys())})
                    VALUES ('{"', '".join(item.values())}');
                """
            )


async def clear_test_database(curs: cursor) -> None:
    """
    Remove test data from the database.

    :param curs: Cursor of the database.
    """
    for table in TEST_DATA.keys():
        curs.execute(f'TRUNCATE TABLE {table} CASCADE;')
    curs.execute('DROP SCHEMA IF EXISTS tests;')
