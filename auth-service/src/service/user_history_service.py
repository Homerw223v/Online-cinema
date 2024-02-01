from typing import Any

from db.login_history_db import LoginHistoryDB, get_user_history_db
from fastapi import Depends
from models.models import UserHistoryModel


class UserHistoryService:
    def __init__(self, user_history_db: LoginHistoryDB):
        self.user_history_db = user_history_db

    async def get_user_history(self, user_id: str, page: int, size: int) -> dict[str:Any]:
        """
        Retrieve user's login/logout history.

        :param user_id: The id of the user.
        :param page: Page number in pagination.
        :param size: Size of the page.

        :return: A list of user's login/logout history with pagination.
        """
        return await self.user_history_db.get_user_history(user_id, page, size)


def get_user_history_service(user_db=Depends(get_user_history_db)) -> UserHistoryService:
    return UserHistoryService(user_db)
