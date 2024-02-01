import abc
from typing import Any


class AbstractCache(abc.ABC):

    @abc.abstractmethod
    def get(self, key: str) -> Any | None:
        """Getting data with key"""
        pass

    @abc.abstractmethod
    def set(self, key: str, value: str | int | float, expired: int):
        """Setting data with key"""
        pass

    @abc.abstractmethod
    def exists(self, key: str) -> bool:
        """Check if data exists in cache with key"""
        pass

    @abc.abstractmethod
    def delete(self, keys: list[str]):
        """Deleting from cache according list of keys"""
        pass

    @abc.abstractmethod
    def flush(self):
        """Clear cache"""
        pass
