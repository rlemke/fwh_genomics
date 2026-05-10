#!/usr/bin/env bash
# Shell wrapper for joint_genotype.py — see python file for argparse help.
exec python3 "$(dirname "$0")/joint_genotype.py" "$@"
