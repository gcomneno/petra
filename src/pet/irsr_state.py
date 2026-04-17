from copy import deepcopy


def _policy_name(refiner) -> str:
    return getattr(refiner, "__name__", "<anonymous>")



def make_hostile_semiprime_residual_state(n: int | str) -> dict:
    return {
        "target": {
            "n": str(n),
        },
        "skeleton": {
            "support_size": 2,
            "exponent_profile": [1, 1],
            "squarefree": True,
            "normalized_order": "a<=b",
        },
        "slots": [
            {
                "slot": "a",
                "kind": "prime",
                "domain": {
                    "type": "range_or_candidates",
                    "min": None,
                    "max": None,
                    "candidates": [],
                },
                "pet_hints": {
                    "near_generator": [],
                    "block_shape": [],
                },
            },
            {
                "slot": "b",
                "kind": "prime",
                "domain": {
                    "type": "range_or_candidates",
                    "min": None,
                    "max": None,
                    "candidates": [],
                },
                "pet_hints": {
                    "near_generator": [],
                    "block_shape": [],
                },
            },
        ],
        "coupling": {
            "product_constraint": "a*b=n",
            "joint_pet_constraints": [],
            "forbidden_patterns": [],
        },
        "refinement": {
            "iteration": 0,
            "status": "open",
            "payload_ready": False,
        },
    }


def try_seed_residual_state_slot_candidates(
    state: dict, slot_name: str, candidates: list[int]
) -> dict | None:
    for slot in state["slots"]:
        if slot.get("slot") == slot_name:
            if slot["domain"]["candidates"]:
                return None
            return refine_residual_state_slot_candidates(state, slot_name, candidates)

    raise KeyError(f"unknown slot: {slot_name}")


def empty_residual_state_slots(state: dict) -> list[str]:
    return [
        slot["slot"]
        for slot in state["slots"]
        if not slot["domain"]["candidates"]
    ]


def make_seed_slot_policy(
    slot_name: str, candidates: list[int], policy_name: str | None = None
):
    def _policy(state: dict):
        return try_seed_residual_state_slot_candidates(state, slot_name, candidates)

    _policy.__name__ = policy_name or f"seed_{slot_name}"
    return _policy


def make_seed_first_empty_slot_policy(
    candidates: list[int], policy_name: str | None = None
):
    def _policy(state: dict):
        empty_slots = empty_residual_state_slots(state)
        if not empty_slots:
            return None
        return try_seed_residual_state_slot_candidates(
            state, empty_slots[0], candidates
        )

    _policy.__name__ = policy_name or "seed_first_empty_slot"
    return _policy


def try_refine_open_residual_state_with_policy_chain(
    state: dict, refiners
) -> dict | None:
    for refiner in refiners:
        refined = refiner(deepcopy(state))
        if refined is not None:
            return {
                "refiner": _policy_name(refiner),
                "state": refined,
            }

    return None



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



def residual_state_branchable_slots(state: dict) -> list[str]:
    if state.get("refinement", {}).get("status") == "contradiction":
        return []

    return [
        slot["slot"]
        for slot in state["slots"]
        if len(slot["domain"]["candidates"]) > 1
    ]



def choose_branch_slot(state: dict) -> str | None:
    slots = residual_state_branchable_slots(state)
    return slots[0] if slots else None



def branch_residual_state(state: dict) -> list[dict]:
    slot_name = choose_branch_slot(state)
    if slot_name is None:
        return []

    return branch_residual_state_on_slot_candidates(state, slot_name)



def classify_residual_state(state: dict) -> str:
    if state.get("refinement", {}).get("status") == "contradiction":
        return "contradiction"
    if residual_state_is_builder_ready(state):
        return "payload-ready"
    if residual_state_branchable_slots(state):
        return "branchable"
    return "open"



def summarize_residual_state_frontier(states: list[dict]) -> dict:
    summary = {
        "total": len(states),
        "open": 0,
        "branchable": 0,
        "payload_ready": 0,
        "contradiction": 0,
    }

    for state in states:
        classification = classify_residual_state(state)
        if classification == "payload-ready":
            summary["payload_ready"] += 1
        elif classification in summary:
            summary[classification] += 1
        else:
            raise ValueError(f"unknown state classification: {classification}")

    return summary



