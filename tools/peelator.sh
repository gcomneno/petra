#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ "$#" -lt 1 ]]; then
  exec "$SCRIPT_DIR/pet_triage_pipeline.sh" "$@"
fi

N="$1"
shift

exec "$SCRIPT_DIR/pet_triage_pipeline.sh" "$N" --legacy-diagnostics "$@"
