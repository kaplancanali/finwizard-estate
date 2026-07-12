from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

_ISO_COUNTRY = re.compile(r"^[A-Z]{2}$")
_ISO_CURRENCY = re.compile(r"^[A-Z]{3}$")


def strip_non_empty_title(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("title cannot be blank or whitespace only")
    return stripped


def validate_iso_country_code(value: str) -> str:
    upper = value.upper()
    if not _ISO_COUNTRY.match(upper):
        raise ValueError("country_code must be ISO 3166-1 alpha-2")
    return upper


def validate_iso_currency(value: str) -> str:
    upper = value.upper()
    if not _ISO_CURRENCY.match(upper):
        raise ValueError("currency must be ISO 4217 (3 letters)")
    return upper


def validate_decimal_places(value: Decimal, *, max_places: int) -> Decimal:
    exponent = value.as_tuple().exponent
    if isinstance(exponent, int) and exponent < -max_places:
        raise ValueError(f"Maximum {max_places} decimal places allowed")
    return value


def validate_price_digits(value: Decimal, *, max_integer_digits: int = 15, max_decimal_places: int = 2) -> Decimal:
    validate_decimal_places(value, max_places=max_decimal_places)
    normalized = value.normalize()
    digits = len(normalized.as_tuple().digits)
    exponent = normalized.as_tuple().exponent
    if isinstance(exponent, int) and exponent < 0:
        integer_digits = digits + exponent
    else:
        integer_digits = digits
    if integer_digits > max_integer_digits:
        raise ValueError(f"Price cannot exceed {max_integer_digits} integer digits")
    return value


def validate_room_count_increment(value: Decimal) -> Decimal:
    doubled = value * 2
    if doubled != doubled.to_integral_value():
        raise ValueError("room_count must use 0.5 increments")
    return value


def validate_construction_year(value: int) -> int:
    max_year = datetime.now().year + 5
    if value < 1800 or value > max_year:
        raise ValueError(f"construction_year must be between 1800 and {max_year}")
    return value


def validate_tag_lengths(tags: list[str], *, max_tags: int = 20, max_tag_length: int = 100) -> list[str]:
    if len(tags) > max_tags:
        raise ValueError(f"Maximum {max_tags} tags allowed")
    for tag in tags:
        if len(tag) > max_tag_length:
            raise ValueError(f"Each tag must be at most {max_tag_length} characters")
    return tags
