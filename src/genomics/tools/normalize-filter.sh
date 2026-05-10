#!/usr/bin/env bash
# Shell wrapper for normalize_filter.py — see python file for argparse help.
exec python3 "$(dirname "$0")/normalize_filter.py" "$@"
