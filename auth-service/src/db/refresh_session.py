from typing import Optional
from uuid import UUID

from db.base_bd import RefreshSession, User
from db.connection import get_session
from db.user_db import UserMethods
from fastapi import Depends
from sqlalchemy import insert, select
from sqlalchemy.orm import selectinload


class RefreshSessionMethods(RefreshSession):
    async def add(self, **kwargs):
        query = insert(RefreshSession).values(kwargs)
        await self.session.execute(query)
        await self.session.commit()
        return_query = select(RefreshSession).where(
            RefreshSession.finger_print == kwargs.get('finger_print')
        )
        result = await self.session.scalar(return_query)
        return result

    async def get_by_finger_print(
        self,
        email: str,
        finger_print: str,
    ) -> Optional['RefreshSession']:
        """Get an auth session by fingerprint."""
        user = await UserMethods(self.session).get_by_email(email)
        refresh_session = await self.session.scalar(
            select(RefreshSession).where(
                RefreshSession.user == user
                and RefreshSession.finger_print == finger_print
            )
        )
        return refresh_session

    async def get_by_refresh_token(
        self, refresh_token: UUID
    ) -> Optional['RefreshSession']:
        """Get an auth session by refresh token"""
        refresh_session = await self.session.scalars(
            select(RefreshSession)
            .where(RefreshSession.refresh_token == refresh_token)
            .options(
                selectinload(RefreshSession.user).selectinload(User.roles)
            )
            # .options(selectinload(RefreshSession.user))
        )
        return refresh_session.one_or_none()


async def get_refresh_session_db(sessions=Depends(get_session)):
    return RefreshSessionMethods(sessions)
