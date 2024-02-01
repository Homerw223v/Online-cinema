from db.base_bd import RoleTable
from db.connection import get_session
from exceptions.db_error import (
    RoleAlreadyExists,
    RoleDoesNotExists,
    RolesDoesNotExists,
)
from fastapi import Depends
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, NoResultFound


class RoleMethods:
    def __init__(self, session):
        self.session = session

    async def get_all_roles(self) -> list['RoleMethods'] | None:
        """
        Retrieve all roles from the database.

        Returns:
            list[RoleBDModel] | None: A list of RoleBDModel, representing each role,
                or None if there are no roles in database.

        Raise:
            RolesDoesNotExists: If no roles in database.
        """
        execute_query = select(RoleTable)
        request = await self.session.scalars(execute_query)
        if result := request.fetchall():
            return result
        raise RolesDoesNotExists

    async def get_single_role(self, role_name: str) -> 'RoleMethods':
        """
        Retrieve a single role from the database based on the role name.

        Args:
            role_name (str): The name of the role to retrieve.

        Returns:
            RoleBDModel: Return RoleBDModel, representing existing role

        Raise:
            RoleDoesNotExists: If role does not exist.
        """
        execute_query = select(RoleTable).where(RoleTable.name == role_name)
        role: RoleTable = await self.session.scalar(execute_query)
        if not role:
            raise RoleDoesNotExists
        return role

    async def create_role(self, role: dict) -> None:
        """
        Create a new role in the database.

        Inserts a new role into the database using the name and description
        attributes of the current instance.

        Args:
            role (dict): Dictionary with Role attribute.
        Raise:
            RoleAlreadyExists: If role already exists.
        """
        try:
            insert_query = insert(RoleTable).values(role)
            await self.session.execute(insert_query)
            await self.session.commit()
        except IntegrityError:
            raise RoleAlreadyExists

    async def update_role(self, role_name: str, new_info: dict) -> None:
        """
        Update an existing role in the database.

        Args:
            role_name (str): The name of the role to update.
            new_info (dict): A dictionary containing the updated attribute values.

        Returns:
            RoleBDModel: Return RoleBDModel, representing updated role.

        Raise:
            RoleDoesNotExists: If given role does not exist.
        """
        try:
            insert_query = (
                update(RoleTable)
                .where(RoleTable.name == role_name)
                .values(new_info)
            )
            await self.session.execute(insert_query)
            await self.session.commit()
        except NoResultFound:
            raise RoleDoesNotExists

    async def delete_role(self, role: str) -> None:
        """
        Delete a role from the database.

        Args:
            role (str): The name of the role to delete.

        Returns:
            None
        """
        execute_query = delete(RoleTable).where(RoleTable.name == role)
        result = await self.session.execute(execute_query)
        if result.rowcount:
            await self.session.commit()
            return
        raise RoleDoesNotExists


async def get_role_db(sessions=Depends(get_session)):
    return RoleMethods(sessions)
