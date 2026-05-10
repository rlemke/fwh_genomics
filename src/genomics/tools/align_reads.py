#!/usr/bin/env python3
"""align-reads — simulate align_reads (genomics pipeline)."""

from __future__ import annotations

import argparse
import json
import sys

from genomics.tools._lib.pipeline import align_reads


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--sample-id", default="NA12878", dest="sample_id")
    args = p.parse_args()
    print(f"align_reads: " + str(args.sample_id), file=sys.stderr)
    result = align_reads(sample_id=args.sample_id)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
