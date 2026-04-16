from copy import deepcopy


def residual_state_to_support_payload_slice(state: dict) -> dict:
    skeleton = state["skeleton"]
    coupling = state["coupling"]

    return {
        "support_size": skeleton["support_size"],
        "exponent_profile": list(skeleton["exponent_profile"]),
        "slots": deepcopy(state["slots"]),
        "joint_pet_constraints": deepcopy(coupling["joint_pet_constraints"]),
        "forbidden_patterns": deepcopy(coupling["forbidden_patterns"]),
    }


def payload_slice_builder_unusable_reasons(payload: dict) -> list[str]:
    reasons: list[str] = []

    slots = payload.get("slots")
    support_size = payload.get("support_size")
    exponent_profile = payload.get("exponent_profile")

    if not isinstance(slots, list):
        return ["slots:not-a-list"]

    if support_size != len(slots):
        reasons.append("support-size:does-not-match-slots")

    if not isinstance(exponent_profile, list):
        reasons.append("exponent-profile:not-a-list")
    elif len(exponent_profile) != len(slots):
        reasons.append("exponent-profile:does-not-match-slots")

    for index, slot in enumerate(slots):
        slot_name = slot.get("slot", f"index-{index}")

        if slot.get("kind") != "prime":
            reasons.append(f"slot:{slot_name}:kind-is-not-prime")
            continue

        domain = slot.get("domain")
        if not isinstance(domain, dict):
            reasons.append(f"slot:{slot_name}:domain-not-a-dict")
            continue

        candidates = domain.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            reasons.append(f"slot:{slot_name}:missing-explicit-candidates")

    return reasons


def payload_slice_is_builder_usable(payload: dict) -> bool:
    return payload_slice_builder_unusable_reasons(payload) == []


def payload_slice_to_builder_payload(payload: dict) -> dict:
    reasons = payload_slice_builder_unusable_reasons(payload)
    if reasons:
        raise ValueError(
            "payload slice is not builder-usable: " + ", ".join(reasons)
        )

    return {
        "support_size": payload["support_size"],
        "exponent_profile": list(payload["exponent_profile"]),
        "prime_slots": [
            {
                "slot": slot["slot"],
                "candidates": deepcopy(slot["domain"]["candidates"]),
            }
            for slot in payload["slots"]
        ],
        "joint_pet_constraints": deepcopy(payload["joint_pet_constraints"]),
        "forbidden_patterns": deepcopy(payload["forbidden_patterns"]),
    }
