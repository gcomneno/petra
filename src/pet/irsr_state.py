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
            if slot["domain"]["candidates"]:
                raise ValueError(f"slot already initialized: {slot_name}")
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



def residual_state_can_branch_on_slot(state: dict, slot_name: str) -> bool:
    if state.get("refinement", {}).get("status") == "contradiction":
        return False

    for slot in state["slots"]:
        if slot.get("slot") == slot_name:
            return len(slot["domain"]["candidates"]) > 1

    raise KeyError(f"unknown slot: {slot_name}")



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



def branch_residual_state_on_slot_candidates(state: dict, slot_name: str) -> list[dict]:
    if state.get("refinement", {}).get("status") == "contradiction":
        raise ValueError("state is in contradiction")
    if not residual_state_can_branch_on_slot(state, slot_name):
        raise ValueError("slot is not branchable")

    branches: list[dict] = []

    slot_candidates = None
    for slot in state["slots"]:
        if slot.get("slot") == slot_name:
            slot_candidates = list(slot["domain"]["candidates"])
            break
    else:
        raise KeyError(f"unknown slot: {slot_name}")

    for candidate in slot_candidates:
        branch = deepcopy(state)

        for slot in branch["slots"]:
            if slot.get("slot") == slot_name:
                slot["domain"]["candidates"] = [candidate]
                break

        payload = residual_state_to_support_payload_slice(branch)
        branch["refinement"]["payload_ready"] = payload_slice_is_builder_usable(payload)
        branch["refinement"]["status"] = (
            "payload-ready" if branch["refinement"]["payload_ready"] else "open"
        )

        branches.append(branch)

    return branches
