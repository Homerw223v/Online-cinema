from datetime import datetime
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from models.models import MovieModel
from models.params_models.PaginatedParams import PaginatedParams
from pydantic import BaseModel
from service.film import FilmService, get_film_service

router = APIRouter()


class FilmsListApi(BaseModel):
    """Represents model for film's list."""

    id: UUID
    title: str
    imdb_rating: float | None


class Film(FilmsListApi):
    """Represents model for a film."""

    genre: list[dict[str, UUID | str]] | None
    description: str | None
    creation_date: datetime | None
    directors: list[dict[str, UUID | str]] | None
    actors: list[dict[str, UUID | str]] | None
    writers: list[dict[str, UUID | str]] | None


@router.get(
    '/search',
    response_model=dict[str, list[FilmsListApi] | int | str],
    description='Search films by its title.',
)
async def search_films(
        params: PaginatedParams = Depends(),
        query: str = Query('', description='The keywords for searching films'),
        film_service: FilmService = Depends(get_film_service),
) -> dict[str, list[FilmsListApi] | int | str]:
    """
    Retrieve all films with pagination.
    Args:
        query (str): The keywords for searching films.
        params (PaginatedParams): Class with page and size parameters.
        film_service (FilmService): An instance of the FilmService.
    Returns:
        dict[str, list[FilmsListApi] | int | str]: A list of films with pagination.
    Raises:
        HTTPException: If the page number is incorrect or films are not found.
    """
    params.validate()
    films: dict[str, int | list[FilmsListApi]] | str = await film_service.get_multiple_movies(
        keyword=query,
        page=params.page,
        size=params.size,
    )
    if isinstance(films, str):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=films)
    films['results'] = [FilmsListApi(**film.model_dump()) for film in films['results']]
    return films


@router.get(
    '',
    response_model=dict[str, list[FilmsListApi] | int | str],
    description='Retrieve all films with pagination.',
)
async def all_films(
        params: PaginatedParams = Depends(),
        sort: str = Query(
            '',
            description='Sorting field for films.(Example: imdb_dating sort from top to bottom or '
                        '-imdb_rating from bottom to top)',
        ),
        genre: str | None = Query(None, description='Filter by genre'),
        film_service: FilmService = Depends(get_film_service),
) -> dict[str, list[FilmsListApi] | int | str]:
    """
    Retrieve all films with pagination.
    Args:
        params (PaginatedParams): Class with page and size parameters.
        sort (str | None): The sorting order for the films. Defaults to None.
        genre (int): The filter parameter for films by genre. Defaults to None.
        film_service (FilmService): An instance of the FilmService.
    Returns:
        dict[str, list[FilmsListApi] | int | str]: A list of films with pagination.
    Raises:
        HTTPException: If the page number is incorrect or films are not found.
    """
    params.validate()
    films: dict[str, int | list[FilmsListApi]] = await film_service.get_multiple_movies(
        page=params.page, size=params.size, sorting=sort, filtering=genre
    )
    if not isinstance(films, dict):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=films)
    films['results'] = [FilmsListApi(**film.model_dump()) for film in films['results']]
    return films


@router.get('/{film_id}', response_model=Film, description='Retrieve a film by its ID.')
async def film_detail(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    """
    Retrieve a film by its ID.
    Args:
        film_id (str): The ID of the film.
        film_service (FilmService): An instance of the FilmService.
    Returns:
        Film: The film information.
    Raises:
        HTTPException: If the film is not found.
    """
    film: MovieModel | None = await film_service.get_single_record(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return Film(**film.model_dump())
