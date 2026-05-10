#!/usr/bin/env bash
# Shell wrapper for align_reads.py — see python file for argparse help.
exec python3 "$(dirname "$0")/align_reads.py" "$@"
