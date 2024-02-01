from http import HTTPStatus

from fastapi import HTTPException, Query


class PaginatedParams:
    def __init__(self,
                 page: int = Query(1, description='Page number'),
                 size: int = Query(10, description='Number of records per page')):
        self.page = page
        self.size = size

    def validate(self):
        if self.page < 1:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f'Page number should be positive, {self.page} instead.',
            )
        if self.size < 1:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f'Size of the page should be positive, {self.size} instead.',
            )
