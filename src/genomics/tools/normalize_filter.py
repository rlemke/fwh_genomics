#!/usr/bin/env python3
"""normalize-filter — simulate normalize_filter (genomics pipeline)."""

from __future__ import annotations

import argparse
import json
import sys

from genomics.tools._lib.pipeline import normalize_filter


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--vcf-path", default="/vcf/cohort.vcf.gz", dest="vcf_path")
    args = p.parse_args()
    print(f"normalize_filter: " + str(args.vcf_path), file=sys.stderr)
    result = normalize_filter(vcf_path=args.vcf_path)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
