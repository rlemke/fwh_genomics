#!/usr/bin/env bash
# Shell wrapper for index.py — see python file for argparse help.
exec python3 "$(dirname "$0")/index.py" "$@"
