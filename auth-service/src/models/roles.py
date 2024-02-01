import enum
from dataclasses import dataclass


@dataclass(frozen=True)
class UserRole:
    """User roles using in this service"""
    admin = 'admin'
    user = 'user'
