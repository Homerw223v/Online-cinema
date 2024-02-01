class ESDataPrepare:

    @staticmethod
    def prepare_for_es(es_data: [dict], index_name: str = 'persons'):
        bulk_query: list[dict] = []
        for row in es_data:
            data = {'_index': index_name, '_id': row['id']}
            data.update({'_source': row})
            bulk_query.append(data)

        return bulk_query
