from elasticsearch import AsyncElasticsearch
from models.abstract_models.abstract_bd_class import AbstractDataBase


class ElasticSearchDatabase(AbstractDataBase):
    def __init__(self, elastic_instance: AsyncElasticsearch):
        self.elastic = elastic_instance

    async def get(self, pk: str, table_name: str) -> dict:
        return await self.elastic.get(index=table_name, id=pk)

    async def search(self, query: dict[str, str], page: int, size: int, table_name: str) -> dict:
        return await self.elastic.search(
            index=table_name,
            body=query,
            size=size,
            from_=(page - 1) * size,
        )
