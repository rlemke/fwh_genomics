#!/usr/bin/env python3
"""joint-genotype — simulate joint_genotype (genomics pipeline)."""

from __future__ import annotations

import argparse
import json
import sys

from genomics.tools._lib.pipeline import joint_genotype


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--cohort-id", default="cohort-001", dest="cohort_id")
    args = p.parse_args()
    print(f"joint_genotype: " + str(args.cohort_id), file=sys.stderr)
    result = joint_genotype(cohort_id=args.cohort_id)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
