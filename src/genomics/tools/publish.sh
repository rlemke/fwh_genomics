#!/usr/bin/env bash
# Shell wrapper for publish.py — see python file for argparse help.
exec python3 "$(dirname "$0")/publish.py" "$@"
