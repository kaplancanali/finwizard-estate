#!/usr/bin/env python3
"""Write OpenAPI schema JSON to stdout or a file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from property_service.main import create_app


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate OpenAPI schema")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("openapi/v1/property-service.yaml"),
        help="Output file path",
    )
    args = parser.parse_args()

    app = create_app()
    schema = app.openapi()
    payload = json.dumps(schema, indent=2)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload)
        print(f"Wrote OpenAPI schema to {args.output}")
    else:
        print(payload)


if __name__ == "__main__":
    main()
