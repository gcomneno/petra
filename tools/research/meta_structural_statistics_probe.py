from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache

Tree = tuple["Tree", ...]
Path = tuple[int, ...]

Z: Tree = ()
MAX_SIZE = 10


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
    return [path for path in paths(tree) if path and subtree(tree, path) == Z]


def remove_leaf_at(tree: Tree, path: Path) -> Tree:
    parent_path = path[:-1]
    index = path[-1]
    parent = subtree(tree, parent_path)
    if parent[index] != Z:
        raise ValueError("REMOVE target must be a leaf")
    children = list(parent)
    del children[index]
    return replace_at(tree, parent_path, canonical(children))


def enumerate_by_add(max_size: int) -> dict[int, set[Tree]]:
    by_size: dict[int, set[Tree]] = {1: {Z}}
    for n in range(2, max_size + 1):
        current: set[Tree] = set()
        for tree in by_size[n - 1]:
            for path in paths(tree):
                current.add(add_node_at(tree, path))
        by_size[n] = {tree for tree in current if size(tree) == n}
    return by_size


def level_profile(tree: Tree) -> Counter[int]:
    profile: Counter[int] = Counter()

    def visit(node: Tree, level: int) -> None:
        profile[level] += 1
        for child in node:
            visit(child, level + 1)

    visit(tree, 0)
    return profile


def degree_profile(tree: Tree) -> Counter[int]:
    return Counter(len(subtree(tree, path)) for path in paths(tree))


def depth(tree: Tree) -> int:
    return max(level_profile(tree))


def leaves(tree: Tree) -> int:
    return sum(1 for path in paths(tree) if subtree(tree, path) == Z)


def root_degree(tree: Tree) -> int:
    return len(tree)


def width(tree: Tree) -> int:
    return max(level_profile(tree).values())


def max_degree(tree: Tree) -> int:
    return max(len(subtree(tree, path)) for path in paths(tree))


def l1_counter_distance(left: Counter[int], right: Counter[int]) -> int:
    keys = set(left) | set(right)
    return sum(abs(left[key] - right[key]) for key in keys)


