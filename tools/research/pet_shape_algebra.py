from __future__ import annotations
from functools import lru_cache
from typing import TypeAlias


# === TYPES AND CONSTANTS ===

Shape: TypeAlias = tuple['Shape', ...]

PathT: TypeAlias = tuple[int, ...]

StableStepT: TypeAlias = tuple['Shape', int]

StablePathT: TypeAlias = tuple[StableStepT, ...]

PartialShape = 'Shape | None | tuple[PartialShape, ...]'

PRIMITIVE_ROOT_OPS: tuple[str, ...] = ('NEW', 'DROP')

PRIMITIVE_LOCAL_OPS: tuple[str, ...] = ('INC', 'DEC')

PRIMITIVE_SHAPE_OPS: tuple[str, ...] = PRIMITIVE_ROOT_OPS + PRIMITIVE_LOCAL_OPS


# === CORE SHAPE ===

def _shape_key(shape: Shape):
    return tuple((_shape_key(child) for child in shape))

def normalize_shape(shape: Shape) -> Shape:
    normalized_children = tuple((normalize_shape(child) for child in shape))
    return tuple(sorted(normalized_children, key=_shape_key))

def shape_mass(shape: Shape) -> int:
    shape = normalize_shape(shape)
    return sum((1 + shape_mass(child) for child in shape))

@lru_cache(maxsize=None)
def _shapes_of_mass(mass: int) -> tuple[Shape, ...]:
    if mass < 0:
        raise ValueError('mass must be >= 0')
    if mass == 0:
        return ((),)
    out: set[Shape] = set()

    def _build(remaining: int, min_key, acc: list[Shape]) -> None:
        if remaining == 0:
            out.add(tuple(acc))
            return
        for child_mass in range(remaining):
            weight = 1 + child_mass
            if weight > remaining:
                break
            for child in _shapes_of_mass(child_mass):
                key = _shape_key(child)
                if min_key is not None and key < min_key:
                    continue
                acc.append(child)
                _build(remaining - weight, key, acc)
                acc.pop()
    _build(mass, None, [])
    return tuple(sorted(out, key=_shape_key))

def _first_primes(n: int) -> list[int]:
    primes: list[int] = []
    candidate = 2
    while len(primes) < n:
        is_prime = True
        for p in primes:
            if p * p > candidate:
                break
            if candidate % p == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(candidate)
        candidate += 1
    return primes

@lru_cache(maxsize=None)
@lru_cache(maxsize=None)
def _exp_gamma(shape: Shape) -> int:
    shape = normalize_shape(shape)
    if shape == ():
        return 1
    child_values = sorted((_exp_gamma(child) for child in shape), reverse=True)
    total = 1
    for prime, exp in zip(_first_primes(len(child_values)), child_values):
        total *= prime ** exp
    return total

def shape_gamma(shape: Shape) -> int:
    shape = normalize_shape(shape)
    if shape == ():
        raise ValueError('shape_gamma is undefined for leaf shape ()')
    child_values = sorted((_exp_gamma(child) for child in shape), reverse=True)
    total = 1
    for prime, exp in zip(_first_primes(len(child_values)), child_values):
        total *= prime ** exp
    return total

def _shape_to_pet(shape: Shape):
    shape = normalize_shape(shape)
    if shape == ():
        raise ValueError('cannot materialize leaf shape () as a root PET')
    children = []
    for child in shape:
        if child == ():
            child_pet = None
            child_value = 1
        else:
            child_pet = _shape_to_pet(child)
            child_value = _exp_gamma(child)
        children.append((child_value, child_pet))
    children.sort(key=lambda item: item[0], reverse=True)
    result = []
    for prime, (_value, exp_repr) in zip(_first_primes(len(children)), children):
        result.append((prime, exp_repr))
    return result

def shape_to_pet(shape: Shape):
    return _shape_to_pet(shape)

def pet_to_shape(tree) -> Shape:
    return normalize_shape(tuple((() if exp_repr is None else pet_to_shape(exp_repr) for _prime, exp_repr in tree)))


# === PRIMITIVE OPS ===

def shape_new(shape: Shape) -> Shape:
    return normalize_shape(shape + ((),))

def shape_drop(shape: Shape) -> Shape:
    if not shape:
        raise ValueError('cannot DROP from an empty root-shape')
    children = list(shape)
    for i, child in enumerate(children):
        if child == ():
            del children[i]
            return normalize_shape(tuple(children))
    raise ValueError('shape_drop requires at least one leaf child at root')

def shape_succ(exp_shape: Shape) -> Shape:
    shape = normalize_shape(exp_shape)
    mass = shape_mass(shape)
    level = _shapes_of_mass(mass)
    idx = level.index(shape)
    if idx + 1 < len(level):
        return level[idx + 1]
    return _shapes_of_mass(mass + 1)[0]

def shape_pred(exp_shape: Shape) -> Shape:
    shape = normalize_shape(exp_shape)
    mass = shape_mass(shape)
    if mass == 0:
        raise ValueError('shape_pred is undefined at exponent-shape for 1')
    level = _shapes_of_mass(mass)
    idx = level.index(shape)
    if idx > 0:
        return level[idx - 1]
    prev_level = _shapes_of_mass(mass - 1)
    return prev_level[-1]

def _replace_at(shape: Shape, path: PathT, op) -> Shape:
    if not path:
        return normalize_shape(op(shape))
    idx = path[0]
    if idx < 0 or idx >= len(shape):
        raise IndexError(f'path index out of range: {idx}')
    children = list(shape)
    children[idx] = _replace_at(children[idx], path[1:], op)
    return normalize_shape(tuple(children))

