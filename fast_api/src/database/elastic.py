"""This module provides functions related to Elasticsearch integration."""
from database.elastic_database.elastic_db import ElasticSearchDatabase
from elasticsearch import AsyncElasticsearch
from models.abstract_models.abstract_bd_class import AbstractDataBase

es: AsyncElasticsearch | None = None


async def get_database() -> AbstractDataBase:
    """
    Returns:
          ElasticSearchDatabase: Class for working with ElasticSearch database.
    """
    return ElasticSearchDatabase(es)
