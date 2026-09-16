"""Bounded A* search over PETRA canonical shapes.

This module is a derived layer. It imports from the canonical ``petra``
package and never the other way around. It does not extend PETRA
semantics: it only searches the graph induced by the four canonical
operators.

The search uses A* with an admissible heuristic based on three structural
lower bounds:

- node-count distance / 2,
- maximum-depth distance,
- leaf-count distance.

Per-shape metrics are cached by object identity during one ``resolve``
call. This is safe because all visited shapes are kept alive by the
frontier and the visited set, so identity is never reused within a call.
"""

from __future__ import annotations

import heapq
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from itertools import count

from petra import (
    Address,
    Container,
    DefaultTarget,
    ExplicitTarget,
    Leaf,
    Operator,
    PetraShape,
    SuccessfulResult,
    apply_graft,
    apply_prune,
    apply_shed,
    apply_sprout,
    parse_shape,
    validate_shape,
)

from .projection import PrimeKey, ProjectionError, project

_OPERATORS = (
    Operator.SPROUT,
    Operator.SHED,
    Operator.GRAFT,
    Operator.PRUNE,
)

_APPLY = {
    Operator.SPROUT: apply_sprout,
    Operator.SHED: apply_shed,
    Operator.GRAFT: apply_graft,
    Operator.PRUNE: apply_prune,
}


class ResolverError(ValueError):
    """A deterministic Resolver failure."""


@dataclass(frozen=True)
class Step:
    """One structural edit along a resolved path."""

    operator: Operator
    invocation_target: DefaultTarget | ExplicitTarget
    before_shape: PetraShape
    after_shape: PetraShape
    value_before: int | None = None
    value_after: int | None = None


@dataclass(frozen=True)
class Path:
    """A bounded shortest path between two canonical PETRA shapes."""

    source: PetraShape
    target: PetraShape
    steps: tuple[Step, ...]
    value_source: int | None = None
    value_target: int | None = None
    explored: int = 0

    @property
    def length(self) -> int:
        return len(self.steps)


def _node_count(shape: PetraShape) -> int:
    """Count Leaf, Container, and Term nodes iteratively."""

    total = 0
    stack: list[PetraShape] = [shape]
    while stack:
        current = stack.pop()
        total += 1
        if isinstance(current, Container):
            total += len(current.terms)
            for term in current.terms:
                stack.append(term.exponent)
    return total


def _max_depth(shape: PetraShape) -> int:
    """Return the maximum nesting depth of a shape (Leaf = 0)."""

    if isinstance(shape, Leaf):
        return 0
    best = 0
    stack: list[tuple[PetraShape, int]] = [(shape, 0)]
    while stack:
        current, level = stack.pop()
        if level > best:
            best = level
        if isinstance(current, Container):
            for term in current.terms:
                stack.append((term.exponent, level + 1))
    return best


def _leaf_count(shape: PetraShape) -> int:
    """Count Leaf nodes in a shape."""

    total = 0
    stack: list[PetraShape] = [shape]
    while stack:
        current = stack.pop()
        if isinstance(current, Leaf):
            total += 1
            continue
        assert isinstance(current, Container)
        for term in current.terms:
            stack.append(term.exponent)
    return total


def _all_term_addresses(
    shape: PetraShape,
) -> Iterator[tuple[Address, bool, bool]]:
    """Yield (address, is_leaf, is_singleton_child) for every term."""

    if not isinstance(shape, Container):
        return

    def visit(
        current: Container,
        prefix: tuple[int, ...],
        nested: bool,
    ) -> Iterator[tuple[Address, bool, bool]]:
        for index, term in enumerate(current.terms):
            indices = (*prefix, index)
            is_leaf = isinstance(term.exponent, Leaf)
            is_singleton = nested and len(current.terms) == 1
            yield Address(indices=indices), is_leaf, is_singleton
            if isinstance(term.exponent, Container):
                yield from visit(term.exponent, indices, nested=True)

    yield from visit(shape, (), nested=False)


def _relevant_addresses(
    shape: PetraShape,
    operator: Operator,
) -> Iterator[Address]:
    """Yield only the addresses where the operator can legally act."""

    if operator is Operator.SPROUT:
        yield Address()
        for address, is_leaf, _ in _all_term_addresses(shape):
            if not is_leaf:
                yield address
        return

    if operator is Operator.SHED:
        for address, is_leaf, _ in _all_term_addresses(shape):
            if is_leaf:
                yield address
        return

    if operator is Operator.GRAFT:
        for address, is_leaf, _ in _all_term_addresses(shape):
            if is_leaf:
                yield Address(indices=address.indices, is_slot=True)
        return

    if operator is Operator.PRUNE:
        for address, is_leaf, is_singleton in _all_term_addresses(shape):
            if is_leaf and is_singleton:
                yield address
        return

    raise AssertionError(f"unknown operator: {operator}")


def _try_neighbor(
    shape: PetraShape,
    operator: Operator,
    target: DefaultTarget | ExplicitTarget,
    seen: set[PetraShape],
) -> Step | None:
    result = _APPLY[operator](shape, target)
    if not isinstance(result, SuccessfulResult):
        return None
    if result.after_shape in seen:
        return None
    seen.add(result.after_shape)
    return Step(
        operator=operator,
        invocation_target=target,
        before_shape=shape,
        after_shape=result.after_shape,
    )


