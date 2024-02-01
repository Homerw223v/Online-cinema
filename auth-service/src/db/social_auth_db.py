from db.base_bd import SocialAuthTable, User
from db.connection import get_session
from fastapi import Depends
from sqlalchemy import insert, select

from schemas.social_auth import SocialOAuthUserModel


class SocialAuthMethods:
    def __init__(self, session):
        self.session = session

    async def get_row_by_social_id(
        self, social_id: str, social_name: str
    ) -> SocialAuthTable:
        """
        Retrieve a row from the SocialAuthTable based on the social ID.

        Args:
            social_id (str): The social ID.
            social_name (str): Name of the social provider.

        Returns:
            SocialAuthTable: The row from the SocialAuthTable.
        """
        query = select(SocialAuthTable).where(
            SocialAuthTable.social_id == social_id,
            SocialAuthTable.social_name == social_name,
        )
        return await self.session.scalar(query)

    async def add_social_auth_user(
        self, social_user: SocialOAuthUserModel, user: User
    ) -> None:
        """
        Add a social authentication user to the SocialAuthTable.

        Args:
            social_user (SocialOAuthUserModel): The social user information.
            user (User): The user object.

        Returns:
            None
        """
        query = insert(SocialAuthTable).values(
            social_id=social_user.social_id,
            social_name=social_user.social_name,
            user_id=user.id,
            # Как сюда вставить пользователя объект user=user?
        )
        await self.session.execute(query)


async def get_social_auth_db(sessions=Depends(get_session)):
    return SocialAuthMethods(sessions)
