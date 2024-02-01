import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk


from settings import BaseTestSettings


@pytest_asyncio.fixture()
async def es_write_data(es_client: AsyncElasticsearch):
    """
    Create indexes and put data in ES for Tests

    """
    async def inner(bulk_query: list[dict], index_name: str, settings: BaseTestSettings):
        if await es_client.indices.exists(index=index_name):
            await es_client.indices.delete(index=index_name)
        await es_client.indices.create(index=index_name,
                                       settings=settings.get_settings(),
                                       mappings=settings.get_index_mapping(index_name))

        updated, errors = await async_bulk(client=es_client, actions=bulk_query, refresh=True)
        if errors:
            raise Exception(errors)

    yield inner



