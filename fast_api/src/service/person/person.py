import logging
from functools import lru_cache
from typing import Any
from uuid import UUID

from core.config import project_settings
from database.elastic import get_database
from database.redis import get_cache
from fastapi import Depends
from models.abstract_models.abstract_bd_class import AbstractDataBase
from models.abstract_models.abstract_cache import AbstractCache
from models.models import PersonAPI, PersonFilmsAPI
from redis.asyncio import Redis
from service.abstract_base_classes import AbstractBaseQueryBuilder, BaseService

logger = logging.getLogger('movies_fastapi')


class PersonQueryBuilder(AbstractBaseQueryBuilder):
    """Build queries for Elasticsearch persons index requests."""

    @staticmethod
    def get_person_films_body(person_id: UUID) -> dict:
        """Elasticsearch query for retrieving films where person appears"""
        return {
            'query': {
                'bool': {
                    'should': [
                        {'nested': {'path': 'actors', 'query': {'match': {'actors.id': f'{person_id}'}}}},
                        {'nested': {'path': 'writers', 'query': {'match': {'writers.id': f'{person_id}'}}}},
                        {'nested': {'path': 'directors', 'query': {'match': {'directors.id': f'{person_id}'}}}},
                    ]
                }
            }
        }

    def _get_keyword_query_part(self) -> dict[str:Any] | None:
        """
        Return keyword query part.
        """
        if self.keyword:
            return {"match": {"full_name": {"query": self.keyword, "fuzziness": "AUTO"}}}

    def _get_sorting_query_part(self) -> dict[str:Any] | None:
        """
        Return sorting query part.
        """
        if self.sorting:
            if self.sorting.startswith('-'):
                return {f'{self.sorting[1:]}.raw': {'order': 'desc'}}
            else:
                return {f'{self.sorting}.raw': {'order': 'asc'}}

    def _get_filtering_query_part(self) -> dict[str:Any] | None:
        """
        Return filtering query part.
        """
        if self.filtering:
            return {"prefix": {"full_name": {"value": self.filtering}}}


class PersonService(BaseService):
    """Class provides methods to interact with a data in ElasticSearch"""

    async def get_multiple_persons(
        self,
        keyword: str = '',
        page: int = 1,
        size: int = 10,
        sorting: str = '',
        filtering: str = '',
    ) -> dict[str, int | list[PersonAPI]] | str:
        """
        Return multiple persons according to query, page, size, sorting, and filtering parameters with pagination.

        :param keyword: Keyword for data extraction.
        :param page: The page number.
        :param size: The number of films to retrieve per page.
        :param sorting: The sorting order for the records. Defaults to None.
        :param filtering: Prefix by which records should be sorted.

        :return: A dict containing records information according to request with pagination information or string with error.
        """
        query = PersonQueryBuilder(keyword, sorting, filtering).get_multiple_records_query()
        return await self._get_multiple_records(query, page, size,
                                                index_name=project_settings.elastic.es_person_index,
                                                keyword=keyword)

    async def get_persons_films(self, person_id: UUID, page: int = 1, size: int = 10):
        """Retrieve person's films using person ID"""
        query = PersonQueryBuilder.get_person_films_body(person_id)
        return await self._get_multiple_records(
            query,
            page,
            size,
            model=PersonFilmsAPI,
            index_name=project_settings.elastic.es_movies_index,
            person_id=person_id,
        )


@lru_cache()
def get_persons_service(
    db: AbstractDataBase = Depends(get_database), cache: AbstractCache = Depends(get_cache)
) -> PersonService:
    """
    Factory function to get an instance of the FilmService.

    Args:
        db (AbstractDataBase): An instance of the AbstractDataBase class.
        cache (Redis):An instance of the AbstractCache class.

    Returns:
        FilmService: An instance of the FilmService.
    """
    return PersonService(db, cache, PersonAPI, project_settings.elastic.es_person_index)
