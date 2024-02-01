import json
import logging
from math import ceil
from typing import Any, Type

import backoff
import pydantic
from core.config import on_give_up
from elasticsearch import ConnectionError as ElasticError
from elasticsearch import NotFoundError
from models.abstract_models.abstract_bd_class import AbstractDataBase
from models.abstract_models.abstract_cache import AbstractCache
from models.models import AbstractModel
from redis.asyncio import ConnectionError as RedisError

logger = logging.getLogger('movies_fastapi')


class BaseService:
    """Base class for services in API."""

    def __init__(self, db: AbstractDataBase, cache: AbstractCache, model: Type[AbstractModel], index_name: str):
        """
        Constructor.

        :param db: An instance of the AbstractDataBase class.
        :param cache: An instance of the AbstractCache class.
        :param model: Subclass of Abstract model for data validation.
        :param index_name: Name of elastic search index.
        """
        self.db = db
        self.cache = cache
        self.model = model
        self.index_name = index_name

    @backoff.on_exception(backoff.expo, (RedisError, ElasticError), max_time=15, on_giveup=on_give_up)
    async def _get_multiple_records(
            self,
            query: dict[str:Any],
            page: int = 1,
            size: int = 10,
            model: Type[AbstractModel] = None,
            index_name: str = None,
            keyword: str | None = None,
            **kwargs,
    ) -> dict[str, int | list[AbstractModel]] | str:
        """
        Return multiple records according to query, page, and size parameters with pagination. Model and index_name are optional
        arguments which are required in some cases where self.model and self.index_name is not suitable.

        :param query: Database query for data extraction.
        :param page: The page number.
        :param size: The number of films to retrieve per page.
        :param model: Subclass of Abstract model for data validation.
        :param index_name: Name of table in database.

        :return: A dict containing records information according to request with pagination information or string with error.
        """

        # Check and return from cache
        index = index_name or self.index_name
        cache_key = f'index={index}_query={keyword or None}_page={page}_size={size}_sort={query.get("sort")}'

        person_id = kwargs.get('person_id')
        if person_id is not None:
            cache_key += f'_person_id={person_id}'

        logger.info('Cache key created = %s', cache_key)
        cached = await self.cache.get(cache_key)

        if cached is not None:
            logger.info('Cache with key %s ==== %s', cache_key, cached)
            cached_records = json.loads(cached)
            return self._get_paginate_result(cached_records, size, page, model)

        try:
            records: dict = await self.db.search(query, page, size, index_name)
            paginate_result = self._get_paginate_result(records, size, page, model)
        except ValueError as err:
            return str(err)

        await self.cache.set(cache_key, json.dumps(records))
        logger.info('SET cache key --> %s', cache_key)
        logger.info('SET cache --> %s', json.dumps(records))

        return paginate_result

    def _get_paginate_result(self, data: dict[str:Any], size, page, model: Type[AbstractModel] = None):
        """
        Return data in paginated format.

        :param data: Data collected from Database.
        :param page: The page number.
        :param size: The number of records to retrieve per page.
        :param model: Subclass of Abstract model for data validation.

        :return: A dict containing records information according to request with pagination information
        """
        if (pages_count := ceil(data['hits']['total']['value'] / size)) < page:
            raise ValueError(f'Page number exceeds maximum possible page, which is {pages_count}.')

        model = model if model else self.model
        pagination = {
            'total': data['hits']['total']['value'],
            'page': page,
            'size': len(data['hits']['hits']),
            'total_pages': pages_count,
            'results': [model(**record['_source']) for record in data['hits']['hits']],
        }

        return pagination

    @backoff.on_exception(backoff.expo, (RedisError, ElasticError), max_time=15, on_giveup=on_give_up)
    async def get_single_record(self, record_id: str) -> AbstractModel | None:
        """
        Retrieve a record by its ID from Database.

        :param record_id: The ID of the record.

        :return: A Model object representing the table in database if found, None otherwise.
        """

        # Check and return from cache
        cached = await self.cache.get(record_id)
        if cached is not None:
            try:
                return self.model.model_validate_json(cached)
            except pydantic.ValidationError as e:
                logger.exception('Cache validation error', exc_info=e)

        try:
            record: dict = await self.db.get(record_id, self.index_name)
        except NotFoundError:
            return None
        record_model = self.model(**record['_source'])
        await self.cache.set(record_id, record_model.model_dump_json())
        return record_model
