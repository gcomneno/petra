#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  tools/pet_triage_pipeline.sh N [options]

Options:
  --max-generator-count K       default: 40
  --excluded-support-limit LIM  default: 100000000
  --max-move-span S             default: 5
  --depth D                     default: 3
  --handoff-radius R            default: 100
  --operator-depth D            proposal operator depth; default: auto
  --blade-window MODE           proposal blade window: full|active; default: full
  --json                        emit JSON from PET commands
  --fork-follow SIDE            run legacy fork follow-up diagnostics for NEW, DROP, or BOTH; default: BOTH
  --no-fork-follow              skip legacy fork follow-up diagnostics
  --no-fork                     skip legacy focused peel fork diagnostics
  --no-scan-summary             skip PET verified divisor summary
  --no-classic-scan             skip PET verified divisor summary and classic scan policy
  --route-only                  run only PET race diagnostic and classic handoff policy
  --legacy-diagnostics          run legacy diagnostics sections 4-8
  --rigid-border-guard          stop after preflight when decimal rigid border is detected
  --decimal-rigid-shallow-route emit a conservative shallow route for decimal rigid borders
  --no-monster-router         skip PET shadow monster router preflight
  --no-recursive                skip legacy recursive diagnostics

Examples:
  tools/pet_triage_pipeline.sh 10403 --max-generator-count 4 --excluded-support-limit 16 --max-move-span 2

  tools/pet_triage_pipeline.sh "$RSA250" --depth 3
EOF
}

N=""
MAX_GENERATOR_COUNT=40
EXCLUDED_SUPPORT_LIMIT=100000000
MAX_MOVE_SPAN=5
DEPTH=3
HANDOFF_RADIUS=100
OPERATOR_DEPTH=auto
BLADE_WINDOW=full
JSON=0
RUN_FORK=1
RUN_FORK_FOLLOW=1
FORK_FOLLOW=BOTH
RUN_RECURSIVE=1
RUN_SCAN_SUMMARY=1
RUN_CLASSIC_SCAN_POLICY=1
RUN_LEGACY_LENS=0
RUN_LEGACY_MASS=0
RUN_LEGACY_FOCUSED=0
RUN_RIGID_BORDER_GUARD=0
RUN_DECIMAL_RIGID_SHALLOW_ROUTE=0
RUN_MONSTER_ROUTER=1

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
    --operator-depth)
      OPERATOR_DEPTH="$2"
      shift 2
      ;;
    --blade-window)
      BLADE_WINDOW="$2"
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
    --no-scan-summary)
      RUN_SCAN_SUMMARY=0
      shift
      ;;
    --no-classic-scan)
      RUN_SCAN_SUMMARY=0
      RUN_CLASSIC_SCAN_POLICY=0
      shift
      ;;
    --route-only)
      RUN_SCAN_SUMMARY=0
      RUN_CLASSIC_SCAN_POLICY=0
      RUN_LEGACY_LENS=0
      RUN_LEGACY_MASS=0
      RUN_LEGACY_FOCUSED=0
      RUN_FORK=0
      RUN_FORK_FOLLOW=0
      RUN_RECURSIVE=0
      shift
      ;;
    --legacy-diagnostics)
      RUN_LEGACY_LENS=1
      RUN_LEGACY_MASS=1
      RUN_LEGACY_FOCUSED=1
      shift
      ;;
    --rigid-border-guard)
      RUN_RIGID_BORDER_GUARD=1
      shift
      ;;
    --decimal-rigid-shallow-route)
      RUN_DECIMAL_RIGID_SHALLOW_ROUTE=1
      shift
      ;;
    --no-monster-router)
      RUN_MONSTER_ROUTER=0
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

run_optional() {
  local status=0
  local output_file
  output_file="$(mktemp)"

  "$@" >"$output_file" 2>&1 || status=$?

  if [[ "$status" -eq 0 ]]; then
    sed \
      -e 's/^source_reason \([^=]*\) = ERROR: /legacy_source_warning \1 = /' \
      -e 's/^reason = ERROR: /legacy_reason = /' \
      "$output_file"
    rm -f "$output_file"
    return 0
  fi

  echo "stage_status = unavailable"
  echo "reason = optional diagnostic command failed"
  echo "exit_status = $status"

  local diagnostic_error
  diagnostic_error="$(sed -n '/[^[:space:]]/p' "$output_file" | head -n 1 | sed 's/^ERROR: //')"
  if [[ -n "$diagnostic_error" ]]; then
    echo "diagnostic_error = $diagnostic_error"
  fi

  rm -f "$output_file"
  return 0
}

echo "PET TRIAGE PIPELINE"
echo "N_digits = ${#N}"
echo "max_generator_count = $MAX_GENERATOR_COUNT"
echo "excluded_support_limit = $EXCLUDED_SUPPORT_LIMIT"
echo "max_move_span = $MAX_MOVE_SPAN"
echo "depth = $DEPTH"
echo "handoff_radius = $HANDOFF_RADIUS"
echo "monster_router = $RUN_MONSTER_ROUTER"
echo "operator_depth = $OPERATOR_DEPTH"
echo "blade_window = $BLADE_WINDOW"
echo "legacy_fork_follow = ${FORK_FOLLOW:-disabled}"
echo
echo "claim = PET triage pipeline only; classic stages verify divisors only when explicitly reported"

proposal_file="$(mktemp)"
decimal_boundary_file="$(mktemp)"
trap 'rm -f "$proposal_file" "$decimal_boundary_file"' EXIT

