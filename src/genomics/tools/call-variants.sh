#!/usr/bin/env bash
# Shell wrapper for call_variants.py — see python file for argparse help.
exec python3 "$(dirname "$0")/call_variants.py" "$@"
