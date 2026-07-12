from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    base = re.sub(r"[^\w\s-]", "", ascii_text.lower())
    base = re.sub(r"[\s_]+", "-", base).strip("-")
    return re.sub(r"-+", "-", base)


@dataclass(frozen=True)
class Slug:
    """URL-safe slug, unique per tenant."""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not normalized or len(normalized) > 255:
            raise ValueError(f"Slug must be 1-255 characters: {self.value!r}")
        if not _SLUG_PATTERN.match(normalized):
            raise ValueError(f"Slug contains invalid characters: {self.value!r}")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_title(cls, title: str, *, suffix: str | None = None) -> "Slug":
        base = _slugify(title)
        if not base:
            raise ValueError("Cannot generate slug from empty title")
        if suffix:
            base = f"{base}-{suffix}"
        return cls(base[:255])
