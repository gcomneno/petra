from copy import deepcopy

from pet.irsr_payload_slice import (
    payload_slice_builder_unusable_reasons,
    payload_slice_is_builder_usable,
    payload_slice_to_builder_payload,
    residual_state_to_support_payload_slice,
)


def refine_residual_state_slot_candidates(
    state: dict, slot_name: str, candidates: list[int]
) -> dict:
    refined = deepcopy(state)

    normalized_candidates = sorted(set(candidates))

    for slot in refined["slots"]:
        if slot.get("slot") == slot_name:
            slot["domain"]["candidates"] = normalized_candidates
            break
    else:
        raise KeyError(f"unknown slot: {slot_name}")

    refined["refinement"]["iteration"] += 1

    payload = residual_state_to_support_payload_slice(refined)
    refined["refinement"]["payload_ready"] = payload_slice_is_builder_usable(payload)
    refined["refinement"]["status"] = (
        "payload-ready" if refined["refinement"]["payload_ready"] else "open"
    )

    return refined


def residual_state_to_builder_payload(state: dict) -> dict:
    payload_slice = residual_state_to_support_payload_slice(state)
    return payload_slice_to_builder_payload(payload_slice)


def residual_state_builder_unready_reasons(state: dict) -> list[str]:
    if state.get("refinement", {}).get("status") == "contradiction":
        return ["state:contradiction"]

    payload_slice = residual_state_to_support_payload_slice(state)
    return payload_slice_builder_unusable_reasons(payload_slice)


def residual_state_is_builder_ready(state: dict) -> bool:
    return residual_state_builder_unready_reasons(state) == []


def residual_state_can_refine(state: dict) -> bool:
    status = state.get("refinement", {}).get("status")
    return status not in {"payload-ready", "contradiction"}



def intersect_residual_state_slot_candidates(
    state: dict, slot_name: str, candidates: list[int]
) -> dict:
    refined = deepcopy(state)

    normalized_candidates = sorted(set(candidates))
    contradiction = False

    for slot in refined["slots"]:
        if slot.get("slot") == slot_name:
            current = slot["domain"]["candidates"]
            if current:
                narrowed = sorted(set(current).intersection(normalized_candidates))
                slot["domain"]["candidates"] = narrowed
                contradiction = len(narrowed) == 0
            else:
                slot["domain"]["candidates"] = normalized_candidates
            break
    else:
        raise KeyError(f"unknown slot: {slot_name}")

    refined["refinement"]["iteration"] += 1

    payload = residual_state_to_support_payload_slice(refined)
    refined["refinement"]["payload_ready"] = (
        False if contradiction else payload_slice_is_builder_usable(payload)
    )
    refined["refinement"]["status"] = (
        "contradiction"
        if contradiction
        else ("payload-ready" if refined["refinement"]["payload_ready"] else "open")
    )

    return refined