def advance_residual_state_once(state: dict) -> dict:
    classification = classify_residual_state(state)

    if classification == "contradiction":
        return {
            "action": "stop",
            "reason": "contradiction",
        }

    if classification == "payload-ready":
        return {
            "action": "promote",
            "builder_payload": residual_state_to_builder_payload(state),
        }

    if classification == "branchable":
        slot = choose_branch_slot(state)
        return {
            "action": "branch",
            "slot": slot,
            "branches": branch_residual_state(state),
        }

    return {
        "action": "idle",
        "reason": "open-without-branching-policy",
    }


def advance_residual_state_once_with_policy(
    state: dict, open_state_refiner=None
) -> dict:
    base = advance_residual_state_once(state)

    if base["action"] != "idle":
        return base

    if open_state_refiner is None:
        return base

    refined = open_state_refiner(deepcopy(state))
    if refined is None:
        return base

    return {
        "action": "refine",
        "state": refined,
    }


def advance_residual_state_once_with_policy_chain(state: dict, refiners) -> dict:
    base = advance_residual_state_once(state)

    if base["action"] != "idle":
        return base

    result = try_refine_open_residual_state_with_policy_chain(state, refiners)
    if result is None:
        return base

    return {
        "action": "refine",
        "refiner": result["refiner"],
        "state": result["state"],
    }



def advance_residual_state_frontier_once(states: list[dict]) -> dict:
    if not states:
        return {
            "consumed": 0,
            "remaining": [],
            "emitted": [],
            "promoted": [],
            "stopped": [],
            "idle": [],
        }

    current = deepcopy(states[0])
    remaining = deepcopy(states[1:])

    result = {
        "consumed": 1,
        "remaining": remaining,
        "emitted": [],
        "promoted": [],
        "stopped": [],
        "idle": [],
    }

    decision = advance_residual_state_once(current)

    if decision["action"] == "branch":
        result["emitted"] = decision["branches"]
    elif decision["action"] == "promote":
        result["promoted"] = [decision["builder_payload"]]
    elif decision["action"] == "stop":
        result["stopped"] = [current]
    elif decision["action"] == "idle":
        result["idle"] = [current]
    else:
        raise ValueError(f"unknown frontier action: {decision['action']}")

    return result



def build_next_residual_state_frontier(step_result: dict) -> list[dict]:
    return (
        deepcopy(step_result["remaining"])
        + deepcopy(step_result["emitted"])
        + deepcopy(step_result["idle"])
    )



def advance_residual_state_frontier_n_steps(states: list[dict], steps: int) -> dict:
    if steps < 0:
        raise ValueError("steps must be >= 0")

    frontier = deepcopy(states)
    promoted: list[dict] = []
    stopped: list[dict] = []
    idle: list[dict] = []
    trace: list[dict] = []

    steps_run = 0

    for _ in range(steps):
        if not frontier:
            break

        step_result = advance_residual_state_frontier_once(frontier)
        steps_run += step_result["consumed"]

        if step_result["emitted"]:
            trace.append(
                {
                    "step": steps_run,
                    "action": "branch",
                    "emitted": len(step_result["emitted"]),
                }
            )
        elif step_result["promoted"]:
            trace.append({"step": steps_run, "action": "promote"})
        elif step_result["stopped"]:
            trace.append({"step": steps_run, "action": "stop"})
        elif step_result["idle"]:
            trace.append({"step": steps_run, "action": "idle"})

        promoted.extend(deepcopy(step_result["promoted"]))
        stopped.extend(deepcopy(step_result["stopped"]))
        idle.extend(deepcopy(step_result["idle"]))

        frontier = build_next_residual_state_frontier(step_result)

    termination_reason = (
        "frontier-exhausted" if not frontier else "step-budget-exhausted"
    )

    return {
        "steps_run": steps_run,
        "frontier": frontier,
        "frontier_summary": summarize_residual_state_frontier(frontier),
        "promoted": promoted,
        "stopped": stopped,
        "idle": idle,
        "trace": trace,
        "termination_reason": termination_reason,
    }



