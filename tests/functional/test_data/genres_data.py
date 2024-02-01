import uuid
import os
from http import HTTPStatus

TESTING_UUID = os.environ.get('TESTING_UUID')

genres_endpoint = '/api/v1/genres/'

genres_name = [
    'Action',
    'Adventure',
    'Animation',
    'Biography',
    'Comedy',
    'Crime',
    'Documentary',
    'Drama',
    'Family',
    'Fantasy',
    'Game-Show',
    'History',
    'Horror',
    'Music',
    'Musical',
    'Mystery',
    'News',
    'Reality-TV',
    'Romance',
    'Sci-Fi',
    'Short',
    'Sport',
    'Talk-Show',
    'Thriller',
    'War',
    'Western',
]

es_genres_data = [dict(id=TESTING_UUID, name=genres_name[0])] + [
    dict(id=str(uuid.uuid4()), name=name) for name in genres_name[1:]
]