section "0. PET decimal boundary preflight"
tools/research/pet_decimal_boundary_study.py "$N" | tee "$decimal_boundary_file"
decimal_rigid_border_hint="$(awk 'NR == 2 {print $NF}' "$decimal_boundary_file")"
if [[ "$RUN_RIGID_BORDER_GUARD" -eq 1 && "$decimal_rigid_border_hint" == "yes" ]]; then
  echo
  echo "preflight_guard_status = stopped"
  echo "preflight_guard_kind = decimal-rigid-border"
  echo "reason = decimal rigid border detected; skipping PET race diagnostic"
  echo "preflight_guard_suggested_next = use shallow decimal-rigid route or rerun without --rigid-border-guard to force PET race"
  echo "claim = PET decimal boundary preflight only; this does not factor N"
  exit 0
fi
if [[ "$RUN_DECIMAL_RIGID_SHALLOW_ROUTE" -eq 1 && "$decimal_rigid_border_hint" == "yes" ]]; then
  echo
  echo "shallow_route_status = available"
  echo "shallow_route_kind = decimal-rigid-border-shallow-classic-probe"
  echo "reason = decimal rigid border detected; using conservative shallow route without PET race diagnostic"
  echo "suggested_command = python -m pet.cli opaque-probe $N --trial-limit 20"
  echo "claim = PET decimal rigid shallow route only; classic verification required"
  exit 0
fi

if [[ "$RUN_MONSTER_ROUTER" -eq 1 ]]; then
  section "0b. PET shadow monster router"
  run_optional tools/research/pet_shadow_monster_router.py "$N" --progress
fi

section "0. PET race diagnostic"
tools/pet_local_probe_proposal.py "$N"   --operator-depth "$OPERATOR_DEPTH"   --backbone-selection race   --blade-window "$BLADE_WINDOW" | tee "$proposal_file"

section "1. PET classic handoff policy"
tools/pet_classic_handoff_route.py "$N"   --proposal-file "$proposal_file"   --operator-depth "$OPERATOR_DEPTH"   --blade-window "$BLADE_WINDOW"   --max-generator-count "$MAX_GENERATOR_COUNT"   --excluded-support-limit "$EXCLUDED_SUPPORT_LIMIT"   --max-move-span "$MAX_MOVE_SPAN"

if [[ "$RUN_SCAN_SUMMARY" -eq 1 ]]; then
  section "2. PET verified divisor summary"
  run_optional tools/pet_classic_scan_summary.py "$N"
fi

if [[ "$RUN_CLASSIC_SCAN_POLICY" -eq 1 ]]; then
  section "3. PET classic scan policy"
  run_optional tools/pet_classic_scan_policy.py "$N"
fi

if [[ "$RUN_LEGACY_LENS" -eq 1 ]]; then
  section "4. Legacy lens hint"
  run_optional tools/pet_lens_hint.py "$N"   --schedule-limit 8   --max-leaves 8   --summary

  section "5. Legacy lens candidates"
  run_optional tools/pet_lens_candidates.py "$N"   --max-leaves 8

  section "6. Legacy lens transition"
  run_optional tools/pet_lens_transition.py "$N"   --max-leaves 8
fi

if [[ "$RUN_LEGACY_MASS" -eq 1 ]]; then
  section "7. Legacy mass response"
  run_optional python -m pet.cli opaque-mass-response "$N"   --max-generator-count "$MAX_GENERATOR_COUNT"   --excluded-support-limit "$EXCLUDED_SUPPORT_LIMIT"   --max-move-span "$MAX_MOVE_SPAN"   --bands   "${JSON_ARG[@]}"
fi

if [[ "$RUN_LEGACY_FOCUSED" -eq 1 ]]; then
  section "8. Legacy focused peel classic handoff diagnostic"
  run_optional python -m pet.cli opaque-focused-peel "$N"   --max-generator-count "$MAX_GENERATOR_COUNT"   --excluded-support-limit "$EXCLUDED_SUPPORT_LIMIT"   --max-move-span "$MAX_MOVE_SPAN"   --classic-handoff   --handoff-radius "$HANDOFF_RADIUS"   "${JSON_ARG[@]}"
fi

if [[ "$RUN_FORK" -eq 1 ]]; then
  section "9. Legacy focused peel fork diagnostic"
  run_optional python -m pet.cli opaque-focused-peel "$N"     --max-generator-count "$MAX_GENERATOR_COUNT"     --excluded-support-limit "$EXCLUDED_SUPPORT_LIMIT"     --max-move-span "$MAX_MOVE_SPAN"     --fork     "${JSON_ARG[@]}"
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
    section "10. Legacy fork-follow diagnostic $BRANCH"
    run_optional python -m pet.cli opaque-focused-peel "$N"       --max-generator-count "$MAX_GENERATOR_COUNT"       --excluded-support-limit "$EXCLUDED_SUPPORT_LIMIT"       --max-move-span "$MAX_MOVE_SPAN"       --fork-follow "$BRANCH"       "${JSON_ARG[@]}"
  done
fi

if [[ "$RUN_RECURSIVE" -eq 1 ]]; then
  for BRANCH in "${BRANCHES[@]}"; do
    section "11. Legacy recursive lens diagnostic $BRANCH"
    run_optional python -m pet.cli opaque-recursive-lens "$N"       --max-generator-count "$MAX_GENERATOR_COUNT"       --excluded-support-limit "$EXCLUDED_SUPPORT_LIMIT"       --max-move-span "$MAX_MOVE_SPAN"       --depth "$DEPTH"       --terminal-reduction       --anchor-field       --composite-edge-peel       --branch-recursion "$BRANCH"       "${JSON_ARG[@]}"
  done
fi
