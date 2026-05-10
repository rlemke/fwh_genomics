#!/usr/bin/env bash
# Shell wrapper for cohort_analytics.py — see python file for argparse help.
exec python3 "$(dirname "$0")/cohort_analytics.py" "$@"
