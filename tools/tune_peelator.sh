#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  tools/tune_peelator.sh N [options]

Options:
  --max-generator-count K       default: 40
  --excluded-support-limit LIM  default: 100000000
  --spans LIST                  comma-separated max_move_span values, default: 3,5,8
  --depths LIST                 comma-separated depth values, default: 4,6,8
  --branches LIST               comma-separated branches: DROP,NEW,BOTH; default: BOTH
  --json                        emit raw JSON lines instead of summary table

Examples:
  tools/tune_peelator.sh "$N50B"
  tools/tune_peelator.sh "$RSA100" --spans 3,5,8,13 --depths 4,6,8,10
EOF
}

N=""
MAX_GENERATOR_COUNT=40
EXCLUDED_SUPPORT_LIMIT=100000000
SPANS="3,5,8"
DEPTHS="4,6,8"
BRANCHES="BOTH"
JSON=0

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

N="$1"
shift

while [[ $# -gt 0 ]]; do
  case "$1" in
    --max-generator-count)
      MAX_GENERATOR_COUNT="$2"
      shift 2
      ;;
    --excluded-support-limit)
      EXCLUDED_SUPPORT_LIMIT="$2"
      shift 2
      ;;
    --spans)
      SPANS="$2"
      shift 2
      ;;
    --depths)
      DEPTHS="$2"
      shift 2
      ;;
    --branches)
      BRANCHES="$2"
      shift 2
      ;;
    --json)
      JSON=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

split_csv() {
  local value="$1"
  value="${value//,/ }"
  printf '%s\n' $value
}

if [[ "$BRANCHES" == "BOTH" ]]; then
  BRANCH_LIST=(DROP NEW)
else
  mapfile -t BRANCH_LIST < <(split_csv "$BRANCHES")
fi

mapfile -t SPAN_LIST < <(split_csv "$SPANS")
mapfile -t DEPTH_LIST < <(split_csv "$DEPTHS")

if [[ "$JSON" -eq 0 ]]; then
  echo "PET TUNE PEELATOR"
  echo "N_digits = ${#N}"
  echo "max_generator_count = $MAX_GENERATOR_COUNT"
  echo "excluded_support_limit = $EXCLUDED_SUPPORT_LIMIT"
  echo "spans = $SPANS"
  echo "depths = $DEPTHS"
  echo "branches = ${BRANCH_LIST[*]}"
  echo
  printf '%-6s %-5s %-5s %-34s %-16s %-8s %-14s %s\n' \
    "branch" "span" "depth" "best_signal" "anchor_status" "classic" "binding" "reason"
  printf '%-6s %-5s %-5s %-34s %-16s %-8s %-14s %s\n' \
    "------" "-----" "-----" "----------------------------------" "----------------" "--------" "--------------" "------"
fi

for branch in "${BRANCH_LIST[@]}"; do
  if [[ "$branch" != "DROP" && "$branch" != "NEW" ]]; then
    echo "--branches entries must be DROP or NEW" >&2
    exit 2
  fi

  for span in "${SPAN_LIST[@]}"; do
    for depth in "${DEPTH_LIST[@]}"; do
      json="$(
        python -m pet.cli opaque-recursive-lens "$N" \
          --max-generator-count "$MAX_GENERATOR_COUNT" \
          --excluded-support-limit "$EXCLUDED_SUPPORT_LIMIT" \
          --max-move-span "$span" \
          --depth "$depth" \
          --branch-recursion "$branch" \
          --composite-edge-peel \
          --anchor-field \
          --json
      )"

      if [[ "$JSON" -eq 1 ]]; then
        jq -c \
          --arg branch "$branch" \
          --argjson span "$span" \
          --argjson depth "$depth" \
          '{
            branch: $branch,
            max_move_span: $span,
            depth: $depth,
            branch_verdict: .branch_verdict,
            recurrence: .recurrence,
            composite_edge_peel: .composite_edge_peel_payload,
            subedge_recursion: .subedge_recursion_payload,
            anchor_field: .anchor_field_payload
          }' <<<"$json"
      else
        jq -r \
          --arg branch "$branch" \
          --arg span "$span" \
          --arg depth "$depth" \
          '
          .branch_verdict as $v |
          [
            $branch,
            $span,
            $depth,
            ($v.best_signal // "unavailable"),
            ($v.anchor_status // "none"),
            (if $v.classic_ready then "yes" else "no" end),
            ($v.binding_strength // "none"),
            ($v.reason // "no verdict")
          ] | @tsv
          ' <<<"$json" \
        | awk -F '\t' '{
            printf "%-6s %-5s %-5s %-34s %-16s %-8s %-14s %s\n",
              $1, $2, $3, $4, $5, $6, $7, $8
          }'
      fi
    done
  done
done
