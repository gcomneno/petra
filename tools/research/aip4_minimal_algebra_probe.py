from __future__ import annotations

from collections import defaultdict, deque
from functools import lru_cache

Tree = tuple["Tree", ...]
Path = tuple[int, ...]

Z: Tree = ()
MAX_SIZE = 6


def key(tree: Tree) -> tuple:
    return tuple(key(child) for child in tree)


def canonical(children: tuple[Tree, ...] | list[Tree]) -> Tree:
    return tuple(sorted(children, key=key))


def size(tree: Tree) -> int:
    return 1 + sum(size(child) for child in tree)


def paths(tree: Tree, prefix: Path = ()) -> list[Path]:
    result = [prefix]
    for index, child in enumerate(tree):
        result.extend(paths(child, prefix + (index,)))
    return result


def subtree(tree: Tree, path: Path) -> Tree:
    current = tree
    for index in path:
        current = current[index]
    return current


def replace_at(tree: Tree, path: Path, replacement: Tree) -> Tree:
    if not path:
        return replacement
    index = path[0]
    children = list(tree)
    children[index] = replace_at(children[index], path[1:], replacement)
    return canonical(children)


def add_node_at(tree: Tree, path: Path) -> Tree:
    target = subtree(tree, path)
    return replace_at(tree, path, canonical((*target, Z)))


def removable_leaf_paths(tree: Tree) -> list[Path]:
    result: list[Path] = []
    for path in paths(tree):
        if path and subtree(tree, path) == Z:
            result.append(path)
    return result


def remove_leaf_at(tree: Tree, path: Path) -> Tree:
    if not path:
        raise ValueError("root cannot be removed")
    parent_path = path[:-1]
    index = path[-1]
    parent = subtree(tree, parent_path)
    if parent[index] != Z:
        raise ValueError("REMOVE_LEAF target must be zero-child")
    new_children = list(parent)
    del new_children[index]
    return replace_at(tree, parent_path, canonical(new_children))


def add_successors(tree: Tree) -> set[Tree]:
    return {add_node_at(tree, path) for path in paths(tree)}


def remove_successors(tree: Tree) -> set[Tree]:
    return {remove_leaf_at(tree, path) for path in removable_leaf_paths(tree)}


def enumerate_by_add(max_size: int) -> dict[int, set[Tree]]:
    by_size: dict[int, set[Tree]] = {1: {Z}}
    for n in range(2, max_size + 1):
        current: set[Tree] = set()
        for tree in by_size[n - 1]:
            current.update(add_successors(tree))
        by_size[n] = {tree for tree in current if size(tree) == n}
    return by_size


def check(condition: bool, name: str) -> None:
    if not condition:
        raise AssertionError(name)
    print(f"{name}=PASS")


