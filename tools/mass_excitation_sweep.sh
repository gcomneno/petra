#!/usr/bin/env bash
set -euo pipefail

N="${1:?usage: tools/mass_excitation_sweep.sh N}"
EXCLUDED_SUPPORT_LIMIT="${EXCLUDED_SUPPORT_LIMIT:-16}"
MAX_GENERATOR_COUNT="${MAX_GENERATOR_COUNT:-20}"
SPANS="${SPANS:-1 2 3 5 8 13}"

echo "N=$N"
echo "excluded_support_limit=$EXCLUDED_SUPPORT_LIMIT"
echo "max_generator_count=$MAX_GENERATOR_COUNT"
echo
echo -e "span\tkind\tmove\tk_range\twidth\tmin_trigger_span\tmax_trigger_span\tfocus\tsignal"

for S in $SPANS; do
  python -m pet.cli opaque-mass-response "$N" \
    --max-generator-count "$MAX_GENERATOR_COUNT" \
    --excluded-support-limit "$EXCLUDED_SUPPORT_LIMIT" \
    --max-move-span "$S" \
    --bands \
    --json \
  | jq -r --arg span "$S" '
      (
        [
          .magnetic_bands[]
          | select(.kind == "multi-threshold")
          | [
              $span,
              .kind,
              .move,
              .k_range,
              (.band_width | tostring),
              (.min_trigger_span | tostring),
              (.max_trigger_span | tostring),
              (.focus_score | tostring),
              .signal
            ]
        ][0]
        // [$span, "none", "-", "-", "-", "-", "-", "-", "-"]
      )
      | @tsv
    '
done
