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

rows_json="$(mktemp)"
trap 'rm -f "$rows_json"' EXIT

: > "$rows_json"

for S in $SPANS; do
  row="$(
    python -m pet.cli opaque-mass-response "$N" \
      --max-generator-count "$MAX_GENERATOR_COUNT" \
      --excluded-support-limit "$EXCLUDED_SUPPORT_LIMIT" \
      --max-move-span "$S" \
      --bands \
      --json \
    | jq -c --arg span "$S" '
        (
          [
            .magnetic_bands[]
            | select(.kind == "multi-threshold")
            | {
                span: ($span | tonumber),
                kind: .kind,
                move: .move,
                k_range: .k_range,
                width: .band_width,
                min_trigger_span: .min_trigger_span,
                max_trigger_span: .max_trigger_span,
                focus: .focus_score,
                signal: .signal
              }
          ][0]
          // {
              span: ($span | tonumber),
              kind: "none",
              move: "-",
              k_range: "-",
              width: null,
              min_trigger_span: null,
              max_trigger_span: null,
              focus: null,
              signal: "-"
            }
        )
      '
  )"
  printf '%s\n' "$row" >> "$rows_json"
  printf '%s\n' "$row" \
  | jq -r '[
      (.span | tostring),
      .kind,
      .move,
      .k_range,
      ((.width // "-") | tostring),
      ((.min_trigger_span // "-") | tostring),
      ((.max_trigger_span // "-") | tostring),
      ((.focus // "-") | tostring),
      .signal
    ] | @tsv'
done

echo
echo "Resonance summary"
jq -s -r '
  def present: map(select(.kind != "none"));
  def same_range($a; $b): $a.k_range == $b.k_range and $a.width == $b.width;

  (present) as $present
  | if ($present | length) == 0 then
      [
        "  status = none",
        "  onset_span = none",
        "  onset_k_range = none",
        "  onset_width = none",
        "  saturation_span = none",
        "  saturation_k_range = none",
        "  saturation_width = none"
      ][]
    else
      ($present[0]) as $onset
      | (
          reduce range(0; ($present | length)) as $i
            ($present[0];
             if $i == 0 then .
             elif same_range($present[$i]; $present[$i - 1]) then .
             else $present[$i]
             end)
        ) as $saturation
      | [
          "  status = present",
          "  onset_span = \($onset.span)",
          "  onset_k_range = \($onset.k_range)",
          "  onset_width = \($onset.width)",
          "  saturation_span = \($saturation.span)",
          "  saturation_k_range = \($saturation.k_range)",
          "  saturation_width = \($saturation.width)"
        ][]
    end
' "$rows_json"
