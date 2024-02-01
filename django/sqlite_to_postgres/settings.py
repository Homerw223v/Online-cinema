"""Settings for sqlite to postgres module."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BATCH_SIZE: int = 1000

DSN: dict = {
    'dbname': os.environ.get('POSTGRES_DB'),
    'user': os.environ.get('POSTGRES_USER'),
    'password': os.environ.get('POSTGRES_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'port': os.environ.get('DB_PORT'),
}

sqlite_bd = Path(__file__).resolve().parent / 'db.sqlite'
