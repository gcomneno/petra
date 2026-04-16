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