def run_residual_state_frontier_until_quiescence(
    states: list[dict], max_steps: int
) -> dict:
    if max_steps < 0:
        raise ValueError("max_steps must be >= 0")

    frontier = deepcopy(states)
    promoted: list[dict] = []
    stopped: list[dict] = []
    idle: list[dict] = []
    trace: list[dict] = []

    steps_run = 0

    while frontier and steps_run < max_steps:
        sweep_len = len(frontier)
        sweep_actions: list[str] = []

        for _ in range(sweep_len):
            if not frontier or steps_run >= max_steps:
                break

            step_result = advance_residual_state_frontier_once(frontier)
            steps_run += step_result["consumed"]

            if step_result["emitted"]:
                trace.append(
                    {
                        "step": steps_run,
                        "action": "branch",
                        "emitted": len(step_result["emitted"]),
                    }
                )
                sweep_actions.append("branch")
            elif step_result["promoted"]:
                trace.append({"step": steps_run, "action": "promote"})
                sweep_actions.append("promote")
            elif step_result["stopped"]:
                trace.append({"step": steps_run, "action": "stop"})
                sweep_actions.append("stop")
            elif step_result["idle"]:
                trace.append({"step": steps_run, "action": "idle"})
                sweep_actions.append("idle")

            promoted.extend(deepcopy(step_result["promoted"]))
            stopped.extend(deepcopy(step_result["stopped"]))
            idle.extend(deepcopy(step_result["idle"]))

            frontier = build_next_residual_state_frontier(step_result)

        if not frontier:
            termination_reason = "frontier-exhausted"
            break

        if steps_run >= max_steps:
            termination_reason = "step-budget-exhausted"
            break

        if sweep_actions and all(action == "idle" for action in sweep_actions):
            termination_reason = "quiescent-idle-frontier"
            break
    else:
        termination_reason = (
            "frontier-exhausted" if not frontier else "step-budget-exhausted"
        )

    return {
        "steps_run": steps_run,
        "frontier": frontier,
        "frontier_summary": summarize_residual_state_frontier(frontier),
        "promoted": promoted,
        "stopped": stopped,
        "idle": idle,
        "trace": trace,
        "termination_reason": termination_reason,
    }


def run_residual_state_frontier_until_quiescence_with_policy(
    states: list[dict], max_steps: int, open_state_refiner=None
) -> dict:
    if max_steps < 0:
        raise ValueError("max_steps must be >= 0")

    frontier = deepcopy(states)
    promoted: list[dict] = []
    stopped: list[dict] = []
    idle: list[dict] = []
    trace: list[dict] = []

    steps_run = 0

    while frontier and steps_run < max_steps:
        sweep_len = len(frontier)
        sweep_actions: list[str] = []

        for _ in range(sweep_len):
            if not frontier or steps_run >= max_steps:
                break

            current = deepcopy(frontier[0])
            remaining = deepcopy(frontier[1:])
            decision = advance_residual_state_once_with_policy(
                current, open_state_refiner
            )
            steps_run += 1

            if decision["action"] == "branch":
                trace.append(
                    {
                        "step": steps_run,
                        "action": "branch",
                        "emitted": len(decision["branches"]),
                    }
                )
                sweep_actions.append("branch")
                frontier = remaining + deepcopy(decision["branches"])
            elif decision["action"] == "promote":
                trace.append({"step": steps_run, "action": "promote"})
                sweep_actions.append("promote")
                promoted.append(deepcopy(decision["builder_payload"]))
                frontier = remaining
            elif decision["action"] == "stop":
                trace.append({"step": steps_run, "action": "stop"})
                sweep_actions.append("stop")
                stopped.append(current)
                frontier = remaining
            elif decision["action"] == "refine":
                trace.append({"step": steps_run, "action": "refine"})
                sweep_actions.append("refine")
                frontier = remaining + [deepcopy(decision["state"])]
            elif decision["action"] == "idle":
                trace.append({"step": steps_run, "action": "idle"})
                sweep_actions.append("idle")
                idle.append(current)
                frontier = remaining + [current]
            else:
                raise ValueError(f"unknown policy-aware action: {decision['action']}")

        if not frontier:
            termination_reason = "frontier-exhausted"
            break

        if steps_run >= max_steps:
            termination_reason = "step-budget-exhausted"
            break

        if sweep_actions and all(action == "idle" for action in sweep_actions):
            termination_reason = "quiescent-idle-frontier"
            break
    else:
        termination_reason = (
            "frontier-exhausted" if not frontier else "step-budget-exhausted"
        )

    return {
        "steps_run": steps_run,
        "frontier": frontier,
        "frontier_summary": summarize_residual_state_frontier(frontier),
        "promoted": promoted,
        "stopped": stopped,
        "idle": idle,
        "trace": trace,
        "termination_reason": termination_reason,
    }


