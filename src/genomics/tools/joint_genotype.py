#!/usr/bin/env python3
"""joint-genotype — simulate joint_genotype (genomics pipeline)."""

from __future__ import annotations

import argparse
import json
import sys

from genomics.tools._lib.pipeline import joint_genotype


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--gvcf-dir", default="/gvcf", dest="gvcf_dir")
    p.add_argument("--reference-build", default="GRCh38", dest="reference_build")
    p.add_argument("--sample-count", type=int, default=100, dest="sample_count")
    args = p.parse_args()
    print(f"joint_genotype: {args.sample_count} gVCFs from {args.gvcf_dir}", file=sys.stderr)
    result = joint_genotype(
        gvcf_dir=args.gvcf_dir,
        reference_build=args.reference_build,
        sample_count=args.sample_count,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
