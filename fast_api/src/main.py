"""
This module initializes a FastAPI application and includes routes for films.
It establishes a connection to Elasticsearch and Redis on application startup and closes the connection on shutdown.
"""
import logging
from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import films, persons, genres
from core.config import project_settings
from database import elastic, redis

logger = logging.getLogger('movies_fastapi')


@asynccontextmanager
async def lifespan(fast_api: FastAPI):
    """
    Event handler for application startup.
    Establishes a connection to Elasticsearch and Redis.
    """
    elastic.es = AsyncElasticsearch(hosts=project_settings.elastic.es_host)
    redis.redis = Redis(**project_settings.redis.model_dump())
    logger.info('Redis and elastic have been configured')

    yield

    await elastic.es.close()
    await redis.redis.close()


app = FastAPI(
    title=project_settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(persons.person_router, prefix='/api/v1/persons', tags=['persons'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])
