#!/usr/bin/env bash
# Shell wrapper for resolve.py — see python file for argparse help.
exec python3 "$(dirname "$0")/resolve.py" "$@"