def shape_inc(shape: Shape, path: PathT) -> Shape:
    if not path:
        raise ValueError('shape_inc requires a non-empty path')
    return _replace_at(normalize_shape(shape), path, shape_succ)

def shape_dec(shape: Shape, path: PathT) -> Shape:
    if not path:
        raise ValueError('shape_dec requires a non-empty path')
    return _replace_at(normalize_shape(shape), path, shape_pred)

def is_primitive_shape_op(op: str) -> bool:
    return op in PRIMITIVE_SHAPE_OPS

def shape_apply(shape: Shape, op: str, path: PathT=()) -> Shape:
    root = normalize_shape(shape)
    op = op.upper()
    if op == 'NEW':
        if path != ():
            raise ValueError('NEW requires root path ()')
        return shape_new(root)
    if op == 'DROP':
        if path != ():
            raise ValueError('DROP requires root path ()')
        return shape_drop(root)
    if op == 'INC':
        if path == ():
            raise ValueError('INC requires a non-empty path')
        return shape_inc(root, path)
    if op == 'DEC':
        if path == ():
            raise ValueError('DEC requires a non-empty path')
        return shape_dec(root, path)
    raise ValueError(f'unknown shape op: {op}')

def shape_can_apply(shape: Shape, op: str, path: PathT=()) -> bool:
    try:
        shape_apply(shape, op, path)
        return True
    except (ValueError, IndexError, NotImplementedError):
        return False


# === PATHS AND NAVIGATION ===

def shape_at(shape: Shape, path: PathT) -> Shape:
    node = normalize_shape(shape)
    for idx in path:
        if idx < 0 or idx >= len(node):
            raise IndexError(f'path index out of range: {idx}')
        node = node[idx]
    return node

def shape_paths(shape: Shape, *, include_root: bool=False) -> tuple[PathT, ...]:
    node = normalize_shape(shape)
    out: list[PathT] = []

    def _walk(cur: Shape, path: PathT) -> None:
        out.append(path)
        for i, child in enumerate(cur):
            _walk(child, path + (i,))
    _walk(node, ())
    if include_root:
        return tuple(out)
    return tuple((path for path in out if path))

def index_path_to_stable_path(shape: Shape, path: PathT) -> StablePathT:
    cur = normalize_shape(shape)
    out: list[StableStepT] = []
    for idx in path:
        if idx < 0 or idx >= len(cur):
            raise IndexError(f'path index out of range: {idx}')
        child = cur[idx]
        ordinal = sum((1 for prev in cur[:idx + 1] if prev == child)) - 1
        out.append((child, ordinal))
        cur = child
    return tuple(out)

def stable_path_to_index_path(shape: Shape, stable_path: StablePathT) -> PathT:
    cur = normalize_shape(shape)
    out: list[int] = []
    for child_shape, ordinal in stable_path:
        child_shape = normalize_shape(child_shape)
        matches = [i for i, child in enumerate(cur) if child == child_shape]
        if ordinal < 0 or ordinal >= len(matches):
            raise IndexError(f'stable path step not resolvable for child={child_shape!r}, ordinal={ordinal}')
        idx = matches[ordinal]
        out.append(idx)
        cur = cur[idx]
    return tuple(out)

def shape_at_stable(shape: Shape, stable_path: StablePathT) -> Shape:
    return shape_at(shape, stable_path_to_index_path(shape, stable_path))


# === SHAPE EXPLORATION ===

def apply_shape_move(shape: Shape, move: dict) -> Shape:
    root = normalize_shape(shape)
    op = move['op']
    path = move['path']
    if op == 'NEW':
        return shape_new(root)
    if op == 'DROP':
        return shape_drop(root)
    if op == 'INC':
        return shape_inc(root, path)
    if op == 'DEC':
        return shape_dec(root, path)
    raise ValueError(f'unknown shape move op: {op}')

def shape_neighbors(shape: Shape) -> tuple[dict, ...]:
    root = normalize_shape(shape)
    out: list[dict] = []
    candidates: list[tuple[str, PathT]] = [('NEW', ()), ('DROP', ())]
    candidates.extend((('INC', path) for path in shape_paths(root)))
    candidates.extend((('DEC', path) for path in shape_paths(root)))
    for op, path in candidates:
        if not shape_can_apply(root, op, path):
            continue
        out.append({'op': op, 'path': path, 'result': shape_apply(root, op, path)})
    seen = set()
    canon = []
    for row in out:
        key = (row['op'], row['path'], row['result'])
        if key in seen:
            continue
        seen.add(key)
        canon.append(row)
    canon.sort(key=lambda row: (row['op'], row['path'], _shape_key(row['result'])))
    return tuple(canon)

def shape_closure(shape: Shape, depth: int) -> tuple[Shape, ...]:
    if depth < 0:
        raise ValueError('depth must be >= 0')
    root = normalize_shape(shape)
    seen = {root}
    frontier = {root}
    for _ in range(depth):
        next_frontier = set()
        for node in frontier:
            for row in shape_neighbors(node):
                result = row['result']
                if result not in seen:
                    seen.add(result)
                    next_frontier.add(result)
        if not next_frontier:
            break
        frontier = next_frontier
    return tuple(sorted(seen, key=_shape_key))

