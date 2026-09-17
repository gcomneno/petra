from __future__ import annotations

from collections import defaultdict, deque
from functools import lru_cache

Tree = tuple["Tree", ...]
Path = tuple[int, ...]

Z: Tree = ()
MAX_SIZE = 7


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


@lru_cache(maxsize=None)
def reducts(tree: Tree) -> frozenset[Tree]:
    result = {tree}
    for child in remove_successors(tree):
        result.update(reducts(child))
    return frozenset(result)


def build_adjacency(corpus: set[Tree]) -> dict[Tree, set[Tree]]:
    adjacency: dict[Tree, set[Tree]] = defaultdict(set)
    for tree in corpus:
        for result in add_successors(tree):
            if result in corpus:
                adjacency[tree].add(result)
                adjacency[result].add(tree)
        for result in remove_successors(tree):
            adjacency[tree].add(result)
            adjacency[result].add(tree)
    return adjacency


def distances_from(
    start: Tree,
    adjacency: dict[Tree, set[Tree]],
) -> dict[Tree, int]:
    distance = {start: 0}
    queue: deque[Tree] = deque([start])
    while queue:
        current = queue.popleft()
        for nxt in adjacency[current]:
            if nxt not in distance:
                distance[nxt] = distance[current] + 1
                queue.append(nxt)
    return distance


def max_common_reducts(left: Tree, right: Tree) -> set[Tree]:
    common = set(reducts(left)).intersection(reducts(right))
    maximum = max(size(tree) for tree in common)
    return {tree for tree in common if size(tree) == maximum}


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
    }
    check(
        {n: len(by_size[n]) for n in by_size} == expected_counts,
        "META_EDIT_ENUMERATION_COUNTS",
    )

    adjacency = build_adjacency(corpus)

    # Every bounded edge must change size by exactly one and therefore flip parity.
    grading_ok = True
    bipartite_ok = True
    for tree, neighbors in adjacency.items():
        for neighbor in neighbors:
            grading_ok &= abs(size(tree) - size(neighbor)) == 1
            bipartite_ok &= size(tree) % 2 != size(neighbor) % 2
    check(grading_ok, "META_EDIT_UNIT_GRADING")
    check(bipartite_ok, "META_EDIT_BIPARTITE")

    # The bounded graph must remain connected.
    distance_from_z = distances_from(Z, adjacency)
    check(len(distance_from_z) == len(corpus), "META_EDIT_BOUNDED_CONNECTED")

    # Compare BFS distance with the exact common-reduct formula for every pair.
    formula_ok = True
    lower_bound_ok = True
    via_z_bound_ok = True
    parity_ok = True
    nonunique_pairs: list[tuple[Tree, Tree, set[Tree]]] = []

    ordered = sorted(corpus, key=lambda tree: (size(tree), key(tree)))
    all_distances = {
        tree: distances_from(tree, adjacency)
        for tree in ordered
    }

    for index, left in enumerate(ordered):
        for right in ordered[index:]:
            actual = all_distances[left][right]
            maxima = max_common_reducts(left, right)
            c = size(next(iter(maxima)))
            predicted = size(left) + size(right) - 2 * c

            formula_ok &= actual == predicted
            lower_bound_ok &= actual >= abs(size(left) - size(right))
            via_z_bound_ok &= actual <= size(left) + size(right) - 2
            parity_ok &= actual % 2 == (size(right) - size(left)) % 2

            if len(maxima) > 1:
                nonunique_pairs.append((left, right, maxima))

    check(formula_ok, "META_EDIT_COMMON_REDUCT_DISTANCE_FORMULA")
    check(lower_bound_ok, "META_EDIT_SIZE_LOWER_BOUND")
    check(via_z_bound_ok, "META_EDIT_VIA_Z_UPPER_BOUND")
    check(parity_ok, "META_EDIT_DISTANCE_PARITY")

    # Explicit non-geodesic via-Z example from the theory note.
    unary = canonical((Z,))
    binary = canonical((Z, Z))
    direct = all_distances[unary][binary]
    via_z = size(unary) + size(binary) - 2
    check(direct == 1 and via_z == 3, "META_EDIT_VIA_Z_NOT_ALWAYS_GEODESIC")

    # Local finiteness is automatic for each finite form; boundedly corroborate
    # the simple realization-level degree upper bounds used in the proof.
    degree_bound_ok = True
    for tree in corpus:
        add_count = len({x for x in add_successors(tree) if size(x) <= MAX_SIZE})
        remove_count = len(remove_successors(tree))
        degree_bound_ok &= add_count <= size(tree)
        degree_bound_ok &= remove_count <= max(0, size(tree) - 1)
    check(degree_bound_ok, "META_EDIT_LOCAL_DEGREE_BOUNDS")

    print(f"META_EDIT_MAX_SIZE={MAX_SIZE}")
    print(f"META_EDIT_FORMS={len(corpus)}")
    print(f"META_EDIT_PAIRS={len(ordered) * (len(ordered) + 1) // 2}")
    print(f"META_EDIT_NONUNIQUE_MAX_COMMON_REDUCT_PAIRS={len(nonunique_pairs)}")
    if nonunique_pairs:
        left, right, maxima = nonunique_pairs[0]
        print(
            "META_EDIT_FIRST_NONUNIQUE_MAX_COMMON_REDUCT="
            f"left_size:{size(left)};right_size:{size(right)};"
            f"common_size:{size(next(iter(maxima)))};count:{len(maxima)}"
        )
    print(
        "META_EDIT_SCOPE=finite rooted non-plane trees up to size 7; "
        "bounded corroboration only"
    )


if __name__ == "__main__":
    main()
