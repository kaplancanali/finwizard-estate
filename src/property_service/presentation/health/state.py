from __future__ import annotations

_startup_complete = False


def mark_startup_complete() -> None:
    global _startup_complete
    _startup_complete = True


def is_startup_complete() -> bool:
    return _startup_complete


def reset_startup_state() -> None:
    global _startup_complete
    _startup_complete = False