def shape_frontier_levels(shape: Shape, depth: int) -> tuple[tuple[Shape, ...], ...]:
    if depth < 0:
        raise ValueError('depth must be >= 0')
    root = normalize_shape(shape)
    levels: list[tuple[Shape, ...]] = [(root,)]
    seen = {root}
    frontier = {root}
    for _ in range(depth):
        next_frontier = set()
        for node in frontier:
            for row in shape_neighbors(node):
                result = row['result']
                if result not in seen:
                    seen.add(result)
                    next_frontier.add(result)
        if not next_frontier:
            break
        level = tuple(sorted(next_frontier, key=_shape_key))
        levels.append(level)
        frontier = set(level)
    return tuple(levels)

def shape_shortest_path(start: Shape, target: Shape, max_depth: int=8) -> tuple[dict, ...]:
    if max_depth < 0:
        raise ValueError('max_depth must be >= 0')
    start_n = normalize_shape(start)
    target_n = normalize_shape(target)
    if start_n == target_n:
        return ()
    seen = {start_n}
    parents: dict[Shape, tuple[Shape, dict] | None] = {start_n: None}
    frontier = {start_n}
    for _ in range(max_depth):
        next_frontier = set()
        for node in sorted(frontier, key=_shape_key):
            for move in shape_neighbors(node):
                result = move['result']
                if result in seen:
                    continue
                seen.add(result)
                parents[result] = (node, move)
                if result == target_n:
                    path = []
                    cur = result
                    while parents[cur] is not None:
                        prev, step = parents[cur]
                        path.append(step)
                        cur = prev
                    path.reverse()
                    return tuple(path)
                next_frontier.add(result)
        if not next_frontier:
            break
        frontier = next_frontier
    raise ValueError(f'target shape {target_n!r} not reached from {start_n!r} within max_depth={max_depth}')

def shape_distance(start: Shape, target: Shape, max_depth: int=8) -> int:
    return len(shape_shortest_path(start, target, max_depth=max_depth))


# === PARTIAL CORE ===

def _partial_shape_key(shape) -> tuple:
    if shape is None:
        return (0,)
    return (1, tuple((_partial_shape_key(child) for child in shape)))

def normalize_partial_shape(shape):
    if shape is None:
        return None
    normalized_children = tuple((normalize_partial_shape(child) for child in shape))
    return tuple(sorted(normalized_children, key=_partial_shape_key))

def partial_shape_hole_count(shape) -> int:
    if shape is None:
        return 1
    return sum((partial_shape_hole_count(child) for child in shape))

def shape_matches_partial(shape: Shape, partial) -> bool:
    shape = normalize_shape(shape)
    partial = normalize_partial_shape(partial)
    if partial is None:
        return True
    if len(shape) != len(partial):
        return False
    partial_children = list(partial)
    partial_children.sort(key=lambda child: 1 if child is None else 0)
    used = [False] * len(shape)

    def _match(i: int) -> bool:
        if i == len(partial_children):
            return True
        pchild = partial_children[i]
        for j, schild in enumerate(shape):
            if used[j]:
                continue
            if shape_matches_partial(schild, pchild):
                used[j] = True
                if _match(i + 1):
                    return True
                used[j] = False
        return False
    return _match(0)

def pet_matches_partial_shape(tree, partial) -> bool:
    return shape_matches_partial(pet_to_shape(tree), partial)

def n_matches_partial_shape(n: int, partial) -> bool:
    from pet.core import encode
    return pet_matches_partial_shape(encode(n), partial)

def partial_shape_is_exact(shape) -> bool:
    if shape is None:
        return False
    return all((partial_shape_is_exact(child) for child in shape))

def _partial_shape_fill_min(shape, *, at_root: bool) -> Shape:
    if shape is None:
        return ((),) if at_root else ()
    return normalize_shape(tuple((_partial_shape_fill_min(child, at_root=False) for child in shape)))

def partial_shape_fill_min(shape) -> Shape:
    return _partial_shape_fill_min(normalize_partial_shape(shape), at_root=True)

def partial_shape_gamma_min(shape) -> int:
    return shape_gamma(partial_shape_fill_min(shape))


# === PARTIAL LOCAL COMPLETION ===

def _partial_shape_fill_neighbors(shape, *, at_root: bool):
    shape = normalize_partial_shape(shape)
    if shape is None:
        return (((),),) if at_root else ((),)
    out = set()
    for i, child in enumerate(shape):
        child_neighbors = _partial_shape_fill_neighbors(child, at_root=False)
        if child is None:
            child_neighbors = ((),)
        elif isinstance(child, tuple):
            child_neighbors = _partial_shape_fill_neighbors(child, at_root=False)
        else:
            child_neighbors = ()
        for new_child in child_neighbors:
            children = list(shape)
            children[i] = new_child
            out.add(normalize_partial_shape(tuple(children)))
    return tuple(sorted(out, key=_partial_shape_key))

def partial_shape_completion_neighbors(shape):
    shape = normalize_partial_shape(shape)
    if partial_shape_is_exact(shape):
        return ()
    if shape is None:
        return (((),),)
    out = set()
    for i, child in enumerate(shape):
        if child is None:
            children = list(shape)
            children[i] = ()
            out.add(normalize_partial_shape(tuple(children)))
            continue
        for new_child in partial_shape_completion_neighbors(child):
            children = list(shape)
            children[i] = new_child
            out.add(normalize_partial_shape(tuple(children)))
    return tuple(sorted(out, key=_partial_shape_key))


# === PARTIAL EXACT MIN ===

