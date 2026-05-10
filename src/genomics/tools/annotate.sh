#!/usr/bin/env bash
# Shell wrapper for annotate.py — see python file for argparse help.
exec python3 "$(dirname "$0")/annotate.py" "$@"
