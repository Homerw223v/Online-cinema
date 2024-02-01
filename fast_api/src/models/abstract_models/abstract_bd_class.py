from abc import ABC, abstractmethod


class AbstractDataBase(ABC):
    """Abstract class for interacting with a database"""

    @abstractmethod
    async def get(self, pk: str, table_name: str) -> dict:
        """Get single record from database, using pk.
        :param pk: The ID of the record.
        :param table_name: The name of table in database, where record located.

        :return: A dictionary with information about record, if record exist.
        """
        pass

    @abstractmethod
    async def search(self, query: dict[str, str], page: int, size: int, table_name: str) -> dict:
        """Get multiple records from database.
        :param query: Query, that will be used in database searching process.
        :param page: Not quite page. This parameter will help you start retrieving records from a certain record.
        :param size: The size of returning records.
        :param table_name: The name of table in database, where records located.

        :return: A dictionary with information about records, if record exists.
        """
        pass
