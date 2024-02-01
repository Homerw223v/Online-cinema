from db.base_bd import User
from db.user_db import UserMethods, get_user_db
from fastapi import Depends


class UserService:
    def __init__(self, user_db: UserMethods):
        self.user_db = user_db

    async def get_multiple_users(self) -> list[User]:
        """
        Retrieve a subset of users with pagination.

        :return: A list of users with pagination.
        """
        return await self.user_db.get_multiple_users()

    async def get_user(self, user_id: str) -> User:
        """
        Retrieve user by its id.

        :param user_id: The id of the user.

        :return: The user information.
        """
        return await self.user_db.get_user(user_id)

    async def get_user_by_email(self, email: str) -> User:
        """
        Retrieve user by its email.

        :param email: The id of the user.

        :return: The user information.
        """
        return await self.user_db.get_user_by_email(email)

    async def update_user(self, user_id: str, body: dict) -> None:
        """
        Update user information.

        :param user_id: The id of the user.
        :param body: The body with the data to be updated for the user.
        """
        await self.user_db.update_user(user_id, body)

    async def delete_user(self, user_id: str) -> None:
        """
        Remove user by its id from database.

        :param user_id: The id of the user.
        """
        await self.delete_user(user_id)


def get_user_service(user_db=Depends(get_user_db)) -> UserService:
    return UserService(user_db)
