from __future__ import annotations

from collections import Counter

_task_counters: Counter[str] = Counter()


def record_task_result(task_name: str, status: str) -> None:
    _task_counters[f"{task_name}:{status}"] += 1


def get_task_counters() -> dict[str, int]:
    return dict(_task_counters)


def reset_task_counters() -> None:
    _task_counters.clear()
