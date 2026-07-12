from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PropertyUpdateDTO:
    expected_version: int
    title: str | None = None
    description: str | None = None
    changes: dict[str, Any] | None = None
