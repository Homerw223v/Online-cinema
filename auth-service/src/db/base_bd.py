import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class BaseDB(DeclarativeBase):
    # __table_args__ = {'schema': 'tests'}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    created = Column(DateTime, default=datetime.utcnow)

    def __init__(self, session, *args, **kwargs):
        super().__init__(**kwargs)
        self.session = session


association_table = Table(
    'user_role',
    BaseDB.metadata,
    Column(
        'id',
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    ),
    Column(
        'user_id',
        ForeignKey('user_table.id', ondelete='CASCADE'),
        nullable=False,
        primary_key=True,
    ),
    Column(
        'role_name',
        ForeignKey('role.name', ondelete='CASCADE'),
        nullable=False,
        primary_key=True,
    ),
)


class AddDeleteMixin:
    pass


class User(BaseDB):
    __tablename__ = 'user_table'

    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=True)
    surname: Mapped[str] = mapped_column(String(50), nullable=True)
    roles: Mapped[list['RoleTable']] = relationship(
        secondary=association_table, cascade='delete', back_populates='users'
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )
    birthday: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    refresh_sessions: Mapped[list['RefreshSession']] = relationship(
        back_populates='user'
    )

    def __repr__(self):
        return f'<User {self.email}>'


class RoleTable(BaseDB):
    __tablename__ = 'role'

    name: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, primary_key=True
    )
    users: Mapped[list['User']] = relationship(
        secondary=association_table, cascade='delete', back_populates='roles'
    )

    def __repr__(self):
        return f'Role: {self.name}'


class RefreshSession(BaseDB):
    __tablename__ = 'refresh_session'
    user_id: Mapped[UUID] = mapped_column(ForeignKey(User.id), nullable=False)
    refresh_token: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    finger_print: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc)
    )
    user: Mapped['User'] = relationship(back_populates='refresh_sessions')
    agent = relationship(User, foreign_keys=[user_id])


class SocialAuthTable(BaseDB):
    __tablename__ = 'social_auth'
    __table_args__ = (UniqueConstraint('user_id'),)

    social_name: Mapped[str] = mapped_column(String(50), nullable=False)
    social_id: Mapped[str] = mapped_column(nullable=False, unique=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(User.id), nullable=False, unique=True
    )


class LoginHistoryTable(BaseDB):
    __tablename__ = 'login_history'

    agent_id = Column(ForeignKey(RefreshSession.id), nullable=False)
    time = Column(DateTime, default=datetime.utcnow)
    action = Column(String(10), nullable=False)
    agent = relationship(RefreshSession, foreign_keys=[agent_id])
