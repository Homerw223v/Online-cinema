from functools import lru_cache
from typing import Any

from core.config import project_settings
from database.elastic import get_database
from database.redis import get_cache
from fastapi import Depends
from models.abstract_models.abstract_bd_class import AbstractDataBase
from models.abstract_models.abstract_cache import AbstractCache
from models.models import GenreModel
from redis.asyncio import Redis
from service.abstract_base_classes import AbstractBaseQueryBuilder, BaseService


class GenreQueryBuilder(AbstractBaseQueryBuilder):
    """Build queries for Elasticsearch genres index requests."""

    def _get_keyword_query_part(self) -> dict[str:Any] | None:
        """
        Return keyword query part.
        """
        if self.keyword:
            return {"match": {"title": {"query": self.keyword, "fuzziness": "AUTO"}}}

    def _get_sorting_query_part(self) -> dict[str:Any] | None:
        """
        Return sorting query part.
        """
        if self.sorting:
            if self.sorting.startswith('-'):
                return {self.sorting[1:]: {"order": "desc"}}
            else:
                return {self.sorting: {"order": "asc"}}

    def _get_filtering_query_part(self) -> dict[str:Any] | None:
        """
        Return filtering query part.
        """
        if self.filtering:
            return {"prefix": {"name": {"value": self.filtering}}}


class GenreService(BaseService):
    """GenreService class provides methods to interact with a data in ElasticSearch"""

    async def get_multiple_genres(
        self,
        keyword: str = '',
        page: int = 1,
        size: int = 10,
        sorting: str = '',
        filtering: str = '',
    ) -> dict[str, int | list[GenreModel]] | str:
        """
        Return multiple genres according to query, page, size, sorting, and filtering parameters with pagination.

        :param keyword: Keyword for data extraction.
        :param page: The page number.
        :param size: The number of films to retrieve per page.
        :param sorting: The sorting order for the records. Defaults to None.
        :param filtering: Prefix by which records should be sorted.

        :return: A dict containing records information according to request with pagination information or string with error.
        """
        query = GenreQueryBuilder(keyword, sorting, filtering).get_multiple_records_query()
        return await self._get_multiple_records(query, page, size)


@lru_cache()
def get_genre_service(
    db: AbstractDataBase = Depends(get_database), redis: AbstractCache = Depends(get_cache)
) -> GenreService:
    """
    Factory function to get an instance of the GenreService.

    Args:
        db (AbstractDataBase): An instance of the AsyncElasticsearch client.
        redis (Redis): An instance of the Redis client.

    Returns:
        GenreService: An instance of the GenreService.
    """
    return GenreService(db, redis, GenreModel, project_settings.elastic.es_genres_index)