def main() -> None:
    by_size = enumerate_by_add(MAX_SIZE)
    corpus = set().union(*by_size.values())

    # Independent small-size sanity counts for unlabeled rooted non-plane trees.
    expected_counts = {1: 1, 2: 1, 3: 2, 4: 4, 5: 9, 6: 20}
    check(
        {n: len(by_size[n]) for n in by_size} == expected_counts,
        "AIP4_ENUMERATION_COUNTS",
    )

    # Closure and exact grading inside the bounded corpus horizon.
    add_closure = True
    remove_closure = True
    add_grade = True
    remove_grade = True
    for tree in corpus:
        for result in add_successors(tree):
            add_grade &= size(result) == size(tree) + 1
            if size(result) <= MAX_SIZE:
                add_closure &= result in corpus
        for result in remove_successors(tree):
            remove_grade &= size(result) == size(tree) - 1
            remove_closure &= result in corpus

    check(add_closure, "AIP4_ADD_CLOSURE")
    check(remove_closure, "AIP4_REMOVE_CLOSURE")
    check(add_grade, "AIP4_ADD_SIZE_PLUS_ONE")
    check(remove_grade, "AIP4_REMOVE_SIZE_MINUS_ONE")

    # Converse relation on every bounded edge.
    inverse_ok = True
    add_edges = 0
    remove_edges = 0
    for tree in corpus:
        for result in add_successors(tree):
            if size(result) <= MAX_SIZE:
                add_edges += 1
                inverse_ok &= tree in remove_successors(result)
        for result in remove_successors(tree):
            remove_edges += 1
            inverse_ok &= tree in add_successors(result)
    check(inverse_ok, "AIP4_CONVERSE_RELATION")

    # Construction: breadth-first ADD reachability from Z spans the corpus.
    reached = {Z}
    queue: deque[Tree] = deque([Z])
    while queue:
        tree = queue.popleft()
        if size(tree) == MAX_SIZE:
            continue
        for result in add_successors(tree):
            if result not in reached:
                reached.add(result)
                queue.append(result)
    check(reached == corpus, "AIP4_ADD_GENERATES_BOUNDED_CORPUS")

    # Reduction: every bounded form has a REMOVE path to Z.
    reduction_ok = True
    for start in corpus:
        seen = {start}
        queue = deque([start])
        found = start == Z
        while queue and not found:
            tree = queue.popleft()
            for result in remove_successors(tree):
                if result == Z:
                    found = True
                    break
                if result not in seen:
                    seen.add(result)
                    queue.append(result)
        reduction_ok &= found
    check(reduction_ok, "AIP4_REMOVE_REDUCES_BOUNDED_CORPUS")

    # Full undirected connectivity under ADD/REMOVE.
    adjacency: dict[Tree, set[Tree]] = defaultdict(set)
    for tree in corpus:
        for result in add_successors(tree):
            if result in corpus:
                adjacency[tree].add(result)
                adjacency[result].add(tree)
        for result in remove_successors(tree):
            adjacency[tree].add(result)
            adjacency[result].add(tree)

    connected = {Z}
    queue = deque([Z])
    while queue:
        tree = queue.popleft()
        for result in adjacency[tree]:
            if result not in connected:
                connected.add(result)
                queue.append(result)
    check(connected == corpus, "AIP4_EDIT_GRAPH_CONNECTED")

    # Bare-form ADD is genuinely multi-valued for a concrete counterexample.
    ambiguous: Tree = canonical((Z, canonical((Z,))))
    ambiguous_results = add_successors(ambiguous)
    check(len(ambiguous_results) >= 2, "AIP4_UNPOINTED_TARGET_AMBIGUITY")

    # Candidate A strictly contains one-step Candidate B: adding a size-2 subtree
    # changes size by two, impossible for one elementary ADD_NODE step.
    unary = canonical((Z,))
    candidate_a_result = canonical((unary,))
    candidate_a_strict = (
        size(candidate_a_result) == size(Z) + size(unary)
        and candidate_a_result not in add_successors(Z)
    )
    check(candidate_a_strict, "AIP4_ARBITRARY_SUBTREE_STRICTLY_STRONGER_ONE_STEP")

    # Historical abstract effects collapse to the elementary directions.
    historical_ok = True
    graft_prune_ok = True
    for tree in corpus:
        for path in paths(tree):
            sprout_effect = add_node_at(tree, path)
            historical_ok &= sprout_effect in add_successors(tree)
            if subtree(tree, path) == Z:
                # GRAFT at a zero-child target is the same elementary ADD.
                graft_prune_ok &= sprout_effect in add_successors(tree)
                # PRUNE reverses that newly created unary local shape.
                graft_prune_ok &= tree in remove_successors(sprout_effect)
        for path in removable_leaf_paths(tree):
            shed_effect = remove_leaf_at(tree, path)
            historical_ok &= shed_effect in remove_successors(tree)

    check(historical_ok, "AIP4_SPROUT_SHED_COLLAPSE")
    check(graft_prune_ok, "AIP4_GRAFT_PRUNE_SPECIAL_CASE")

    print(f"AIP4_MAX_SIZE={MAX_SIZE}")
    print(f"AIP4_FORMS={len(corpus)}")
    print(f"AIP4_ADD_EDGES={add_edges}")
    print(f"AIP4_REMOVE_EDGES={remove_edges}")
    print("AIP4_SCOPE=finite rooted non-plane trees up to size 6")


if __name__ == "__main__":
    main()
