from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from models.models import GenreModel
from models.params_models.PaginatedParams import PaginatedParams
from service.genre import GenreService, get_genre_service

router = APIRouter()


@router.get('/{genre_id}', response_model=GenreModel, description='Retrieve a genre by its ID.')
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> GenreModel:
    """
    Retrieve a genre by its ID.
    Args:
        genre_id: The ID of the genre.
        genre_service: An instance of the GenreService.
    Returns:
        The genre information.
    Raises:
        HTTPException: If the genre is not found.
    """
    genre: GenreModel | None = await genre_service.get_single_record(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return genre


@router.get(
    '/',
    response_model=dict[str, list[GenreModel] | int | str],
    description='Retrieve all genres with pagination.',
)
async def all_genres(
    params: PaginatedParams = Depends(),
    sort: str = Query(
        '',
        description='Sorting field for genres.(Example: name sort from top to bottom or -name from bottom to top)',
    ),
    filt: str = Query(
        '', description='Filtering field for genre.(Example: A will return all genres which starts from letter A.)'
    ),
    genre_service: GenreService = Depends(get_genre_service),
) -> dict[str, list[GenreModel] | int | str]:
    """
    Retrieve all genres with pagination.
    Args:
        params (PaginatedParams): Class with page and size parameters.
        sort: The sorting order for the films. Defaults to None.
        filt: Prefix by which genres should be sorted.
        genre_service: An instance of the GenreService.
    Returns:
        dict[str, list[Film] | int | str]: A list of genres with pagination.
    Raises:
        HTTPException: If the page number is incorrect or genres are not found.
    """
    params.validate()
    genres = await genre_service.get_multiple_genres(page=params.page, size=params.size, sorting=sort, filtering=filt)
    if isinstance(genres, str):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=genres)
    return genres
