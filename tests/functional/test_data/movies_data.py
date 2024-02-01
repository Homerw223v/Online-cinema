from uuid import uuid4
from random import randint, sample
from test_data.genres_data import es_genres_data
from faker import Faker

from test_data.es_data_prepare import ESDataPrepare

movies_endpoint = '/api/v1/films'


def create_random_person(count: int = 1) -> list[dict]:
    """
    Generate a list of random person names and person unique id.

    Args:
        count (int): The number of random person names to generate. Default is 1.

    Returns:
        list[dict]: A list of dictionaries containing the generated person names.
                    Each dictionary has 'id' and 'name' keys.
    """
    fake = Faker()
    fake_names = []
    for _ in range(count):
        fake_names.append(
            {'id': str(uuid4()),
             'name': fake.name()}
        )
    return fake_names


movies_data = [
    {
        "id": str(uuid4()),
        "title": f"Movie number {i}",
        "imdb_rating": float(randint(1, 10)),
        "description": f"Film description number {i}",
        "creation_date": None,
        "directors": create_random_person(),
        "actors": create_random_person(randint(2, 5)),
        "writers": create_random_person(),
        "genre": sample(es_genres_data, randint(2, 4))
    } for i in range(1, 101)
]
movies_data.append({'id': '154c628c-1432-40f9-8e30-c5c643d7c8a0',
                    'title': 'Unexpected Man',
                    'imdb_rating': 1.0,
                    'description': 'Film about unexpected man',
                    'creation_date': None,

                    'directors': [{'id': '75f64354-a7ee-4ced-b39e-b7257d941439',
                                   'name': 'Christopher Green'}],
                    'actors': [{'id': '556f090d-2c80-4c0a-8416-a490cd276a75', 'name': 'Erin Snow'},
                               {'id': '9c56a712-b336-4e1e-a678-7d333343a03c', 'name': 'Jacob Hood'},
                               {'id': '5237a109-1126-4bf1-a7aa-df00b367824f', 'name': 'James Kim'},
                               {'id': '03a24e38-a23d-48e2-8074-314c47ab741a', 'name': 'Christian Shaw'},
                               {'id': '102c5730-866e-41bc-b25b-8d35c40fbf3a', 'name': 'Joanna Lowe'}],
                    'writers': [{'id': 'f835e9a3-7974-4606-b85a-6570092f53b5',
                                 'name': 'Eric Kelley'}],
                    'genre': [{'id': '0c58cd08-dce3-466c-9607-c211bdf704a0', 'name': 'Short'},
                              {'id': '3ec14361-f7dd-402d-9ee1-83b6dfe86250', 'name': 'Comedy'},
                              {'id': '1fbe8de9-07a9-4511-8404-5ba373db8831', 'name': 'Reality-TV'},
                              {'id': '33715136-d115-4693-a10f-9d65e57933cb', 'name': 'Musical'}]})
movies_data.append({'id': '3b46f841-c1ee-4c36-9f73-2ee29808fdda',
                    'title': 'Unexpected Man 2',
                    'imdb_rating': 1.0,
                    'description': 'Film about 2 unexpected mans',
                    'creation_date': None,
                    'directors': [{'id': '9064baad-0fd0-4be1-bd7f-84f6c7f7cd68', 'name': 'Elizabeth Brown'}],
                    'actors': [{'id': '9556253a-b996-402f-b3a1-45c94df3d0c4', 'name': 'Joseph Holder'},
                               {'id': '4bc4aeb9-291a-4dbb-ad7a-ed0f34503ec3', 'name': 'Brittney Munoz'},
                               {'id': 'ef5a9278-d931-4380-9c16-0f99a4aeeec3', 'name': 'Carla Ford'}],
                    'writers': [{'id': 'a55bbe42-0a2b-442b-8433-69964e9142c6', 'name': 'Matthew Gentry'}],
                    'genre': [{'id': '2f54c051-d25f-4a04-bf55-691869d1984e', 'name': 'History'},
                              {'id': 'd86e403f-a76b-4619-aeb2-ee7eb5e7e87a', 'name': 'Animation'},
                              {'id': '884a824a-4c22-4f00-b66d-a0a8f9add69c', 'name': 'Western'}]}
                   )


class FilmsData(ESDataPrepare):
    raw_films = [{
        'actors': [{'id': '556f090d-2c80-4c0a-8416-a490cd276a75', 'name': 'User Name'}],
        'creation_date': None,
        'description': 'Film about unexpected man',
        'directors': [{'id': '75f64354-a7ee-4ced-b39e-b7257d941439', 'name': 'Christopher Green'}],
        'genre': [{'id': '0c58cd08-dce3-466c-9607-c211bdf704a0', 'name': 'Short'}],
        'id': '154c628c-1432-40f9-8e30-c5c643d7c8a0',
        'imdb_rating': 1.0,
        'title': 'Unexpected Man',
        'writers': [{'id': 'f835e9a3-7974-4606-b85a-6570092f53b5',
                     'name': 'Eric Kelley'}]
    },
        {
            'actors': [{'id': '556f090d-2c80-4c0a-8416-a490cd276a75', 'name': 'User Name'}],
            'creation_date': None,
            'description': 'Film about unexpected man 2',
            'directors': [{'id': '75f64354-a7ee-4ced-b39e-b7257d941439', 'name': 'Christopher Green'}],
            'genre': [{'id': '0c58cd08-dce3-466c-9607-c211bdf704a0', 'name': 'Short'}],
            'id': 'b4a0969e-1db6-432b-aeb0-8c0992b02df5',
            'imdb_rating': 1.0,
            'title': 'Unexpected Man 2',
            'writers': [{'id': 'f835e9a3-7974-4606-b85a-6570092f53b5',
                         'name': 'Eric Kelley'}]
        },
        {
            'actors': [{'id': '556f090d-2c80-4c0a-8416-a490cd276a75', 'name': 'User Name'}],
            'creation_date': None,
            'description': 'Film about men in black',
            'directors': [{'id': '75f64354-a7ee-4ced-b39e-b7257d941439', 'name': 'Christopher Green'}],
            'genre': [{'id': '0c58cd08-dce3-466c-9607-c211bdf704a0', 'name': 'Short'}],
            'id': 'e0f41502-2762-43be-8cde-c277b2327153',
            'imdb_rating': 1.0,
            'title': 'Men in black',
            'writers': [{'id': 'f835e9a3-7974-4606-b85a-6570092f53b5',
                         'name': 'Eric Kelley'}]
        }]

    @staticmethod
    def films():
        return FilmsData.prepare_for_es(FilmsData.raw_films, 'movies')

films = FilmsData.raw_films