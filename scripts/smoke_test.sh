#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
curl --fail --silent "${BASE_URL}/healthz" | grep -q '"status":"ok"'
curl --fail --silent "${BASE_URL}/readyz" | grep -q '"status":"ready"'

echo "smoke test passed"