def partial_shape_min_exact_completions(shape):
    root = normalize_partial_shape(shape)
    if partial_shape_is_exact(root):
        return (normalize_shape(root),)
    seen = {root}
    frontier = {root}
    exact = set()
    while frontier:
        next_frontier = set()
        for node in frontier:
            for nxt in partial_shape_completion_neighbors(node):
                if partial_shape_is_exact(nxt):
                    exact.add(normalize_shape(nxt))
                    continue
                if nxt not in seen:
                    seen.add(nxt)
                    next_frontier.add(nxt)
        frontier = next_frontier
    return tuple(sorted(exact, key=_shape_key))

def partial_shape_gamma_min_exact(shape):
    return tuple((shape_gamma(s) for s in partial_shape_min_exact_completions(shape)))

partial_shape_exact_completions = partial_shape_min_exact_completions

partial_shape_gamma_exact = partial_shape_gamma_min_exact


# === PARTIAL COMPLETION PATHS ===

def partial_shape_shortest_completion_path(shape, target=None):
    start = normalize_partial_shape(shape)
    if partial_shape_is_exact(start):
        exact_start = normalize_shape(start)
        if target is not None and exact_start != normalize_shape(target):
            raise ValueError('exact start shape does not match requested target')
        return (exact_start,)
    if target is None:
        target_set = set(partial_shape_min_exact_completions(start))
    else:
        target_shape = normalize_shape(target)
        if target_shape not in set(partial_shape_min_exact_completions(start)):
            raise ValueError('requested target is not an exact completion of the partial shape')
        target_set = {target_shape}
    _ROOT = object()
    seen = {start}
    parents = {start: _ROOT}
    frontier = {start}
    while frontier:
        next_frontier = set()
        for node in sorted(frontier, key=_partial_shape_key):
            for nxt in partial_shape_completion_neighbors(node):
                if nxt in seen:
                    continue
                seen.add(nxt)
                parents[nxt] = node
                if partial_shape_is_exact(nxt) and normalize_shape(nxt) in target_set:
                    path = [normalize_shape(nxt)]
                    cur = node
                    while cur is not _ROOT:
                        path.append(cur)
                        cur = parents[cur]
                    path.reverse()
                    return tuple(path)
                next_frontier.add(nxt)
        frontier = next_frontier
    raise ValueError('no exact completion path found')

def partial_shape_completion_distance(shape, target=None) -> int:
    return len(partial_shape_shortest_completion_path(shape, target=target)) - 1

def partial_shape_shortest_completion_target(shape, target=None) -> Shape:
    path = partial_shape_shortest_completion_path(shape, target=target)
    return normalize_shape(path[-1])

def partial_shape_shortest_completion_gamma(shape, target=None) -> int:
    return shape_gamma(partial_shape_shortest_completion_target(shape, target=target))

def partial_shape_shortest_completion_pet(shape, target=None):
    return shape_to_pet(partial_shape_shortest_completion_target(shape, target=target))


# === PARTIAL BOUNDED COMPLETION ===

def partial_shape_completion_frontier(shape, max_mass: int) -> tuple[Shape, ...]:
    partial = normalize_partial_shape(shape)
    if max_mass < 0:
        raise ValueError('max_mass must be >= 0')
    out = []
    for mass in range(1, max_mass + 1):
        for exact in _shapes_of_mass(mass):
            if shape_matches_partial(exact, partial):
                out.append(exact)
    out.sort(key=lambda s: (shape_mass(s), _shape_key(s)))
    return tuple(out)

def partial_shape_completion_gamma_frontier(shape, max_mass: int) -> tuple[int, ...]:
    return tuple(sorted((shape_gamma(s) for s in partial_shape_completion_frontier(shape, max_mass))))

def partial_shape_completion_count(shape, max_mass: int) -> int:
    return len(partial_shape_completion_frontier(shape, max_mass))

def partial_shape_completion_levels(shape, max_mass: int) -> tuple[tuple[Shape, ...], ...]:
    partial = normalize_partial_shape(shape)
    if max_mass < 0:
        raise ValueError('max_mass must be >= 0')
    levels = []
    for mass in range(1, max_mass + 1):
        level = tuple((exact for exact in _shapes_of_mass(mass) if shape_matches_partial(exact, partial)))
        levels.append(level)
    return tuple(levels)

def partial_shape_completion_gamma_levels(shape, max_mass: int) -> tuple[tuple[int, ...], ...]:
    return tuple((tuple(sorted((shape_gamma(s) for s in level))) for level in partial_shape_completion_levels(shape, max_mass)))

def partial_shape_completion_profile(shape, max_mass: int) -> dict:
    levels = partial_shape_completion_levels(shape, max_mass)
    per_mass = {}
    cumulative = {}
    total = 0
    for mass, level in enumerate(levels, start=1):
        count = len(level)
        total += count
        per_mass[mass] = count
        cumulative[mass] = total
    return {'partial': normalize_partial_shape(shape), 'max_mass': max_mass, 'per_mass': per_mass, 'cumulative': cumulative, 'total': total}

def partial_shape_completion_gamma_profile(shape, max_mass: int) -> dict:
    levels = partial_shape_completion_levels(shape, max_mass)
    per_mass_count = {}
    per_mass_min_gamma = {}
    per_mass_gammas = {}
    for mass, level in enumerate(levels, start=1):
        gammas = tuple(sorted((shape_gamma(s) for s in level)))
        per_mass_count[mass] = len(level)
        per_mass_gammas[mass] = gammas
        per_mass_min_gamma[mass] = gammas[0] if gammas else None
    return {'partial': normalize_partial_shape(shape), 'max_mass': max_mass, 'per_mass_count': per_mass_count, 'per_mass_min_gamma': per_mass_min_gamma, 'per_mass_gammas': per_mass_gammas}

