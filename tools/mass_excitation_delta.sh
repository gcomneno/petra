#!/usr/bin/env bash
set -euo pipefail

FULL="${1:?usage: tools/mass_excitation_delta.sh FULL FACTOR}"
FACTOR="${2:?usage: tools/mass_excitation_delta.sh FULL FACTOR}"

EXCLUDED_SUPPORT_LIMIT="${EXCLUDED_SUPPORT_LIMIT:-16}"
MAX_GENERATOR_COUNT="${MAX_GENERATOR_COUNT:-20}"
SPANS="${SPANS:-1 2 3 5 8 13}"

if (( FACTOR <= 1 )); then
  echo "error: FACTOR must be > 1" >&2
  exit 2
fi

if (( FULL % FACTOR != 0 )); then
  echo "error: FACTOR does not divide FULL" >&2
  exit 2
fi

PEELED=$(( FULL / FACTOR ))

summary_for() {
  local n="$1"

  SPANS="$SPANS" \
  EXCLUDED_SUPPORT_LIMIT="$EXCLUDED_SUPPORT_LIMIT" \
  MAX_GENERATOR_COUNT="$MAX_GENERATOR_COUNT" \
  tools/mass_excitation_sweep.sh "$n" \
  | awk '
      /^  status = / { status=$3 }
      /^  onset_span = / { onset_span=$3 }
      /^  onset_k_range = / { onset_k_range=$3 }
      /^  onset_width = / { onset_width=$3 }
      /^  saturation_span = / { saturation_span=$3 }
      /^  saturation_k_range = / { saturation_k_range=$3 }
      /^  saturation_width = / { saturation_width=$3 }
      END {
        if (status == "") status="unknown"
        if (onset_span == "") onset_span="none"
        if (onset_k_range == "") onset_k_range="none"
        if (onset_width == "") onset_width="none"
        if (saturation_span == "") saturation_span="none"
        if (saturation_k_range == "") saturation_k_range="none"
        if (saturation_width == "") saturation_width="none"
        printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n", status, onset_span, onset_k_range, onset_width, saturation_span, saturation_k_range, saturation_width
      }
    '
}

baseline="$(summary_for "$FULL")"
peeled="$(summary_for "$PEELED")"

IFS=$'\t' read -r b_status b_onset_span b_onset_range b_onset_width b_sat_span b_sat_range b_sat_width <<< "$baseline"
IFS=$'\t' read -r p_status p_onset_span p_onset_range p_onset_width p_sat_span p_sat_range p_sat_width <<< "$peeled"

extinction="no"
if [[ "$b_status" == "present" && "$p_status" == "none" ]]; then
  extinction="yes"
fi

changed="no"
if [[ "$b_onset_span" != "$p_onset_span" || "$b_onset_range" != "$p_onset_range" || "$b_sat_span" != "$p_sat_span" || "$b_sat_range" != "$p_sat_range" ]]; then
  changed="yes"
fi

echo "PET MASS EXCITATION DELTA"
echo
echo "FULL=$FULL"
echo "FACTOR=$FACTOR"
echo "PEELED=$PEELED"
echo "excluded_support_limit=$EXCLUDED_SUPPORT_LIMIT"
echo "max_generator_count=$MAX_GENERATOR_COUNT"
echo "spans=$SPANS"
echo
echo "Baseline resonance"
echo "  status = $b_status"
echo "  onset_span = $b_onset_span"
echo "  onset_k_range = $b_onset_range"
echo "  onset_width = $b_onset_width"
echo "  saturation_span = $b_sat_span"
echo "  saturation_k_range = $b_sat_range"
echo "  saturation_width = $b_sat_width"
echo
echo "Peeled resonance"
echo "  status = $p_status"
echo "  onset_span = $p_onset_span"
echo "  onset_k_range = $p_onset_range"
echo "  onset_width = $p_onset_width"
echo "  saturation_span = $p_sat_span"
echo "  saturation_k_range = $p_sat_range"
echo "  saturation_width = $p_sat_width"
echo
echo "Delta verdict"
echo "  changed = $changed"
echo "  extinction = $extinction"
echo "  claim = PET mass excitation delta only; this does not discover or prove factors"