def _neighbors(shape: PetraShape) -> Iterator[Step]:
    """Yield every canonical one-step neighbor reachable from the shape."""

    seen: set[PetraShape] = {shape}

    for operator in _OPERATORS:
        step = _try_neighbor(shape, operator, DefaultTarget(), seen)
        if step is not None:
            yield step

        for address in _relevant_addresses(shape, operator):
            step = _try_neighbor(
                shape, operator, ExplicitTarget(address), seen
            )
            if step is not None:
                yield step


def _try_project(shape: PetraShape, key: PrimeKey) -> int | None:
    try:
        return project(shape, key)
    except ProjectionError:
        return None


def _enrich_path(path: Path, key: PrimeKey) -> Path:
    enriched_steps = tuple(
        Step(
            operator=step.operator,
            invocation_target=step.invocation_target,
            before_shape=step.before_shape,
            after_shape=step.after_shape,
            value_before=_try_project(step.before_shape, key),
            value_after=_try_project(step.after_shape, key),
        )
        for step in path.steps
    )

    return Path(
        source=path.source,
        target=path.target,
        steps=enriched_steps,
        value_source=_try_project(path.source, key),
        value_target=_try_project(path.target, key),
        explored=path.explored,
    )


def _build_cached_metrics(
    target_shape: PetraShape,
) -> tuple[
    Callable[[PetraShape], int],
    Callable[[PetraShape], int],
]:
    """Return (heuristic, node_count) closures with per-call caches."""

    node_cache: dict[int, int] = {}
    depth_cache: dict[int, int] = {}
    leaf_cache: dict[int, int] = {}
    heuristic_cache: dict[int, int] = {}

    target_nodes = _node_count(target_shape)
    target_depth = _max_depth(target_shape)
    target_leaves = _leaf_count(target_shape)

    def node_count(shape: PetraShape) -> int:
        key = shape
        cached = node_cache.get(key)
        if cached is None:
            cached = _node_count(shape)
            node_cache[key] = cached
        return cached

    def max_depth(shape: PetraShape) -> int:
        key = shape
        cached = depth_cache.get(key)
        if cached is None:
            cached = _max_depth(shape)
            depth_cache[key] = cached
        return cached

    def leaf_count(shape: PetraShape) -> int:
        key = shape
        cached = leaf_cache.get(key)
        if cached is None:
            cached = _leaf_count(shape)
            leaf_cache[key] = cached
        return cached

    def heuristic(shape: PetraShape) -> int:
        key = shape
        cached = heuristic_cache.get(key)
        if cached is None:
            cached = max(
                abs(node_count(shape) - target_nodes) // 2,
                abs(max_depth(shape) - target_depth),
                abs(leaf_count(shape) - target_leaves),
            )
            heuristic_cache[key] = cached
        return cached

    return heuristic, node_count


def resolve(
    source: str | PetraShape,
    target: str | PetraShape,
    *,
    max_depth: int = 10,
    max_nodes: int = 20,
    max_visited: int = 1000,
    key: PrimeKey | None = None,
) -> Path:
    """Find the shortest canonical edit path between two shapes using A*."""

    if max_depth < 0:
        raise ResolverError("max_depth must be >= 0")
    if max_nodes < 1:
        raise ResolverError("max_nodes must be >= 1")
    if max_visited < 1:
        raise ResolverError("max_visited must be >= 1")

    source_shape = _coerce(source)
    target_shape = _coerce(target)

    validate_shape(source_shape)
    validate_shape(target_shape)

    if source_shape == target_shape:
        path = Path(
            source=source_shape, target=target_shape, steps=(), explored=0
        )
        return _enrich_path(path, key) if key is not None else path

    heuristic, node_count = _build_cached_metrics(target_shape)

    if node_count(source_shape) > max_nodes:
        raise ResolverError("source shape exceeds max_nodes")
    if node_count(target_shape) > max_nodes:
        raise ResolverError("target shape exceeds max_nodes")

    tie = count()
    h0 = heuristic(source_shape)
    open_set: list[tuple[int, int, int, PetraShape, tuple[Step, ...]]] = [
        (h0, 0, next(tie), source_shape, ())
    ]
    best_g: dict[PetraShape, int] = {source_shape: 0}
    explored = 0

    while open_set:
        _f, g, _, current_shape, current_path = heapq.heappop(open_set)

        if best_g.get(current_shape, g + 1) < g:
            continue

        if len(current_path) >= max_depth:
            continue

        explored += 1
        if explored > max_visited:
            raise ResolverError(
                "explored more than "
                f"{max_visited} shapes without finding a path"
            )

        if current_shape == target_shape:
            path = Path(
                source=source_shape,
                target=target_shape,
                steps=current_path,
                explored=explored,
            )
            return _enrich_path(path, key) if key is not None else path

        for step in _neighbors(current_shape):
            neighbor = step.after_shape
            if node_count(neighbor) > max_nodes:
                continue

            new_g = g + 1
            if new_g >= best_g.get(neighbor, float("inf")):
                continue

            best_g[neighbor] = new_g
            new_path = (*current_path, step)
            new_f = new_g + heuristic(neighbor)
            heapq.heappush(
                open_set,
                (new_f, new_g, next(tie), neighbor, new_path),
            )

    raise ResolverError(
        f"no path found within max_depth={max_depth}, "
        f"max_nodes={max_nodes}"
    )


def _coerce(value: str | PetraShape) -> PetraShape:
    if isinstance(value, str):
        return parse_shape(value)
    if isinstance(value, (Leaf, Container)):
        return value
    raise ResolverError(
        "expected a canonical PETRA shape or its textual form"
    )
