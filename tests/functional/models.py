from dataclasses import dataclass
from typing import Any


@dataclass
class SessionResponse:
    headers: Any
    status: int
    body: dict
