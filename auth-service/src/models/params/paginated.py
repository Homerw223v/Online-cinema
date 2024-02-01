from typing import Annotated

from fastapi import Query


class PaginatedParams:
    def __init__(
        self,
        page: Annotated[int, Query(description='Page number', ge=1)] = 1,
        size: Annotated[int, Query(description='Number of records per page', ge=1)] = 10,
    ):
        self.page = page
        self.size = size


def get_paginated_params(page: int, size: int) -> PaginatedParams:
    """
    Factory function to get an instance of the PaginatedParams.

    :param page: The page number.
    :param size: The number of users to retrieve per page.

    :return: Instance of PaginatedParams
    """
    return PaginatedParams(page, size)
