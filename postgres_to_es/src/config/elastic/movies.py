from .base import BaseESIndexSettings
from src.query.query_builder import QueryBuilderTables
from src.query.query_executor import QueryExecutor


class MoviesIndexSettings(BaseESIndexSettings):
    def _get_data_extraction_query(self):
        query = """
                SELECT
                    fw.id AS id,
                    fw.title,
                    fw.rating AS imdb_rating,
                    fw.description,
                    fw.creation_date as creation_date,
                    ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) FILTER (WHERE pfw.role = 'director') AS directors,
                    ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) FILTER (WHERE pfw.role = 'actor') AS actors,
                    ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) FILTER (WHERE pfw.role = 'writer') AS writers,
                    ARRAY_AGG(DISTINCT jsonb_build_object('id', g.id, 'name', g.name)) AS genre,
                    GREATEST(fw.updated_at, MAX(p.updated_at), MAX(g.updated_at)) as modified
                FROM content.film_work fw
                LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
                LEFT JOIN content.person p ON p.id = pfw.person_id
                LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
                LEFT JOIN content.genre g ON g.id = gfw.genre_id
                WHERE fw.id IN ('{}')
                GROUP BY fw.id
                ORDER BY GREATEST(fw.updated_at, MAX(p.updated_at), MAX(g.updated_at)) ASC;
                """
        return query

    def get_modified_ids(self, cursor, break_point):
        result = set()
        return result.union(
            QueryExecutor.get_modified_records_ids(QueryBuilderTables.FILM_WORK, cursor, break_point),
            QueryExecutor.get_modified_m2m_records(QueryBuilderTables.PERSON, cursor, break_point),
            QueryExecutor.get_modified_m2m_records(QueryBuilderTables.GENRE, cursor, break_point),
        )