def partial_shape_completion_report(shape, max_mass: int, preview: int=5) -> dict:
    partial = normalize_partial_shape(shape)
    if max_mass < 0:
        raise ValueError('max_mass must be >= 0')
    if preview < 0:
        raise ValueError('preview must be >= 0')
    count_profile = partial_shape_completion_profile(partial, max_mass)
    gamma_profile = partial_shape_completion_gamma_profile(partial, max_mass)
    frontier = partial_shape_completion_frontier(partial, max_mass)
    min_target_shape = partial_shape_fill_min(partial)
    min_target_gamma = shape_gamma(min_target_shape)
    return {'partial': partial, 'max_mass': max_mass, 'preview': preview, 'is_exact': partial_shape_is_exact(partial), 'hole_count': partial_shape_hole_count(partial), 'fill_min': min_target_shape, 'min_target_shape': min_target_shape, 'min_target_gamma': min_target_gamma, 'completion_count': count_profile['total'], 'per_mass_count': count_profile['per_mass'], 'cumulative_count': count_profile['cumulative'], 'per_mass_min_gamma': gamma_profile['per_mass_min_gamma'], 'preview_exact_shapes': frontier[:preview], 'preview_exact_gammas': tuple(sorted((shape_gamma(s) for s in frontier[:preview])))}


# === REPORTS ===

def partial_shape_report(shape) -> dict:
    partial = normalize_partial_shape(shape)
    target = partial_shape_shortest_completion_target(partial)
    return {'partial': partial, 'is_exact': partial_shape_is_exact(partial), 'hole_count': partial_shape_hole_count(partial), 'fill_min': partial_shape_fill_min(partial), 'completion_distance': partial_shape_completion_distance(partial), 'target_shape': target, 'target_gamma': shape_gamma(target)}


# === PUBLIC API ===

__all__ = [
    "Shape",
    "PathT",
    "StableStepT",
    "StablePathT",
    "PartialShape",
    "normalize_shape",
    "PRIMITIVE_ROOT_OPS",
    "PRIMITIVE_LOCAL_OPS",
    "PRIMITIVE_SHAPE_OPS",
    "is_primitive_shape_op",
    "shape_new",
    "shape_drop",
    "shape_inc",
    "shape_dec",
    "shape_apply",
    "shape_can_apply",
    "shape_succ",
    "shape_pred",
    "shape_mass",
    "shape_gamma",
    "shape_to_pet",
    "pet_to_shape",
    "shape_at",
    "shape_paths",
    "index_path_to_stable_path",
    "stable_path_to_index_path",
    "shape_at_stable",
    "apply_shape_move",
    "shape_neighbors",
    "shape_closure",
    "shape_frontier_levels",
    "shape_shortest_path",
    "shape_distance",
    "normalize_partial_shape",
    "partial_shape_hole_count",
    "shape_matches_partial",
    "pet_matches_partial_shape",
    "n_matches_partial_shape",
    "partial_shape_is_exact",
    "partial_shape_fill_min",
    "partial_shape_gamma_min",
    "partial_shape_completion_neighbors",
    "partial_shape_min_exact_completions",
    "partial_shape_gamma_min_exact",
    "partial_shape_exact_completions",
    "partial_shape_gamma_exact",
    "partial_shape_shortest_completion_path",
    "partial_shape_completion_distance",
    "partial_shape_shortest_completion_target",
    "partial_shape_shortest_completion_gamma",
    "partial_shape_shortest_completion_pet",
    "partial_shape_completion_frontier",
    "partial_shape_completion_gamma_frontier",
    "partial_shape_completion_count",
    "partial_shape_completion_levels",
    "partial_shape_completion_gamma_levels",
    "partial_shape_completion_profile",
    "partial_shape_completion_gamma_profile",
    "partial_shape_completion_report",
    "partial_shape_report",
]


def _merge_exact_shapes_to_forced_core(shapes: tuple[Shape, ...]):
    if not shapes:
        raise ValueError("cannot merge an empty exact-shape family")

    shapes = tuple(normalize_shape(shape) for shape in shapes)

    if all(shape == shapes[0] for shape in shapes):
        return shapes[0]

    arities = {len(shape) for shape in shapes}
    if len(arities) != 1:
        return None

    arity = len(shapes[0])
    children = tuple(
        _merge_exact_shapes_to_forced_core(tuple(shape[i] for shape in shapes))
        for i in range(arity)
    )
    return normalize_partial_shape(children)


def partial_shape_forced_core(shape, max_mass: int):
    partial = normalize_partial_shape(shape)
    exacts = partial_shape_completion_frontier(partial, max_mass)

    if not exacts:
        return None

    return _merge_exact_shapes_to_forced_core(exacts)


def partial_shape_forced_core_report(shape, max_mass: int) -> dict:
    partial = normalize_partial_shape(shape)
    exacts = partial_shape_completion_frontier(partial, max_mass)
    forced_core = partial_shape_forced_core(partial, max_mass)

    stabilization_mass = partial_shape_forced_core_stabilization_mass(partial, max_mass)
    stable_window = partial_shape_forced_core_stable_window(partial, max_mass)

    return {
        "partial": partial,
        "max_mass": max_mass,
        "completion_count": len(exacts),
        "forced_core": forced_core,
        "forced_core_kind": classify_forced_core_pattern(forced_core),
        "reported_in_canonical_coordinates": True,
        "forced_hole_count": partial_shape_hole_count(forced_core),
        "is_exact": partial_shape_is_exact(forced_core) if forced_core is not None else False,
        "fast_preview": False,
        "change_masses": partial_shape_forced_core_change_masses(partial, max_mass),
        "stabilization_mass": stabilization_mass,
        "stable_window": stable_window,
    }


