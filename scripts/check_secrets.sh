#!/usr/bin/env bash
set -euo pipefail

# Simple grep-based check for common secret patterns.
# This is NOT perfect; use a secret-scanner in CI for stronger guarantees.

echo "[check] scanning for .env files..."
found_env=$(find . -name '.env' -o -name '.env.*' | wc -l | tr -d ' ')
if [ "$found_env" != "0" ]; then
  echo "Found env files (should not be committed):"
  find . -name '.env' -o -name '.env.*'
  exit 1
fi

echo "[check] scanning for AWS keys patterns..."
if rg -n "AKIA[0-9A-Z]{16}" . ; then
  echo "Potential AWS access key found."; exit 1
fi

echo "[ok] basic secret scan passed"
