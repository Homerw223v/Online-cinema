import abc
import json
from typing import Any, Dict

from singleton import SingletonMeta

from .config import BaseAppSettings


class BaseStorage(abc.ABC):
    """Abstract storage for state.
    Allows saving and retrieving state.
    The method of storing state may vary depending on the final implementation.
    For example, state can be stored in a database or a distributed file storage.
    """

    @abc.abstractmethod
    def save_state(self, state: Dict[str, Any]) -> None:
        """Save the state to the storage."""

    @abc.abstractmethod
    def retrieve_state(self) -> Dict[str, Any]:
        """Retrieve the state from the storage."""


class JsonFileStorage(BaseStorage):
    """Implementation of storage using a local file.
    Storage format: JSON
    """

    file_path = BaseAppSettings().state_path

    def save_state(self, state: Dict[str, Any]) -> None:
        """Save the state to the storage."""
        with open(self.file_path, 'w') as fp:
            json.dump(state, fp)

    def retrieve_state(self) -> Dict[str, Any]:
        """Retrieve the state from the storage."""
        try:
            with open(self.file_path, 'r') as fp:
                state = json.load(fp)
            return state
        except FileNotFoundError:
            return {}


class State(metaclass=SingletonMeta):
    """Class for working with states.
    metaclass=SingletonMeta is used to ensure that there is only one instance of the class, as the state
    should be the same for the entire project.
    """

    def __init__(self) -> None:
        self.storage = JsonFileStorage()

    def set_state(self, key: str, value: Any) -> None:
        """Set the state for a specific key."""
        state = self.storage.retrieve_state()
        state[key] = value
        self.storage.save_state(state)

    def get_state(self, key: str) -> Any:
        """Get the state for a specific key."""
        state = self.storage.retrieve_state()
        return state.get(key, None)
