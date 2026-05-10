#!/usr/bin/env python3
"""index — build an aligner index for a cached reference (simulator)."""

from __future__ import annotations

import argparse
import json
import sys

from genomics.tools._lib.index import index_entry


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument(
        "--aligner",
        default="bwa",
        choices=["bwa", "star", "bowtie2"],
        help="Aligner to index for (default: bwa)",
    )
    p.add_argument(
        "--reference",
        default="GRCh38",
        help="Reference build name (e.g. GRCh38, GRCh37, T2TCHM13)",
    )
    args = p.parse_args()

    print(f"index: {args.aligner}/{args.reference}", file=sys.stderr)
    result = index_entry(aligner=args.aligner, reference=args.reference)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
