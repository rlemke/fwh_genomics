#!/usr/bin/env python3
"""resolve — alias / accession lookup over the genomics resource registry.

Pick one of ``--reference NAME``, ``--annotation NAME``, ``--sample
ACCESSION``, or ``--list [--category CATEGORY]``.
"""

from __future__ import annotations

import argparse
import json
import sys

from genomics.tools._lib.resolve import (
    list_resources,
    resolve_annotation,
    resolve_reference,
    resolve_sample,
)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--reference", help="Resolve a reference genome name (alias or facet ID)")
    g.add_argument("--annotation", help="Resolve an annotation database name")
    g.add_argument("--sample", help="Resolve an SRA accession")
    g.add_argument("--list", action="store_true", help="List all cached resources")
    p.add_argument(
        "--category",
        default="",
        help="Filter --list by category (reference / annotation / sra)",
    )
    args = p.parse_args()

    if args.list:
        print(f"resolve: list category={args.category or 'all'}", file=sys.stderr)
        result = list_resources(category=args.category)
    elif args.reference:
        print(f"resolve: reference {args.reference}", file=sys.stderr)
        result = resolve_reference(name=args.reference)
    elif args.annotation:
        print(f"resolve: annotation {args.annotation}", file=sys.stderr)
        result = resolve_annotation(name=args.annotation)
    else:
        print(f"resolve: sample {args.sample}", file=sys.stderr)
        result = resolve_sample(accession=args.sample)

    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
