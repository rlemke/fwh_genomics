#!/usr/bin/env python3
"""validate — verify the checksum of a cached genomics resource (simulator)."""

from __future__ import annotations

import argparse
import json
import sys

from genomics.tools._lib.operations import validate
from genomics.tools._lib.resolve import resolve_reference


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--resource", default="GRCh38", help="Resource name to validate")
    args = p.parse_args()

    cache = resolve_reference(name=args.resource)["cache"]
    print(f"validate: {args.resource}", file=sys.stderr)
    result = validate(cache=cache)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
