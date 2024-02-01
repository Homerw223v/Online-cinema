from typing import Optional
from uuid import UUID

from db.base_bd import AddDeleteMixin, RoleTable, User
from db.connection import get_session
from exceptions.db_error import (
    NoSuchRoleForUser,
    RoleDoesNotExists,
    UserDoesNotExists,
)
from fastapi import Depends
from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.exc import NoResultFound


class UserMethods(User, AddDeleteMixin):
    async def add(self, **kwargs):
        query = insert(User).values(kwargs)
        await self.session.execute(query)
        await self.session.commit()
        return_query = select(User).where(User.email == kwargs.get('email'))
        result = await self.session.scalar(return_query)
        return result

    async def delete(self, obj):
        await self.session.delete(obj)
        await self.session.commit()

    async def get_by_email(self, email: str) -> Optional['User']:
        """Get a user by email."""
        user = (
            await self.session.scalars(select(User).where(User.email == email))
        ).one_or_none()
        return user

    async def get_multiple_users(self) -> list['User']:
        """
        Retrieve all users from the database.

        :return: A list of UserDB or None if there are no users in database.
        """
        query = select(User)
        result = await self.session.scalars(query)
        return result.fetchall()

    async def get_user(self, user_id: str) -> 'User':
        """
        Retrieve a user by its id.

        :param user_id: ID of the user in the database.

        :return: A user from the database.
        """
        query = select(User).where(User.id == user_id)
        return await self.session.scalar(query)

    async def get_user_by_email(self, email: str) -> 'User':
        """
        Retrieve a user by it's email.

        :param email: Email (login) of the user in the database.

        :return: A user from the database.
        """
        query = select(User).where(User.email == email)
        return await self.session.scalar(query)

    async def update_user(self, user_id: str, new_info: dict) -> None:
        """
        Update an existing user in the database.

        :param user_id: ID of the user in the database.
        :param new_info: Information to be updated.
        """
        user = await self.get_user(user_id)
        if user:
            query = update(User).where(User.id == user_id).values(new_info)
            await self.session.execute(query)
            await self.session.commit()
        else:
            raise ValueError(
                f'Update of user with id {user_id} is not possible. No user with such id.'
            )

    async def delete_user(self, user_id: UUID) -> None:
        """
        Delete an existing user from the database.

        :param user_id: ID of the user in the database.
        """
        try:
            query = delete(User).where(User.id == user_id)
            await self.session.execute(query)
            await self.session.commit()
        except NoResultFound:
            raise ValueError(
                f'Deletion of user with id {user_id} is not possible. No user with such id.'
            )

    async def assign_role_to_user(self, user_id: str, role: str) -> None:
        """
        Assigns a new role to a user.

        Args:
            user_id (str): The ID of the user.
            role (str): The name of the role to be assigned.

        Raises:
            RoleDoesNotExists: If the specified role does not exist.
        """
        user_query = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.roles))
        )
        user: User = await self.session.scalar(user_query)
        role_query = select(RoleTable).where(RoleTable.name == role)
        role: RoleTable = await self.session.scalar(role_query)
        if not role:
            raise RoleDoesNotExists
        if not user:
            raise UserDoesNotExists
        user.roles.append(role)
        await self.session.commit()

    async def remove_role_from_user(self, user_id: str, role: str) -> None:
        """
        Removes a role from a user.

        Args:
            user_id (str): The ID of the user.
            role (str): The name of the role to be removed.

        Raises:
            NoSuchRoleForUser: If the specified role is not assigned to the user.
        """
        try:
            user_query = (
                select(User)
                .where(User.id == user_id)
                .options(selectinload(User.roles))
            )
            user: User = await self.session.scalar(user_query)
            role_query = select(RoleTable).where(RoleTable.name == role)
            role: RoleTable = await self.session.scalar(role_query)
            user.roles.remove(role)
        except ValueError:
            raise NoSuchRoleForUser
        else:
            await self.session.commit()

    async def get_all_user_roles(self, user_id: str) -> User:
        """
        Retrieves all roles of a user.

        Args:
            user_id (str): The ID of the user.

        Raises:
            UserDoesNotExists: If the specified user does not exist.

        Returns:
            User: The user object with all roles loaded.
        """
        query = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.roles))
        )
        user: User = await self.session.scalar(query)
        if user:
            return user
        raise UserDoesNotExists


async def get_user_db(sessions=Depends(get_session)):
    return UserMethods(sessions)
