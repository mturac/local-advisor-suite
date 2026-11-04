#!/usr/bin/env sh
# Run the full test suite (standard library unittest; no pip installs needed).
set -e
cd "$(dirname "$0")"
python3 -m unittest discover -s tests -p 'test_*.py' "$@"
