#!/usr/bin/env python3
"""Print development roadmap completion status."""

from __future__ import annotations

from pathlib import Path

from property_service.architecture.roadmap_status import evaluate_roadmap, format_roadmap_report


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    report = evaluate_roadmap(root)
    print(format_roadmap_report(report))


if __name__ == "__main__":
    main()