def partial_shape_forced_core_trace(shape, max_mass: int) -> tuple[dict, ...]:
    partial = normalize_partial_shape(shape)

    if max_mass < 0:
        raise ValueError("max_mass must be >= 0")

    rows = []
    prev_forced_core = None
    has_prev = False

    for bound in range(1, max_mass + 1):
        exacts = partial_shape_completion_frontier(partial, bound)
        forced_core = _merge_exact_shapes_to_forced_core(exacts) if exacts else None
        changed = (forced_core != prev_forced_core) if has_prev else True
        change_kind = "start" if not has_prev else classify_forced_core_delta(prev_forced_core, forced_core)

        rows.append({
            "max_mass": bound,
            "completion_count": len(exacts),
            "forced_core": forced_core,
            "prev_forced_core": prev_forced_core if has_prev else None,
            "changed": changed,
            "change_kind": change_kind,
        })

        prev_forced_core = forced_core
        has_prev = True

    return tuple(rows)


def partial_shape_forced_core_change_masses(shape, max_mass: int) -> tuple[int, ...]:
    rows = partial_shape_forced_core_trace(shape, max_mass)
    return tuple(row["max_mass"] for row in rows if row["changed"])


def partial_shape_forced_core_stabilization_mass(shape, max_mass: int):
    rows = partial_shape_forced_core_trace(shape, max_mass)
    positive_rows = [row for row in rows if row["completion_count"] > 0]

    if not positive_rows:
        return None

    for i in range(len(positive_rows)):
        core = positive_rows[i]["forced_core"]
        if all(row["forced_core"] == core for row in positive_rows[i:]):
            return positive_rows[i]["max_mass"]

    return None


def partial_shape_forced_core_stable_window(shape, max_mass: int) -> int:
    rows = partial_shape_forced_core_trace(shape, max_mass)
    if not any(row["completion_count"] > 0 for row in rows):
        return 0

    stabilization_mass = partial_shape_forced_core_stabilization_mass(shape, max_mass)
    if stabilization_mass is None:
        return 0
    return max_mass - stabilization_mass + 1


def partial_shape_forced_core_meets_window(shape, max_mass: int, window: int) -> bool:
    if window < 1:
        raise ValueError("window must be >= 1")
    rows = partial_shape_forced_core_trace(shape, max_mass)
    if not any(row["completion_count"] > 0 for row in rows):
        return False
    return partial_shape_forced_core_stable_window(shape, max_mass) >= window


def partial_shape_refines(specific, general) -> bool:
    specific = normalize_partial_shape(specific)
    general = normalize_partial_shape(general)

    if general is None:
        return True
    if specific is None:
        return general is None

    if len(specific) != len(general):
        return False

    general_children = list(general)
    general_children.sort(key=lambda child: 1 if child is None else 0)

    used = [False] * len(specific)

    def _match(i: int) -> bool:
        if i == len(general_children):
            return True

        gchild = general_children[i]

        for j, schild in enumerate(specific):
            if used[j]:
                continue
            if partial_shape_refines(schild, gchild):
                used[j] = True
                if _match(i + 1):
                    return True
                used[j] = False

        return False

    return _match(0)


def classify_forced_core_delta(prev, cur) -> str:
    prev = normalize_partial_shape(prev)
    cur = normalize_partial_shape(cur)

    if prev == cur:
        return "same"
    if partial_shape_refines(cur, prev):
        return "strengthen"
    if partial_shape_refines(prev, cur):
        return "relax"
    return "reshape"


def classify_forced_core_pattern(forced_core) -> str:
    forced_core = normalize_partial_shape(forced_core)

    if forced_core is None:
        return "empty"

    if partial_shape_is_exact(forced_core):
        return "exact"

    if all(child is None for child in forced_core):
        return "root-arity-only"

    return "partially-structured"


def partial_shape_free_paths(shape, max_mass: int) -> tuple[PathT, ...]:
    forced_core = partial_shape_forced_core(shape, max_mass)

    if forced_core is None:
        return ((),)

    out: list[PathT] = []

    def _walk(node, path: PathT) -> None:
        if node is None:
            out.append(path)
            return
        for i, child in enumerate(node):
            _walk(child, path + (i,))

    _walk(forced_core, ())
    return tuple(out)


def partial_shape_residual(shape, max_mass: int) -> dict:
    partial = normalize_partial_shape(shape)
    report = partial_shape_forced_core_report(partial, max_mass)
    free_paths = partial_shape_free_paths(partial, max_mass)

    return {
        "partial": partial,
        "max_mass": max_mass,
        "forced_core": report["forced_core"],
        "forced_core_kind": report["forced_core_kind"],
        "reported_in_canonical_coordinates": True,
        "free_paths": free_paths,
        "free_path_count": len(free_paths),
        "forced_hole_count": report["forced_hole_count"],
        "fast_preview": False,
        "stable_window": report["stable_window"],
        "stabilization_mass": report["stabilization_mass"],
    }


