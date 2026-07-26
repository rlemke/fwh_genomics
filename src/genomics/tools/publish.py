#!/usr/bin/env python3
"""publish — simulate publishing a cohort's final report bundle."""

from __future__ import annotations

import argparse
import json
import sys

from genomics.tools._lib.pipeline import publish


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--variant-table-path", default="/vcf/cohort.annotated.tsv",
                   dest="variant_table_path")
    p.add_argument("--qc-report-path", default="/reports/qc_report.html", dest="qc_report_path")
    p.add_argument("--stats-path", default="/reports/cohort_stats.json", dest="stats_path")
    p.add_argument("--dataset-id", default="cohort-001", dest="dataset_id")
    args = p.parse_args()
    print(f"publish: {args.dataset_id}", file=sys.stderr)
    result = publish(
        variant_table_path=args.variant_table_path,
        qc_report_path=args.qc_report_path,
        stats_path=args.stats_path,
        dataset_id=args.dataset_id,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
