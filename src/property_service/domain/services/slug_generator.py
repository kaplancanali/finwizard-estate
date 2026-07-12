from __future__ import annotations

from property_service.domain.value_objects.slug import Slug


class SlugGenerator:
    """Generates URL-safe slugs with collision resolution."""

    def __init__(self) -> None:
        self._used_slugs: set[str] = set()

    def generate(self, title: str, *, district: str | None = None) -> Slug:
        base_parts = [title]
        if district:
            base_parts.append(district)
        base_title = " ".join(base_parts)
        slug = Slug.from_title(base_title)
        return self._resolve_collision(slug)

    def register_existing(self, slug: Slug) -> None:
        self._used_slugs.add(slug.value)

    def _resolve_collision(self, slug: Slug) -> Slug:
        if slug.value not in self._used_slugs:
            self._used_slugs.add(slug.value)
            return slug
        counter = 2
        while True:
            candidate = Slug.from_title(slug.value, suffix=str(counter))
            if candidate.value not in self._used_slugs:
                self._used_slugs.add(candidate.value)
                return candidate
            counter += 1
