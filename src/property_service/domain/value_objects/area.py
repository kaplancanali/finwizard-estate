from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Area:
    value_sqm: Decimal

    def __post_init__(self) -> None:
        if self.value_sqm <= 0:
            raise ValueError(f"Area must be positive: {self.value_sqm}")
