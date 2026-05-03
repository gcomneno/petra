#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  tools/peelator_pipeline.sh N [options]

Options:
  --max-generator-count K       default: 40
  --excluded-support-limit LIM  default: 100000000
  --max-move-span S             default: 5
  --depth D                     default: 3
  --handoff-radius R            default: 100
  --json                        emit JSON from PET commands
  --fork-follow SIDE           run fork follow-up lens for NEW, DROP, or BOTH; default: BOTH
  --no-fork-follow              skip fork follow-up lens pass
  --no-fork                     skip focused peel fork pass
  --no-recursive                skip recursive terminal reduction pass

Examples:
  tools/peelator_pipeline.sh 10403 --max-generator-count 4 --excluded-support-limit 16 --max-move-span 2

  tools/peelator_pipeline.sh "$RSA250" --depth 3
EOF
}

N=""
MAX_GENERATOR_COUNT=40
EXCLUDED_SUPPORT_LIMIT=100000000
MAX_MOVE_SPAN=5
DEPTH=3
HANDOFF_RADIUS=100
JSON=0
RUN_FORK=1
RUN_FORK_FOLLOW=1
FORK_FOLLOW=BOTH
RUN_RECURSIVE=1

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
    --max-move-span)
      MAX_MOVE_SPAN="$2"
      shift 2
      ;;
    --depth)
      DEPTH="$2"
      shift 2
      ;;
    --handoff-radius)
      HANDOFF_RADIUS="$2"
      shift 2
      ;;
    --json)
      JSON=1
      shift
      ;;
    --fork-follow)
      FORK_FOLLOW="$2"
      shift 2
      ;;
    --no-fork-follow)
      RUN_FORK_FOLLOW=0
      shift
      ;;
    --no-fork)
      RUN_FORK=0
      shift
      ;;
    --no-recursive)
      RUN_RECURSIVE=0
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

JSON_ARG=()
if [[ "$JSON" -eq 1 ]]; then
  JSON_ARG=(--json)
fi

section() {
  echo
  echo "================================================================"
  echo "$1"
  echo "================================================================"
}

echo "PEELATOR PIPELINE"
echo "N_digits = ${#N}"
echo "max_generator_count = $MAX_GENERATOR_COUNT"
echo "excluded_support_limit = $EXCLUDED_SUPPORT_LIMIT"
echo "max_move_span = $MAX_MOVE_SPAN"
echo "depth = $DEPTH"
echo "handoff_radius = $HANDOFF_RADIUS"
echo "fork_follow = ${FORK_FOLLOW:-disabled}"
echo
echo "claim = PET diagnostic pipeline only; this does not factor N unless classic handoff verifies factors"

section "0. pet-lens-hint"
tools/pet_lens_hint.py "$N" \
  --schedule-limit 8 \
  --max-leaves 8 \
  --summary

section "0b. pet-lens-candidates"
tools/pet_lens_candidates.py "$N" \
  --max-leaves 8

section "0c. pet-lens-transition"
tools/pet_lens_transition.py "$N" \
  --max-leaves 8

section "0d. pet-local-probe-proposal"
tools/pet_local_probe_proposal.py "$N" \
  --max-leaves 8 \
  --max-generator-count "$MAX_GENERATOR_COUNT" \
  --excluded-support-limit "$EXCLUDED_SUPPORT_LIMIT" \
  --max-move-span "$MAX_MOVE_SPAN"

section "1. opaque-mass-response --bands"
python -m pet.cli opaque-mass-response "$N" \
  --max-generator-count "$MAX_GENERATOR_COUNT" \
  --excluded-support-limit "$EXCLUDED_SUPPORT_LIMIT" \
  --max-move-span "$MAX_MOVE_SPAN" \
  --bands \
  "${JSON_ARG[@]}"

section "2. opaque-focused-peel --classic-handoff"
python -m pet.cli opaque-focused-peel "$N" \
  --max-generator-count "$MAX_GENERATOR_COUNT" \
  --excluded-support-limit "$EXCLUDED_SUPPORT_LIMIT" \
  --max-move-span "$MAX_MOVE_SPAN" \
  --classic-handoff \
  --handoff-radius "$HANDOFF_RADIUS" \
  "${JSON_ARG[@]}"

if [[ "$RUN_FORK" -eq 1 ]]; then
  section "3. opaque-focused-peel --fork"
  python -m pet.cli opaque-focused-peel "$N" \
    --max-generator-count "$MAX_GENERATOR_COUNT" \
    --excluded-support-limit "$EXCLUDED_SUPPORT_LIMIT" \
    --max-move-span "$MAX_MOVE_SPAN" \
    --fork \
    "${JSON_ARG[@]}"
fi

BRANCHES=()
if [[ "$FORK_FOLLOW" == "BOTH" ]]; then
  BRANCHES=(DROP NEW)
elif [[ "$FORK_FOLLOW" == "NEW" || "$FORK_FOLLOW" == "DROP" ]]; then
  BRANCHES=("$FORK_FOLLOW")
else
  echo "--fork-follow must be NEW, DROP, or BOTH" >&2
  exit 2
fi

if [[ "$RUN_FORK_FOLLOW" -eq 1 ]]; then
  for BRANCH in "${BRANCHES[@]}"; do
    section "4. opaque-focused-peel --fork-follow $BRANCH"
    python -m pet.cli opaque-focused-peel "$N" \
      --max-generator-count "$MAX_GENERATOR_COUNT" \
      --excluded-support-limit "$EXCLUDED_SUPPORT_LIMIT" \
      --max-move-span "$MAX_MOVE_SPAN" \
      --fork-follow "$BRANCH" \
      "${JSON_ARG[@]}"
  done
fi

if [[ "$RUN_RECURSIVE" -eq 1 ]]; then
  for BRANCH in "${BRANCHES[@]}"; do
    section "5. opaque-recursive-lens --terminal-reduction --branch-recursion $BRANCH"
    python -m pet.cli opaque-recursive-lens "$N" \
      --max-generator-count "$MAX_GENERATOR_COUNT" \
      --excluded-support-limit "$EXCLUDED_SUPPORT_LIMIT" \
      --max-move-span "$MAX_MOVE_SPAN" \
      --depth "$DEPTH" \
      --terminal-reduction \
      --anchor-field \
      --composite-edge-peel \
      --branch-recursion "$BRANCH" \
      "${JSON_ARG[@]}"
  done
fi
