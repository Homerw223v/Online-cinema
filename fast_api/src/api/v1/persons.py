from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from models.models import PersonAPI, PersonFilmsAPI
from models.params_models.PaginatedParams import PaginatedParams
from service.person import PersonService, get_persons_service

person_router = APIRouter()


@person_router.get(
    '/search',
    response_model=dict[str, list[PersonAPI] | int],
    description='Search persons using name',
)
async def search_persons(
    query: str = Query('', description='Person name'),
    params: PaginatedParams = Depends(),
    sort: str = Query(None, description='Sorting field for people', example='full_name:desc'),
    service: PersonService = Depends(get_persons_service),
) -> dict[str, list[PersonAPI] | int | str]:
    """
    Retrieve all films with pagination.
    Args:
        params (PaginatedParams): Class with page and size parameters.
        sort (str | None): The sorting order for the persons. Defaults to _source.
        query (str): The filter parameter for persons name.
        service (FilmService): An instance of the PersonService.
    Returns:
        A list of persons.
    """
    params.validate()
    persons = await service.get_multiple_persons(keyword=query, page=params.page, size=params.size, sorting=sort)
    if isinstance(persons, str):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=persons)
    return persons


@person_router.get('/{person_id}', description='Get information about person')
async def get_person_by_id(
    person_id: str = Path(description='Person uuid'), service: PersonService = Depends(get_persons_service)
) -> PersonAPI | None:
    """
    Retrieve person by ID
    Args:
        person_id (uuid): Person ID.
        service (FilmService): An instance of the PersonService.
    Returns:
        Person.
    """
    person: PersonAPI | None = await service.get_single_record(person_id)

    if person is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Person not found')

    return person


@person_router.get(
    '/{person_id}/films',
    response_model=dict[str, list[PersonFilmsAPI] | int],
    description='Get all the films in which this person participated',
)
async def get_person_films(
    person_id: UUID = Path(description='Person uuid'),
    params: PaginatedParams = Depends(),
    service: PersonService = Depends(get_persons_service),
) -> dict[str, list[PersonFilmsAPI] | int] | None:
    """
    Retrieve person films
    Args:
        person_id (uuid): Person ID.
        params (PaginatedParams): Class with page and size parameters.
        service (FilmService): An instance of the PersonService.
    Returns:
        List of films
    """
    params.validate()
    films = await service.get_persons_films(person_id, page=params.page, size=params.size)

    if films is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='Bad request')
    return films
