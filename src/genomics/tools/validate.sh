#!/usr/bin/env bash
# Shell wrapper for validate.py — see python file for argparse help.
exec python3 "$(dirname "$0")/validate.py" "$@"
