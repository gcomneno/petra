from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache
from itertools import permutations
from math import factorial

Tree = tuple["Tree", ...]
Path = tuple[int, ...]
MarkedTree = tuple[bool, tuple["MarkedTree", ...]]

Z: Tree = ()
MAX_SIZE = 10
BRUTE_VERIFY_MAX_SIZE = 8


def key(tree: Tree) -> tuple:
    return tuple(key(child) for child in tree)


def canonical(children: tuple[Tree, ...] | list[Tree]) -> Tree:
    return tuple(sorted(children, key=key))


@lru_cache(maxsize=None)
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
    return [
        path
        for path in paths(tree)
        if path and subtree(tree, path) == Z
    ]


def remove_leaf_at(tree: Tree, path: Path) -> Tree:
    parent_path = path[:-1]
    index = path[-1]
    parent = subtree(tree, parent_path)
    if parent[index] != Z:
        raise ValueError("REMOVE target must be a leaf")
    children = list(parent)
    del children[index]
    return replace_at(tree, parent_path, canonical(children))


def add_successors(tree: Tree) -> set[Tree]:
    return {add_node_at(tree, path) for path in paths(tree)}


def enumerate_by_add(max_size: int) -> dict[int, set[Tree]]:
    by_size: dict[int, set[Tree]] = {1: {Z}}
    for n in range(2, max_size + 1):
        current: set[Tree] = set()
        for tree in by_size[n - 1]:
            current.update(add_successors(tree))
        by_size[n] = {tree for tree in current if size(tree) == n}
    return by_size


@lru_cache(maxsize=None)
def automorphism_count(tree: Tree) -> int:
    multiplicities = Counter(tree)
    total = 1
    for child, multiplicity in multiplicities.items():
        total *= automorphism_count(child) ** multiplicity
        total *= factorial(multiplicity)
    return total


def parent_vector(tree: Tree) -> tuple[int, ...]:
    """Return a DFS-labelled rooted realization as a parent vector.

    Vertex 0 is the root. For every non-root vertex v, result[v] is its parent.
    The concrete DFS labels are representation-local and are used only by the
    bounded brute-force automorphism verifier below.
    """

    parents = [-1]

    def visit(node: Tree, parent: int) -> None:
        for child in node:
            child_id = len(parents)
            parents.append(parent)
            visit(child, child_id)

    visit(tree, 0)
    return tuple(parents)


def brute_automorphism_count(tree: Tree) -> int:
    """Count root-preserving automorphisms by direct vertex permutations.

    This deliberately does not use the recursive automorphism recurrence. It is
    only practical for small trees and serves as an independent bounded check.
    """

    parents = parent_vector(tree)
    n = len(parents)
    if n == 1:
        return 1

    count = 0
    for tail in permutations(range(1, n)):
        image = (0, *tail)
        valid = True
        for vertex in range(1, n):
            if image[parents[vertex]] != parents[image[vertex]]:
                valid = False
                break
        if valid:
            count += 1
    return count


def marked_key(marked: MarkedTree) -> tuple:
    is_marked, children = marked
    return (is_marked, tuple(marked_key(child) for child in children))


def mark_occurrence(
    tree: Tree,
    target: Path,
    prefix: Path = (),
) -> MarkedTree:
    children = [
        mark_occurrence(child, target, prefix + (index,))
        for index, child in enumerate(tree)
    ]
    children.sort(key=marked_key)
    return (prefix == target, tuple(children))


def orbit_signature(tree: Tree, target: Path) -> tuple:
    return marked_key(mark_occurrence(tree, target))


def check(condition: bool, name: str) -> None:
    if not condition:
        raise AssertionError(name)
    print(f"{name}=PASS")


