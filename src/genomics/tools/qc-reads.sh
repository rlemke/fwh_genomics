#!/usr/bin/env bash
# Shell wrapper for qc_reads.py — see python file for argparse help.
exec python3 "$(dirname "$0")/qc_reads.py" "$@"
