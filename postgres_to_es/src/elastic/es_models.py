from datetime import datetime
from typing import List
from uuid import UUID

import orjson
from pydantic import BaseModel, field_validator


class AbstractModel(BaseModel):
    id: UUID


class GenreModel(AbstractModel):
    name: str


class PersonRolesModel(AbstractModel):
    role: List[str] | None

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson.dumps
        validate_assignment = True

    @field_validator('role')
    @classmethod
    def validate(cls, value):
        return value or []


class PersonModel(AbstractModel):
    full_name: str
    films: List[PersonRolesModel] | None


class PersonSubModel(AbstractModel):
    name: str


class MovieModel(AbstractModel):
    title: str
    imdb_rating: float | None = None
    description: str | None
    creation_date: datetime | None
    directors: list[PersonSubModel] | None
    actors: list[PersonSubModel] | None
    writers: list[PersonSubModel] | None
    genre: list[GenreModel] | None

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson.dumps
        validate_assignment = True

    @field_validator('directors', 'actors', 'writers', 'genre')
    @classmethod
    def validate(cls, value):
        return value or []
