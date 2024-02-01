import inspect
import logging
from time import sleep

from src.config import elastic
from src.config.elastic import BaseESIndexSettings
from src.elastic.es_loader import ElasticSearchLoader
from src.pg_extractor import PostgresExtractor


def get_es_index_settings(index_name: str) -> BaseESIndexSettings:
    """
    Return the instance of BaseESIndexSettings with prefix index_name.
    For example, if index_name == movies, MoviesIndexSettings('movies') will
    be returned.

    :param index_name: Name of ElasticSearch index.

    :return: instance of BaseESIndexSettings.
    """
    for name, obj in inspect.getmembers(elastic):
        if name == f"{index_name.capitalize()}IndexSettings":
            return obj(index_name)

    raise ValueError(f'Invalid index {index_name}.')


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s][Method:%(funcName)s]: %(message)s',
        datefmt='%d-%b-%y %H:%M:%S',
    )

    while True:
        for index_ in ['movies', 'genres', 'persons']:
            settings = get_es_index_settings(index_)
            es_loader = ElasticSearchLoader(settings)
            extractor = PostgresExtractor(settings)
            es_loader.load(extractor.get_es_data_generator())
        sleep(60)