def stats(tree: Tree) -> tuple[int, int, int, int, int, int]:
    return (
        size(tree),
        depth(tree),
        leaves(tree),
        root_degree(tree),
        width(tree),
        max_degree(tree),
    )


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
        "META_STATS_ENUMERATION_COUNTS",
    )

    depth_ok = True
    leaf_ok = True
    root_degree_ok = True
    degree_profile_ok = True
    level_profile_ok = True
    width_ok = True
    max_degree_ok = True
    max_degree_profile_l1 = 0
    max_level_profile_l1 = 0
    add_edges_checked = 0
    remove_edges_checked = 0

    for tree in corpus:
        if size(tree) < MAX_SIZE:
            for path in paths(tree):
                successor = add_node_at(tree, path)
                target = subtree(tree, path)
                k = len(target)
                ell = len(path)
                add_edges_checked += 1

                depth_ok &= depth(successor) == max(depth(tree), ell + 1)
                leaf_ok &= leaves(successor) - leaves(tree) == (0 if k == 0 else 1)
                root_degree_ok &= root_degree(successor) - root_degree(tree) == (
                    1 if not path else 0
                )

                expected_degree = degree_profile(tree).copy()
                expected_degree[0] += 1
                expected_degree[k] -= 1
                expected_degree[k + 1] += 1
                expected_degree += Counter()
                degree_profile_ok &= degree_profile(successor) == expected_degree

                expected_level = level_profile(tree).copy()
                expected_level[ell + 1] += 1
                level_profile_ok &= level_profile(successor) == expected_level

                degree_l1 = l1_counter_distance(
                    degree_profile(tree), degree_profile(successor)
                )
                level_l1 = l1_counter_distance(
                    level_profile(tree), level_profile(successor)
                )
                max_degree_profile_l1 = max(max_degree_profile_l1, degree_l1)
                max_level_profile_l1 = max(max_level_profile_l1, level_l1)

                width_ok &= abs(width(successor) - width(tree)) <= 1
                max_degree_ok &= abs(max_degree(successor) - max_degree(tree)) <= 1

        for path in removable_leaf_paths(tree):
            successor = remove_leaf_at(tree, path)
            parent_path = path[:-1]
            parent_degree = len(subtree(tree, parent_path))
            ell = len(path)
            remove_edges_checked += 1

            depth_ok &= abs(depth(successor) - depth(tree)) <= 1
            leaf_ok &= leaves(successor) - leaves(tree) == (
                0 if parent_degree == 1 else -1
            )
            root_degree_ok &= root_degree(successor) - root_degree(tree) == (
                -1 if len(path) == 1 else 0
            )

            expected_degree = degree_profile(tree).copy()
            expected_degree[0] -= 1
            expected_degree[parent_degree] -= 1
            expected_degree[parent_degree - 1] += 1
            expected_degree += Counter()
            degree_profile_ok &= degree_profile(successor) == expected_degree

            expected_level = level_profile(tree).copy()
            expected_level[ell] -= 1
            expected_level += Counter()
            level_profile_ok &= level_profile(successor) == expected_level

            degree_l1 = l1_counter_distance(
                degree_profile(tree), degree_profile(successor)
            )
            level_l1 = l1_counter_distance(
                level_profile(tree), level_profile(successor)
            )
            max_degree_profile_l1 = max(max_degree_profile_l1, degree_l1)
            max_level_profile_l1 = max(max_level_profile_l1, level_l1)

            width_ok &= abs(width(successor) - width(tree)) <= 1
            max_degree_ok &= abs(max_degree(successor) - max_degree(tree)) <= 1

    check(depth_ok, "META_STATS_DEPTH_RULE")
    check(leaf_ok, "META_STATS_LEAF_RULE")
    check(root_degree_ok, "META_STATS_ROOT_DEGREE_RULE")
    check(degree_profile_ok, "META_STATS_DEGREE_PROFILE_RULE")
    check(level_profile_ok, "META_STATS_LEVEL_PROFILE_RULE")
    check(width_ok, "META_STATS_WIDTH_1_LIPSCHITZ")
    check(max_degree_ok, "META_STATS_MAX_DEGREE_1_LIPSCHITZ")
    check(max_degree_profile_l1 == 3, "META_STATS_DEGREE_PROFILE_L1_SHARP")
    check(max_level_profile_l1 == 1, "META_STATS_LEVEL_PROFILE_L1_EXACT")

    collisions: dict[tuple[int, int, int, int, int, int], list[Tree]] = defaultdict(list)
    for tree in corpus:
        collisions[stats(tree)].append(tree)

    nonclassification = next(
        (forms for forms in collisions.values() if len(forms) >= 2),
        None,
    )
    check(nonclassification is not None, "META_STATS_BASIC_TUPLE_NONCLASSIFYING")

    assert nonclassification is not None
    witness_a, witness_b = nonclassification[:2]
    witness_stats = stats(witness_a)
    check(witness_a != witness_b, "META_STATS_WITNESS_DISTINCT")
    check(stats(witness_b) == witness_stats, "META_STATS_WITNESS_EQUAL_STATS")

    print(f"META_STATS_MAX_SIZE={MAX_SIZE}")
    print(f"META_STATS_FORMS={len(corpus)}")
    print(f"META_STATS_ADD_EDGES_CHECKED={add_edges_checked}")
    print(f"META_STATS_REMOVE_EDGES_CHECKED={remove_edges_checked}")
    print(f"META_STATS_MAX_DEGREE_PROFILE_L1={max_degree_profile_l1}")
    print(f"META_STATS_MAX_LEVEL_PROFILE_L1={max_level_profile_l1}")
    print(f"META_STATS_FIRST_COLLISION_STATS={witness_stats}")
    print(f"META_STATS_FIRST_COLLISION_A={witness_a}")
    print(f"META_STATS_FIRST_COLLISION_B={witness_b}")
    print(
        "META_STATS_SCOPE=finite rooted non-plane trees up to size 10; "
        "local edit formulas checked exhaustively inside bounded corpus; "
        "bounded corroboration only"
    )


if __name__ == "__main__":
    main()
