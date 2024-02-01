from datetime import datetime
from uuid import UUID

import orjson
from pydantic import BaseModel, field_validator


class AbstractModel(BaseModel):
    id: UUID

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson.dumps


class GenreModel(AbstractModel):
    name: str


class PersonModel(AbstractModel):
    name: str
    surname: str
    movies: list[str] | None

    def __init__(self, **data: dict) -> None:
        data['name'], data['surname'] = data['full_name'].split(' ')
        del data['full_name']
        super().__init__(**data)


class MovieModel(AbstractModel):
    title: str
    imdb_rating: float | None = None
    description: str | None
    creation_date: datetime | None
    directors: list[dict[str, UUID | str]] | None
    actors: list[dict[str, UUID | str]] | None
    writers: list[dict[str, UUID | str]] | None
    genre: list[dict[str, UUID | str]] | None

    class Config:
        validate_assignment = True

    @field_validator('directors', 'actors', 'writers', 'genre')
    @classmethod
    def validate(cls, value):
        return value or []


class PersonFilms(AbstractModel):
    """Nested persons films response object"""
    role: list[str]


class PersonAPI(AbstractModel):
    """Person response object"""
    full_name: str
    films: list[PersonFilms] = []


class PersonFilmsAPI(AbstractModel):
    """Films where person appears (actor, writer and so on)"""
    title: str
    imdb_rating: float | None
