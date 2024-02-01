from .base import BaseESIndexSettings
from src.query.query_builder import QueryBuilderTables
from src.query.query_executor import QueryExecutor


class PersonsIndexSettings(BaseESIndexSettings):
    def _get_data_extraction_query(self):
        query = """
                with temp_table as (SELECT
                    p.id as p_id,
                    p.full_name as p_full_name,
                    fw.id as fw_id,
                    ARRAY_AGG(DISTINCT pfw.role) as roles,
                    GREATEST(p.updated_at, fw.updated_at) as updated_at
                FROM content.person p
                LEFT JOIN content.person_film_work pfw ON pfw.person_id = p.id
                LEFT JOIN content.film_work fw ON fw.id = pfw.film_work_id
                WHERE p.id IN ('{}')
                GROUP BY p.id, fw.id)

                SELECT
                    p_id as id,
                    p_full_name as full_name,
                    ARRAY_AGG(jsonb_build_object('id', fw_id, 'role', roles)) as films,
                    MAX(updated_at) as modified
                FROM temp_table
                GROUP BY p_id, p_full_name
                ORDER BY MAX(updated_at) ASC;
                """
        return query

    def get_modified_ids(self, cursor, break_point):
        return set(QueryExecutor.get_modified_records_ids(QueryBuilderTables.PERSON, cursor, break_point))
