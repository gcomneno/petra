from __future__ import annotations


from typing import Any, List, Tuple, Union



PETExp = Union[None, "PET"]
PETNode = Tuple[int, PETExp]
PET = List[PETNode]


def _shape_signature(tree: PET) -> tuple:
    children = []
    for _, exp_repr in tree:
        if exp_repr is None:
            children.append(())
        else:
            children.append(_shape_signature(exp_repr))
    return tuple(sorted(children))


def _signature_to_jsonable(sig: tuple) -> list:
    return [_signature_to_jsonable(child) for child in sig]


def shape_signature_dict(n: int) -> dict[str, Any]:
    """Return canonical signature data for the PET shape class of n.

    The signature is computed on the minimal shape representative, not on n
    directly.
    """
    minimal_tree = minimal_shape_representative(encode(n))
    generator = decode(minimal_tree)
    child_generators = [
        1 if exp_repr is None else decode(exp_repr)
        for _, exp_repr in minimal_tree
    ]
    signature = _shape_signature(minimal_tree)

    return {
        "n": n,
        "generator": generator,
        "already_minimal": generator == n,
        "child_generators": child_generators,
        "signature": _signature_to_jsonable(signature),
    }


def is_prime(n: int) -> bool:
    """Return True if n is prime, else False."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def prime_factorization(n: int) -> List[Tuple[int, int]]:
    """Return the prime factorization of n as a sorted list of (prime, exponent)."""
    if n < 2:
        raise ValueError("n must be >= 2")

    factors: List[Tuple[int, int]] = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            exp = 0
            while n % d == 0:
                n //= d
                exp += 1
            factors.append((d, exp))
        d = 3 if d == 2 else d + 2

    if n > 1:
        factors.append((n, 1))

    return factors


def encode(n: int) -> PET:
    """Encode an integer n >= 2 into its canonical Prime Exponent Tree."""
    if n < 2:
        raise ValueError("n must be >= 2")

    tree: PET = []
    for prime, exp in prime_factorization(n):
        exp_repr: PETExp = None if exp == 1 else encode(exp)
        tree.append((prime, exp_repr))
    return tree


def validate(tree: PET) -> None:
    """Validate that a tree is a canonical PET."""
    if not isinstance(tree, list) or not tree:
        raise TypeError("tree must be a non-empty list")

    last_prime = 1

    for node in tree:
        if not isinstance(node, tuple) or len(node) != 2:
            raise TypeError("each node must be a tuple (prime, exponent_repr)")

        prime, exp_repr = node

        if not isinstance(prime, int):
            raise TypeError("prime must be an int")

        if not is_prime(prime):
            raise ValueError(f"{prime} is not prime")

        if prime <= last_prime:
            raise ValueError("primes must be strictly increasing at each level")

        last_prime = prime

        if exp_repr is None:
            continue

        if not isinstance(exp_repr, list):
            raise TypeError("exponent_repr must be None or another PET")

        validate(exp_repr)


def decode(tree: PET) -> int:
    """Decode a Prime Exponent Tree back into the represented integer."""
    validate(tree)

    result = 1
    for prime, exp_repr in tree:
        exp = 1 if exp_repr is None else decode(exp_repr)
        result *= prime ** exp
    return result


def _node_count(tree: PET) -> int:
    total = 0
    for _, exp_repr in tree:
        total += 1
        if exp_repr is not None:
            total += _node_count(exp_repr)
    return total


def node_count(tree: PET) -> int:
    validate(tree)
    return _node_count(tree)


def _leaf_count(tree: PET) -> int:
    total = 0
    for _, exp_repr in tree:
        if exp_repr is None:
            total += 1
        else:
            total += _leaf_count(exp_repr)
    return total


def leaf_count(tree: PET) -> int:
    validate(tree)
    return _leaf_count(tree)


def _collect_leaf_depths(tree: PET, depth: int, depths: list[int]) -> None:
    for _, exp_repr in tree:
        if exp_repr is None:
            depths.append(depth)
        else:
            _collect_leaf_depths(exp_repr, depth + 1, depths)


def average_leaf_depth(tree: PET) -> float:
    validate(tree)
    depths: list[int] = []
    _collect_leaf_depths(tree, 1, depths)
    return sum(depths) / len(depths)


def leaf_depth_variance(tree: PET) -> float:
    validate(tree)
    depths: list[int] = []
    _collect_leaf_depths(tree, 1, depths)
    mean = sum(depths) / len(depths)
    return sum((depth - mean) ** 2 for depth in depths) / len(depths)


def _height(tree: PET) -> int:
    child_heights = [
        _height(exp_repr)
        for _, exp_repr in tree
        if exp_repr is not None
    ]
    if not child_heights:
        return 1
    return 1 + max(child_heights)


def height(tree: PET) -> int:
    validate(tree)
    return _height(tree)


def _max_branching(tree: PET) -> int:
    current = len(tree)
    child_values = [
        _max_branching(exp_repr)
        for _, exp_repr in tree
        if exp_repr is not None
    ]
    if not child_values:
        return current
    return max(current, max(child_values))


def _branch_profile(tree: PET, depth: int, counts: list[int]) -> None:
    if depth == len(counts):
        counts.append(0)

    counts[depth] += len(tree)

    for _, exp_repr in tree:
        if exp_repr is not None:
            _branch_profile(exp_repr, depth + 1, counts)


def branch_profile(tree: PET) -> list[int]:
    validate(tree)
    counts: list[int] = []
    _branch_profile(tree, 0, counts)
    return counts


def max_branching(tree: PET) -> int:
    validate(tree)
    return _max_branching(tree)


def recursive_mass(tree: PET) -> int:
    validate(tree)
    return node_count(tree) - len(tree)


def _first_primes(count: int) -> list[int]:
    primes: list[int] = []
    candidate = 2

    while len(primes) < count:
        if is_prime(candidate):
            primes.append(candidate)
        candidate += 1 if candidate == 2 else 2

    return primes


def _minimal_shape_tree(tree: PET) -> PET:
    children: list[tuple[int, PETExp]] = []

    for _, exp_repr in tree:
        if exp_repr is None:
            child_tree = None
            child_value = 1
        else:
            child_tree = _minimal_shape_tree(exp_repr)
            child_value = decode(child_tree)

        children.append((child_value, child_tree))

    children.sort(key=lambda item: item[0], reverse=True)
    primes = _first_primes(len(children))

    result: PET = []
    for prime, (_, exp_repr) in zip(primes, children):
        result.append((prime, exp_repr))

    return result


def minimal_shape_representative(tree: PET) -> PET:
    """Return the canonical PET with minimal decoded value among all PETs
    having the same structural shape as ``tree``.
    """
    validate(tree)
    result = _minimal_shape_tree(tree)
    validate(result)
    return result


def shape_generator(n: int) -> int:
    """Return the smallest integer having the same PET structural shape as n."""
    return decode(minimal_shape_representative(encode(n)))


def pet_from_factorization(factors: List[Tuple[int, int]]) -> PET:
    """Build a canonical PET directly from a sorted factor specification.

    This avoids factoring the decoded target integer again.
    """
    if not factors:
        raise ValueError("factor spec cannot be empty")

    tree: PET = []
    last_prime = 1

    for prime, exp in factors:
        if not isinstance(prime, int) or not isinstance(exp, int):
            raise TypeError("factor spec entries must be integer pairs")
        if prime < 2:
            raise ValueError("prime must be >= 2")
        if exp < 1:
            raise ValueError("exponent must be >= 1")
        if not is_prime(prime):
            raise ValueError(f"{prime} is not prime")
        if prime <= last_prime:
            raise ValueError("primes must be strictly increasing")
        last_prime = prime

        exp_repr: PETExp = None if exp == 1 else encode(exp)
        tree.append((prime, exp_repr))

    validate(tree)
    return tree


def shape_generator_from_factorization(factors: List[Tuple[int, int]]) -> int:
    """Return the minimal-shape generator directly from a factor specification."""
    return decode(minimal_shape_representative(pet_from_factorization(factors)))


def metrics_dict(tree: PET) -> dict[str, Any]:
    validate(tree)
    return {
        "node_count": node_count(tree),
        "leaf_count": leaf_count(tree),
        "height": height(tree),
        "max_branching": max_branching(tree),
        "branch_profile": branch_profile(tree),
        "recursive_mass": recursive_mass(tree),
        "average_leaf_depth": average_leaf_depth(tree),
        "leaf_depth_variance": leaf_depth_variance(tree),
    }
