from abc import ABC, abstractmethod
from typing import Any


class AbstractBaseQueryBuilder(ABC):
    """Provide interface and methods for building ElasticSearch queries."""

    def __init__(self, keyword: str, sorting: str, filtering: str) -> None:
        """
        Constructor.

        :param keyword: The keywords for searching records.
        :param sorting: The sorting order for the records.
        :param filtering: Prefix by which records should be selected.
        """
        self.keyword = keyword
        self.sorting = sorting
        self.filtering = filtering

    def get_multiple_records_query(self) -> dict[str:Any]:
        """
        Return query for multiple records endpoint.
        """
        keyword = self._get_keyword_query_part()
        filtering = self._get_filtering_query_part()
        sorting = self._get_sorting_query_part()

        body = {}

        if keyword:
            body["query"] = keyword

        if filtering:
            body["query"] = filtering

        if sorting:
            body["sort"] = sorting

        return body if body else {"query": {"match_all": {}}}

    @abstractmethod
    def _get_keyword_query_part(self) -> dict[str:Any] | None:
        """
        Return keyword query part.
        """
        pass

    @abstractmethod
    def _get_sorting_query_part(self) -> dict[str:Any] | None:
        """
        Return sorting query part.
        """
        pass

    @abstractmethod
    def _get_filtering_query_part(self) -> dict[str:Any] | None:
        """
        Return filtering query part.
        """
        pass
