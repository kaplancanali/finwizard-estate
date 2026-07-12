from __future__ import annotations

import re
from dataclasses import dataclass

_CODE_PATTERN = re.compile(r"^FW-[A-Z]{2}-[A-Z0-9]{2,6}-\d{8}$")


@dataclass(frozen=True)
class PropertyCode:
    """Human-readable unique identifier, e.g. FW-TR-IST-00001234."""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().upper()
        if not _CODE_PATTERN.match(normalized):
            msg = (
                f"Invalid property code format: {self.value!r}. "
                "Expected FW-{COUNTRY}-{REGION}-{SEQUENCE:08d}"
            )
            raise ValueError(msg)
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
