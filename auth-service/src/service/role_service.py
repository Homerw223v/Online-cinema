from functools import lru_cache

from db.role_db import RoleMethods, get_role_db
from db.user_db import UserMethods, get_user_db
# from db.user_role_db import UserRoleMethods, get_user_role_db
from fastapi import Depends
from schemas.user import UserRoles


class RoleService:
    def __init__(self, role_db: RoleMethods, user_db: UserMethods):
        """
        Initializes a RoleService instance.

        Args:
            role_db (RoleBDModel): The database model for roles.
            # user_role_db (UserRoleBD): The database model for user roles.
        """
        self.role_db = role_db
        self.user_db = user_db

    async def all_roles(self) -> list[RoleMethods] | None:
        """
        Retrieves all roles.

        Returns:
            list[RoleBDModel] | None: A list of roles or None if no roles are found.
        """
        return await self.role_db.get_all_roles()

    async def single_role(self, role_name: str) -> RoleMethods:
        """
        Retrieves a single role by its name.

        Args:
            role_name: The name of the role.

        Returns:
            RoleBDModel: The role object.
        """
        return await self.role_db.get_single_role(role_name)

    async def create_new_role(self, role: dict) -> None:
        """
        Creates a new role.

        Args:
            role (dict): The role data.

        Returns:
            RoleBDModel: The created role object.
        """
        await self.role_db.create_role(role)

    async def update_role(self, role_name: str, new_info: dict) -> None:
        """
        Updates a role.

        Args:
            role_name: The name of the role to update.
            new_info: The updated role information.

        Returns:
            RoleBDModel: The updated role object.
        """
        await self.role_db.update_role(role_name, new_info)

    async def delete_role(self, role_name: str) -> None:
        """
        Deletes a role.

        Args:
            role_name: The name of the role to delete.

        Returns:
            dict[Any, str]: A dictionary with a information message.
        """
        await self.role_db.delete_role(role_name)

    async def assign_role(self, user_id: str, role_name: str) -> None:
        """
        Assigns a role to a user.

        Args:
            user_id: The ID of the user.
            role_name: The name of the role.
        """
        await self.user_db.assign_role_to_user(user_id, role_name)

    async def remove_role_from_user(self, user_id: str, role_name: str) -> None:
        """
        Removes a role from a user.

        Args:
            user_id: The ID of the user.
            role_name: The name of the role.
        """
        await self.user_db.remove_role_from_user(user_id, role_name)

    async def all_users_role(self, user_id: str) -> UserRoles | None:
        """
        Retrieves all roles for a user.

        Args:
            user_id: The ID of the user.

        Returns:
            list[UserRoleBD] | None: A list of user roles or None if no roles are found.
        """
        result = await self.user_db.get_all_user_roles(user_id)
        user_roles = [role.name for role in result.roles]
        return UserRoles(id=result.id, name=result.name, email=result.email, roles=user_roles)


@lru_cache()
def get_role_service(role_db=Depends(get_role_db), user_db=Depends(get_user_db)):
    return RoleService(role_db=role_db, user_db=user_db)