def run_residual_state_frontier_until_quiescence_with_policy_chain(
    states: list[dict], max_steps: int, refiners
) -> dict:
    if max_steps < 0:
        raise ValueError("max_steps must be >= 0")

    frontier = deepcopy(states)
    promoted: list[dict] = []
    stopped: list[dict] = []
    idle: list[dict] = []
    trace: list[dict] = []

    steps_run = 0

    while frontier and steps_run < max_steps:
        sweep_len = len(frontier)
        sweep_actions: list[str] = []

        for _ in range(sweep_len):
            if not frontier or steps_run >= max_steps:
                break

            current = deepcopy(frontier[0])
            remaining = deepcopy(frontier[1:])
            decision = advance_residual_state_once_with_policy_chain(
                current, refiners
            )
            steps_run += 1

            if decision["action"] == "branch":
                trace.append(
                    {
                        "step": steps_run,
                        "action": "branch",
                        "emitted": len(decision["branches"]),
                    }
                )
                sweep_actions.append("branch")
                frontier = remaining + deepcopy(decision["branches"])
            elif decision["action"] == "promote":
                trace.append({"step": steps_run, "action": "promote"})
                sweep_actions.append("promote")
                promoted.append(deepcopy(decision["builder_payload"]))
                frontier = remaining
            elif decision["action"] == "stop":
                trace.append({"step": steps_run, "action": "stop"})
                sweep_actions.append("stop")
                stopped.append(current)
                frontier = remaining
            elif decision["action"] == "refine":
                trace.append(
                    {
                        "step": steps_run,
                        "action": "refine",
                        "refiner": decision["refiner"],
                    }
                )
                sweep_actions.append("refine")
                frontier = remaining + [deepcopy(decision["state"])]
            elif decision["action"] == "idle":
                trace.append({"step": steps_run, "action": "idle"})
                sweep_actions.append("idle")
                idle.append(current)
                frontier = remaining + [current]
            else:
                raise ValueError(
                    f"unknown policy-chain action: {decision['action']}"
                )

        if not frontier:
            termination_reason = "frontier-exhausted"
            break

        if steps_run >= max_steps:
            termination_reason = "step-budget-exhausted"
            break

        if sweep_actions and all(action == "idle" for action in sweep_actions):
            termination_reason = "quiescent-idle-frontier"
            break
    else:
        termination_reason = (
            "frontier-exhausted" if not frontier else "step-budget-exhausted"
        )

    return {
        "steps_run": steps_run,
        "frontier": frontier,
        "frontier_summary": summarize_residual_state_frontier(frontier),
        "promoted": promoted,
        "stopped": stopped,
        "idle": idle,
        "trace": trace,
        "termination_reason": termination_reason,
    }



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

        branch["refinement"]["iteration"] += 1

        payload = residual_state_to_support_payload_slice(branch)
        branch["refinement"]["payload_ready"] = payload_slice_is_builder_usable(payload)
        branch["refinement"]["status"] = (
            "payload-ready" if branch["refinement"]["payload_ready"] else "open"
        )

        branches.append(branch)

    return branches
