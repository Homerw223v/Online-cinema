from .base import BaseESIndexSettings
from src.query.query_builder import QueryBuilderTables
from src.query.query_executor import QueryExecutor


class GenresIndexSettings(BaseESIndexSettings):
    def _get_data_extraction_query(self):
        query = """
                SELECT id, name, updated_at as modified FROM content.genre WHERE id IN ('{}');
                """
        return query

    def get_modified_ids(self, cursor, break_point):
        return set(QueryExecutor.get_modified_records_ids(QueryBuilderTables.GENRE, cursor, break_point))