def _exact_matches_partial_assignments(shape: Shape, partial, path: PathT = ()) -> tuple[dict[PathT, Shape], ...]:
    shape = normalize_shape(shape)
    partial = normalize_partial_shape(partial)

    if partial is None:
        return ({path: shape},)

    if len(shape) != len(partial):
        return ()

    partial_items = list(enumerate(partial))
    partial_items.sort(key=lambda item: (item[1] is None, _partial_shape_key(item[1])))

    out = []
    used = [False] * len(shape)

    def _freeze_map(m: dict[PathT, Shape]):
        return tuple(sorted(m.items()))

    def _backtrack(i: int, acc: dict[PathT, Shape]) -> None:
        if i == len(partial_items):
            out.append(dict(acc))
            return

        orig_idx, pchild = partial_items[i]

        for j, schild in enumerate(shape):
            if used[j]:
                continue
            if not shape_matches_partial(schild, pchild):
                continue

            child_matches = _exact_matches_partial_assignments(schild, pchild, path + (orig_idx,))
            if not child_matches:
                continue

            used[j] = True
            for child_map in child_matches:
                merged = dict(acc)
                merged.update(child_map)
                _backtrack(i + 1, merged)
            used[j] = False

    _backtrack(0, {})

    dedup = {}
    for row in out:
        dedup[_freeze_map(row)] = row
    return tuple(dedup.values())


def exact_shape_local_profile(shape: Shape, partial, free_paths: tuple[PathT, ...]) -> dict[PathT, tuple[Shape, ...]]:
    shape = normalize_shape(shape)
    partial = normalize_partial_shape(partial)
    free_paths = tuple(dict.fromkeys(free_paths))

    if not free_paths:
        return {}

    # Fast path for symmetric families like (None, None) or ((None,), (None,)).
    # When all children of `partial` are identical, sibling positions are
    # interchangeable, so we can union profiles over child subtrees instead of
    # enumerating all exact<->partial assignments.
    if partial is not None and partial and all(child == partial[0] for child in partial):
        suffixes = tuple(dict.fromkeys(path[1:] for path in free_paths if path))
        merged: dict[PathT, set[Shape]] = {}

        for child_shape in shape:
            if () in suffixes:
                merged.setdefault((), set()).add(child_shape)

            nonempty_suffixes = tuple(s for s in suffixes if s)
            if nonempty_suffixes:
                child_local = exact_shape_local_profile(child_shape, partial[0], nonempty_suffixes)
                for suffix, values in child_local.items():
                    merged.setdefault(suffix, set()).update(values)

        out = {}
        for path in free_paths:
            suffix = path[1:] if path else ()
            out[path] = tuple(sorted(merged.get(suffix, set()), key=_shape_key))
        return out

    assignments = _exact_matches_partial_assignments(shape, partial)
    out = {path: set() for path in free_paths}

    for row in assignments:
        for path in free_paths:
            if path in row:
                out[path].add(row[path])

    return {
        path: tuple(sorted(values, key=_shape_key))
        for path, values in out.items()
    }


@lru_cache(maxsize=None)
@lru_cache(maxsize=None)
def shape_local_gamma(shape: Shape) -> int:
    return _exp_gamma(normalize_shape(shape))


def partial_shape_residual_profile(shape, max_mass: int, preview: int = 5) -> dict:
    partial = normalize_partial_shape(shape)
    residual = partial_shape_residual(partial, max_mass)
    frontier = partial_shape_completion_frontier(partial, max_mass)
    forced_core = residual["forced_core"]

    per_path_values = {path: set() for path in residual["free_paths"]}

    # Fast path: symmetric root-only freedom, e.g. forced_core == (None, None).
    # In this regime every free path is an interchangeable root child, so the
    # local observed family is just the union of root children over the frontier.
    if (
        forced_core is not None
        and forced_core
        and all(child is None for child in forced_core)
        and residual["free_paths"]
        and all(len(path) == 1 for path in residual["free_paths"])
    ):
        pooled = set()
        for exact in frontier:
            for child in exact:
                pooled.add(child)
        for path in residual["free_paths"]:
            per_path_values[path] = set(pooled)
    else:
        for exact in frontier:
            local = exact_shape_local_profile(exact, forced_core, residual["free_paths"])
            for path, values in local.items():
                per_path_values[path].update(values)

    per_path = {}
    for path in residual["free_paths"]:
        local_shapes = tuple(sorted(per_path_values[path], key=_shape_key))
        local_gammas = tuple(sorted(shape_local_gamma(s) for s in local_shapes))
        local_forced_core = _merge_exact_shapes_to_forced_core(local_shapes) if local_shapes else None
        per_path[path] = {
            "count": len(local_shapes),
            "preview_shapes": local_shapes[:preview],
            "preview_local_gammas": local_gammas[:preview],
            "local_forced_core": local_forced_core,
            "local_forced_core_kind": classify_forced_core_pattern(local_forced_core),
        }

    return {
        "partial": partial,
        "max_mass": max_mass,
        "preview": preview,
        "forced_core": residual["forced_core"],
        "forced_core_kind": residual["forced_core_kind"],
        "reported_in_canonical_coordinates": True,
        "free_paths": residual["free_paths"],
        "free_path_count": residual["free_path_count"],
        "per_path": per_path,
    }


