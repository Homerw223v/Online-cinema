"""Classes for each table in database."""

import datetime
from collections import namedtuple
from dataclasses import dataclass, field
from uuid import uuid4

now: datetime = datetime.datetime.utcnow()


@dataclass
class FilmWork:
    """Class for film_work table."""

    title: str
    description: str
    rating: float
    type: str
    creation_date: datetime = field(default=None)
    created_at: datetime = field(default=now)
    updated_at: datetime = field(default=now)
    id: uuid4 = field(default=uuid4)


@dataclass
class Genre:
    """Class for genre table."""

    name: str
    description: str
    created_at: datetime = field(default=now)
    updated_at: datetime = field(default=now)
    id: uuid4 = field(default=uuid4)


@dataclass
class Person:
    """Class for person table."""

    full_name: str
    created_at: datetime = field(default=now)
    updated_at: datetime = field(default=now)
    id: uuid4 = field(default=uuid4)


@dataclass
class GenreFilmWork:
    """Class for genre_film_work table."""

    film_work_id: uuid4
    genre_id: uuid4
    created_at: datetime = field(default=now)
    id: uuid4 = field(default=uuid4)


@dataclass
class PersonFilmWork:
    """Class for person_film_work table."""

    film_work_id: uuid4
    person_id: uuid4
    role: str
    created_at: datetime = field(default=now)
    id: uuid4 = field(default=uuid4)


FromSQL: namedtuple = namedtuple('FromSQL', ['table_cls', 'table_name'])
tables: tuple = (
    FromSQL(FilmWork, 'film_work'),
    FromSQL(Person, 'person'),
    FromSQL(Genre, 'genre'),
    FromSQL(PersonFilmWork, 'person_film_work'),
    FromSQL(GenreFilmWork, 'genre_film_work'),
)
