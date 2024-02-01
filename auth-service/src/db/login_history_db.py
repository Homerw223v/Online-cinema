from math import ceil
from typing import Any
from uuid import UUID

from db.base_bd import LoginHistoryTable, RefreshSession
from db.connection import get_session
from fastapi import Depends
from sqlalchemy import select


class LoginHistoryDB:
    def __init__(self, session):
        self.session = session

    async def get_user_history(
        self, user_id: str, page: int, size: int
    ) -> dict[str:Any]:
        """
        Retrieve user login/logout history from the database.

        :param user_id: ID of the user in the database.
        :param page: Page number in pagination.
        :param size: Size of the page.

        :return: list of login/logout history.
        """
        query = (
            select(
                RefreshSession.finger_print,
                LoginHistoryTable.time,
                LoginHistoryTable.action,
            )
            .join(LoginHistoryTable)
            .where(RefreshSession.user_id == UUID(user_id))
        )
        result = await self.session.execute(query)
        # TODO: get number of rows from result
        result = list(result.all())

        if (pages_count := ceil(len(result) / size)) < page:
            raise ValueError(
                f'Page number exceeds maximum possible page, which is {pages_count}.'
            )

        pagination = {
            'total': len(result),
            'page': page,
            'size': size,
            'total_pages': pages_count,
            'results': [row._mapping for row in result],
        }

        return pagination


async def get_user_history_db(sessions=Depends(get_session)):
    return LoginHistoryDB(sessions)