def partial_shape_residual_summary(shape, max_mass: int, preview: int = 5) -> dict:
    partial = normalize_partial_shape(shape)
    profile = partial_shape_residual_profile(partial, max_mass, preview=preview)
    residual = partial_shape_residual(partial, max_mass)

    per_path_summary = {}
    for path, row in profile["per_path"].items():
        per_path_summary[path] = {
            "local_forced_core": row["local_forced_core"],
            "local_forced_core_kind": row["local_forced_core_kind"],
            "observed_local_gammas": row["preview_local_gammas"],
            "observed_local_shapes": row["preview_shapes"],
            "observed_local_count": row["count"],
        }

    return {
        "partial": partial,
        "max_mass": max_mass,
        "preview": preview,
        "forced_core": residual["forced_core"],
        "forced_core_kind": residual["forced_core_kind"],
        "reported_in_canonical_coordinates": True,
        "free_paths": residual["free_paths"],
        "free_path_count": residual["free_path_count"],
        "forced_hole_count": residual["forced_hole_count"],
        "stable_window": residual["stable_window"],
        "stabilization_mass": residual["stabilization_mass"],
        "per_path_summary": per_path_summary,
    }


# --- hotfix override: residual fast_preview support ---
def partial_shape_residual_profile(shape, max_mass: int, preview: int = 5, fast_preview: bool = False) -> dict:
    partial = normalize_partial_shape(shape)
    residual = partial_shape_residual(partial, max_mass)
    frontier = partial_shape_completion_frontier(partial, max_mass)
    forced_core = residual["forced_core"]

    per_path_values = {path: set() for path in residual["free_paths"]}

    # Fast path: symmetric root-only freedom, e.g. forced_core == (None, None).
    if (
        forced_core is not None
        and forced_core
        and all(child is None for child in forced_core)
        and residual["free_paths"]
        and all(len(path) == 1 for path in residual["free_paths"])
    ):
        pooled = set()
        for exact in frontier:
            for child in exact:
                pooled.add(child)
        for path in residual["free_paths"]:
            per_path_values[path] = set(pooled)
    else:
        for exact in frontier:
            local = exact_shape_local_profile(exact, forced_core, residual["free_paths"])
            for path, values in local.items():
                per_path_values[path].update(values)

    per_path = {}
    for path in residual["free_paths"]:
        local_shapes = tuple(sorted(per_path_values[path], key=_shape_key))
        preview_shapes = local_shapes[:preview]
        preview_local_gammas = tuple(sorted(shape_local_gamma(s) for s in preview_shapes))

        if fast_preview:
            local_forced_core = None
            local_forced_core_kind = "skipped-fast-preview"
        else:
            local_forced_core = _merge_exact_shapes_to_forced_core(local_shapes) if local_shapes else None
            local_forced_core_kind = classify_forced_core_pattern(local_forced_core)

        per_path[path] = {
            "count": len(local_shapes),
            "preview_shapes": preview_shapes,
            "preview_local_gammas": preview_local_gammas,
            "local_forced_core": local_forced_core,
            "local_forced_core_kind": local_forced_core_kind,
        }

    return {
        "partial": partial,
        "max_mass": max_mass,
        "preview": preview,
        "fast_preview": fast_preview,
        "forced_core": residual["forced_core"],
        "forced_core_kind": residual["forced_core_kind"],
        "reported_in_canonical_coordinates": True,
        "free_paths": residual["free_paths"],
        "free_path_count": residual["free_path_count"],
        "per_path": per_path,
    }


def partial_shape_residual_summary(shape, max_mass: int, preview: int = 5, fast_preview: bool = False) -> dict:
    partial = normalize_partial_shape(shape)
    profile = partial_shape_residual_profile(partial, max_mass, preview=preview, fast_preview=fast_preview)
    residual = partial_shape_residual(partial, max_mass)

    per_path_summary = {}
    for path, row in profile["per_path"].items():
        per_path_summary[path] = {
            "local_forced_core": row["local_forced_core"],
            "local_forced_core_kind": row["local_forced_core_kind"],
            "observed_local_gammas": row["preview_local_gammas"],
            "observed_local_shapes": row["preview_shapes"],
            "observed_local_count": row["count"],
        }

    return {
        "partial": partial,
        "max_mass": max_mass,
        "preview": preview,
        "fast_preview": profile["fast_preview"],
        "forced_core": residual["forced_core"],
        "forced_core_kind": residual["forced_core_kind"],
        "reported_in_canonical_coordinates": True,
        "free_paths": residual["free_paths"],
        "free_path_count": residual["free_path_count"],
        "forced_hole_count": residual["forced_hole_count"],
        "stable_window": residual["stable_window"],
        "stabilization_mass": residual["stabilization_mass"],
        "per_path_summary": per_path_summary,
    }


def partial_shape_observed_decomposition(shape, max_mass: int, preview: int = 5, fast_preview: bool = False) -> dict:
    partial = normalize_partial_shape(shape)
    summary = partial_shape_residual_summary(
        partial,
        max_mass=max_mass,
        preview=preview,
        fast_preview=fast_preview,
    )

    return {
        "partial": summary["partial"],
        "observed_core": summary["forced_core"],
        "observed_core_kind": summary["forced_core_kind"],
        "reported_in_canonical_coordinates": True,
        "residual_free_paths": summary["free_paths"],
        "residual_free_path_count": summary["free_path_count"],
        "residual_local_profiles": summary["per_path_summary"],
        "evidence": {
            "max_mass": summary["max_mass"],
            "preview": summary["preview"],
            "fast_preview": summary["fast_preview"],
            "stable_window": summary["stable_window"],
            "stabilization_mass": summary["stabilization_mass"],
            "forced_hole_count": summary["forced_hole_count"],
        },
    }
