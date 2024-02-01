import uuid

persons_endpoint = '/api/v1/persons'

person_1 = {
    'id': '556f090d-2c80-4c0a-8416-a490cd276a75',
    'full_name': 'User Name',
    'films': [
        {
            'id': '556f090d-2c80-4c0a-8416-a490cd276a75',
            'role': [
                'actor'
            ]
        }
    ]
}


class PersonsData:

    @staticmethod
    def _prepare_for_es(es_data: [dict], index_name: str = 'persons'):
        bulk_query: list[dict] = []
        for row in es_data:
            data = {'_index': index_name, '_id': row['id']}
            data.update({'_source': row})
            bulk_query.append(data)

        return bulk_query

    @staticmethod
    def one_person() -> list[dict]:
        es_data = [person_1]
        return PersonsData._prepare_for_es(es_data)

    @staticmethod
    def persons_40_alex_10_poline() -> list[dict]:
        names = ['Alex Foo', 'Polina Bar']
        es_data = [
            {
                'id': uuid.uuid4(),
                'full_name': names[0],
                'films': [
                    {
                        'id': uuid.uuid4(),
                        'role': [
                            'actor'
                        ]
                    }
                ]
            } for _ in range(20)
        ]

        es_data.extend(
            [
                {
                    'id': uuid.uuid4(),
                    'full_name': names[1],
                    'films': [
                        {
                            'id': uuid.uuid4(),
                            'role': [
                                'actor'
                            ]
                        }
                    ]
                } for _ in range(10)
            ]
        )

        return PersonsData._prepare_for_es(es_data)