def main() -> None:
    by_size = enumerate_by_add(MAX_SIZE)
    corpus = set().union(*by_size.values())

    expected_counts = {
        1: 1,
        2: 1,
        3: 2,
        4: 4,
        5: 9,
        6: 20,
        7: 48,
        8: 115,
        9: 286,
        10: 719,
    }
    check(
        {n: len(by_size[n]) for n in by_size} == expected_counts,
        "META_AUT_ENUMERATION_COUNTS",
    )

    brute_verified_forms = 0
    count_recurrence_ok = True
    rigidity_bruteforce_ok = True
    for n in range(1, BRUTE_VERIFY_MAX_SIZE + 1):
        for tree in by_size[n]:
            brute_count = brute_automorphism_count(tree)
            recurrence_count = automorphism_count(tree)
            count_recurrence_ok &= brute_count == recurrence_count

            multiplicities = Counter(tree)
            recursive_rigid = (
                all(multiplicity == 1 for multiplicity in multiplicities.values())
                and all(automorphism_count(child) == 1 for child in tree)
            )
            rigidity_bruteforce_ok &= (brute_count == 1) == recursive_rigid
            brute_verified_forms += 1

    check(count_recurrence_ok, "META_AUT_COUNT_RECURRENCE")
    check(rigidity_bruteforce_ok, "META_AUT_RIGIDITY_CRITERION")

    same_orbit_add_same_successor = True
    same_orbit_remove_same_successor = True
    add_collision: tuple[Tree, list[Path]] | None = None
    remove_collision: tuple[Tree, list[Path]] | None = None

    nontrivial_aut_forms = 0
    total_add_orbits = 0
    total_remove_orbits = 0

    for tree in corpus:
        if automorphism_count(tree) > 1:
            nontrivial_aut_forms += 1

        add_by_orbit: dict[tuple, set[Tree]] = defaultdict(set)
        add_by_successor: dict[Tree, list[Path]] = defaultdict(list)
        for path in paths(tree):
            signature = orbit_signature(tree, path)
            successor = add_node_at(tree, path)
            add_by_orbit[signature].add(successor)
            add_by_successor[successor].append(path)

        total_add_orbits += len(add_by_orbit)
        same_orbit_add_same_successor &= all(
            len(successors) == 1 for successors in add_by_orbit.values()
        )

        if add_collision is None:
            for target_paths in add_by_successor.values():
                signatures = {
                    orbit_signature(tree, path)
                    for path in target_paths
                }
                if len(signatures) > 1:
                    add_collision = (tree, target_paths)
                    break

        remove_by_orbit: dict[tuple, set[Tree]] = defaultdict(set)
        remove_by_successor: dict[Tree, list[Path]] = defaultdict(list)
        for path in removable_leaf_paths(tree):
            signature = orbit_signature(tree, path)
            successor = remove_leaf_at(tree, path)
            remove_by_orbit[signature].add(successor)
            remove_by_successor[successor].append(path)

        total_remove_orbits += len(remove_by_orbit)
        same_orbit_remove_same_successor &= all(
            len(successors) == 1 for successors in remove_by_orbit.values()
        )

        if remove_collision is None:
            for target_paths in remove_by_successor.values():
                signatures = {
                    orbit_signature(tree, path)
                    for path in target_paths
                }
                if len(signatures) > 1:
                    remove_collision = (tree, target_paths)
                    break

    check(
        same_orbit_add_same_successor,
        "META_AUT_ADD_ORBIT_IMPLIES_SAME_SUCCESSOR",
    )
    check(
        same_orbit_remove_same_successor,
        "META_AUT_REMOVE_ORBIT_IMPLIES_SAME_SUCCESSOR",
    )

    # These are bounded searches for a converse failure, not proofs of the
    # converse. PASS means no counterexample was found in this corpus.
    check(
        add_collision is None,
        "META_AUT_ADD_CONVERSE_NO_COUNTEREXAMPLE_BOUNDED",
    )
    check(
        remove_collision is None,
        "META_AUT_REMOVE_CONVERSE_NO_COUNTEREXAMPLE_BOUNDED",
    )

    print(f"META_AUT_MAX_SIZE={MAX_SIZE}")
    print(f"META_AUT_FORMS={len(corpus)}")
    print(f"META_AUT_BRUTE_VERIFY_MAX_SIZE={BRUTE_VERIFY_MAX_SIZE}")
    print(f"META_AUT_BRUTE_VERIFIED_FORMS={brute_verified_forms}")
    print(f"META_AUT_NONTRIVIAL_AUT_FORMS={nontrivial_aut_forms}")
    print(f"META_AUT_TOTAL_ADD_TARGET_ORBITS={total_add_orbits}")
    print(f"META_AUT_TOTAL_REMOVE_TARGET_ORBITS={total_remove_orbits}")
    print(
        "META_AUT_SCOPE=finite rooted non-plane trees up to size 10; "
        "brute-force automorphism verification up to size 8; "
        "bounded corroboration only"
    )


if __name__ == "__main__":
    main()
