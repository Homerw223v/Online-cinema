import json

from pydantic_settings import BaseSettings
from pydantic import create_model


class BaseTestSettings(BaseSettings):
    es_host: str
    redis_host: str
    redis_port: str
    service_url: str

    @classmethod
    def get_index_mapping(cls, index_name: str) -> dict:
        """
        Return ElasticSearch index mappings.

        :param index_name: Name of ES index.
        """
        index_mapping_path = f'assets/es_{index_name}_schema.json'
        with open(index_mapping_path, 'r') as fp:
            return json.load(fp)['mappings']

    @classmethod
    def get_settings(cls) -> None:
        """
        Return ElasticSearch index settings.
        """
        with open('assets/settings.json', 'r') as fp:
            return json.load(fp)['settings']


def create_index_test_settings(index_name: str) -> BaseTestSettings:
    """
    Create instance of BaseTestSettings with additional fields for index index_name.

    :param index_name: Name of ES index.

    :return: Instance of BaseTestSettings.
    """
    fields = {
        'es_index_name': (str, index_name),
        'es_index_mapping': (dict, BaseTestSettings.get_index_mapping(index_name)),
        'es_index_settings': (dict, BaseTestSettings.get_settings()),
    }
    index_test_settings = create_model(f'{index_name.capitalize()}TestSettings', **fields, __base__=BaseTestSettings)

    return index_test_settings()



settings = BaseTestSettings()

base_test_settings = BaseTestSettings()

genres_test_settings = create_index_test_settings('genres')
movies_test_settings = create_index_test_settings('movies')
