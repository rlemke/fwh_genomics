#!/usr/bin/env python3
"""ingest-reference — simulate ingest_reference (genomics pipeline)."""

from __future__ import annotations

import argparse
import json
import sys

from genomics.tools._lib.pipeline import ingest_reference


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--reference-build", default="GRCh38", dest="reference_build")
    args = p.parse_args()
    print(f"ingest_reference: " + str(args.reference_build), file=sys.stderr)
    result = ingest_reference(reference_build=args.reference_build)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
