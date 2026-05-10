#!/usr/bin/env python3
"""publish — simulate publishing a cohort's final report bundle."""

from __future__ import annotations

import argparse
import json
import sys

from genomics.tools._lib.pipeline import publish


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--cohort-id", default="cohort-001", dest="cohort_id")
    p.add_argument("--report-dir", default="/reports/", dest="report_dir")
    args = p.parse_args()
    print(f"publish: {args.cohort_id} -> {args.report_dir}", file=sys.stderr)
    result = publish(cohort_id=args.cohort_id, report_dir=args.report_dir)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
