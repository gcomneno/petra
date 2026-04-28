from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def test_shape_new_and_drop_roundtrip_on_root_children():
    from tools.pet_shape_algebra import normalize_shape, shape_new, shape_drop

    base = normalize_shape(((), ((),)))
    grown = shape_new(base)

    assert grown == normalize_shape(((), (), ((),)))
    assert shape_drop(grown) == base


def test_shape_succ_small_chain():
    from tools.pet_shape_algebra import shape_succ

    assert shape_succ(()) == ((),)
    assert shape_succ(((),)) == ((), ())
    assert shape_succ(((), ())) == (((),),)


def test_shape_pred_inverts_shape_succ_on_small_chain():
    from tools.pet_shape_algebra import shape_pred, shape_succ

    samples = [
        (),
        ((),),
        ((), ()),
        (((),),),
    ]

    for shape in samples[:-1]:
        assert shape_pred(shape_succ(shape)) == shape


def test_shape_inc_and_dec_roundtrip_on_single_root_child():
    from tools.pet_shape_algebra import normalize_shape, shape_dec, shape_inc

    base = normalize_shape(((),))
    grown = shape_inc(base, (0,))

    assert grown == normalize_shape((((),),))
    assert shape_dec(grown, (0,)) == base


def test_shape_inc_and_dec_roundtrip_on_deep_chain():
    from tools.pet_shape_algebra import normalize_shape, shape_dec, shape_inc

    base = normalize_shape(((((),),),))
    grown = shape_inc(base, (0, 0, 0))

    assert grown == normalize_shape((((((),),),),))
    assert shape_dec(grown, (0, 0, 0)) == base


def test_pet_to_shape_small_numbers():
    from pet.core import encode
    from tools.pet_shape_algebra import pet_to_shape

    assert pet_to_shape(encode(2)) == ((),)
    assert pet_to_shape(encode(3)) == ((),)
    assert pet_to_shape(encode(4)) == (((),),)
    assert pet_to_shape(encode(6)) == ((), ())
    assert pet_to_shape(encode(8)) == (((),),)


def test_shape_gamma_small_shapes():
    from tools.pet_shape_algebra import shape_gamma

    assert shape_gamma(((),)) == 2
    assert shape_gamma(((), ())) == 6
    assert shape_gamma((((),),)) == 4
    assert shape_gamma(((), ((),))) == 12


def test_shape_to_pet_roundtrip_via_pet_to_shape():
    from pet.core import decode
    from tools.pet_shape_algebra import pet_to_shape, shape_gamma, shape_to_pet

    shapes = [
        ((),),
        ((), ()),
        (((),),),
        ((), ((),)),
    ]

    for shape in shapes:
        pet = shape_to_pet(shape)
        assert pet_to_shape(pet) == shape
        assert decode(pet) == shape_gamma(shape)


def test_shape_gamma_matches_core_shape_generator_on_small_sample():
    from pet.core import encode, shape_generator
    from tools.pet_shape_algebra import pet_to_shape, shape_gamma

    sample = [2, 3, 4, 6, 8, 12, 18, 24, 36, 72]

    for n in sample:
        assert shape_gamma(pet_to_shape(encode(n))) == shape_generator(n)


def test_shape_to_pet_materializes_core_generator_on_small_sample():
    from pet.core import decode, encode, shape_generator
    from tools.pet_shape_algebra import pet_to_shape, shape_to_pet

    sample = [2, 3, 4, 6, 8, 12, 18, 24, 36, 72]

    for n in sample:
        shape = pet_to_shape(encode(n))
        assert decode(shape_to_pet(shape)) == shape_generator(n)


def test_shape_at_reads_deep_node():
    from tools.pet_shape_algebra import normalize_shape, shape_at

    shape = normalize_shape(((((),),),))
    assert shape_at(shape, ()) == shape
    assert shape_at(shape, (0,)) == (((),),)
    assert shape_at(shape, (0, 0)) == ((),)
    assert shape_at(shape, (0, 0, 0)) == ()


def test_shape_paths_lists_all_nodes():
    from tools.pet_shape_algebra import normalize_shape, shape_paths

    shape = normalize_shape(((), ((),)))
    assert shape_paths(shape) == ((0,), (1,), (1, 0))
    assert shape_paths(shape, include_root=True) == ((), (0,), (1,), (1, 0))


def test_shape_neighbors_for_single_leaf_child():
    from tools.pet_shape_algebra import normalize_shape, shape_neighbors

    shape = normalize_shape(((),))
    moves = shape_neighbors(shape)

    got = {(row["op"], row["path"], row["result"]) for row in moves}
    expected = {
        ("NEW", (), normalize_shape(((), ()))),
        ("DROP", (), normalize_shape(())),
        ("INC", (0,), normalize_shape((((),),))),
    }

    assert got == expected


def test_shape_neighbors_for_single_recursive_child():
    from tools.pet_shape_algebra import normalize_shape, shape_neighbors

    shape = normalize_shape((((),),))
    moves = shape_neighbors(shape)

    got = {(row["op"], row["path"], row["result"]) for row in moves}
    expected = {
        ("NEW", (), normalize_shape(((), ((),)))),
        ("INC", (0,), normalize_shape((((), ()),))),
        ("INC", (0, 0), normalize_shape(((((),),),))),
        ("DEC", (0,), normalize_shape(((),))),
    }

    assert got == expected


def test_shape_closure_depth_zero_returns_only_root():
    from tools.pet_shape_algebra import normalize_shape, shape_closure

    shape = normalize_shape(((),))
    assert shape_closure(shape, 0) == (shape,)


def test_shape_closure_depth_one_matches_immediate_reachable_shapes():
    from tools.pet_shape_algebra import normalize_shape, shape_closure

    shape = normalize_shape(((),))
    got = set(shape_closure(shape, 1))
    expected = {
        normalize_shape(((),)),
        normalize_shape(()),
        normalize_shape(((), ())),
        normalize_shape((((),),)),
    }

    assert got == expected


def test_shape_closure_normalizes_input_shape():
    from tools.pet_shape_algebra import shape_closure

    got = set(shape_closure((((),), ()), 0))
    expected = { ((), ((),)) }

    assert got == expected


def test_shape_frontier_levels_depth_zero():
    from tools.pet_shape_algebra import normalize_shape, shape_frontier_levels

    shape = normalize_shape(((),))
    assert shape_frontier_levels(shape, 0) == ((shape,),)


def test_shape_frontier_levels_depth_one_from_single_leaf_child():
    from tools.pet_shape_algebra import normalize_shape, shape_frontier_levels

    shape = normalize_shape(((),))
    levels = shape_frontier_levels(shape, 1)

    assert levels[0] == (shape,)
    assert set(levels[1]) == {
        normalize_shape(()),
        normalize_shape(((), ())),
        normalize_shape((((),),)),
    }


def test_shape_frontier_levels_depth_two_has_no_duplicates_across_levels():
    from tools.pet_shape_algebra import normalize_shape, shape_frontier_levels

    shape = normalize_shape(((),))
    levels = shape_frontier_levels(shape, 2)

    flat = [node for level in levels for node in level]
    assert len(flat) == len(set(flat))


def test_shape_shortest_path_identity_is_empty():
    from tools.pet_shape_algebra import normalize_shape, shape_shortest_path

    shape = normalize_shape(((),))
    assert shape_shortest_path(shape, shape) == ()


def test_shape_shortest_path_single_step_inc():
    from tools.pet_shape_algebra import (
        apply_shape_move,
        normalize_shape,
        shape_shortest_path,
    )

    start = normalize_shape(((),))
    target = normalize_shape((((),),))

    path = shape_shortest_path(start, target, max_depth=2)

    assert len(path) == 1
    assert path[0]["op"] == "INC"
    assert path[0]["path"] == (0,)
    assert apply_shape_move(start, path[0]) == target


def test_shape_shortest_path_single_step_drop():
    from tools.pet_shape_algebra import (
        apply_shape_move,
        normalize_shape,
        shape_shortest_path,
    )

    start = normalize_shape(((),))
    target = normalize_shape(())

    path = shape_shortest_path(start, target, max_depth=2)

    assert len(path) == 1
    assert path[0]["op"] == "DROP"
    assert path[0]["path"] == ()
    assert apply_shape_move(start, path[0]) == target


def test_shape_shortest_path_two_steps_to_root_new_then_inc():
    from tools.pet_shape_algebra import (
        apply_shape_move,
        normalize_shape,
        shape_shortest_path,
    )

    start = normalize_shape(())
    target = normalize_shape((((),),))

    path = shape_shortest_path(start, target, max_depth=3)

    cur = start
    for step in path:
        cur = apply_shape_move(cur, step)

    assert cur == target
    assert len(path) == 2


def test_shape_distance_identity_is_zero():
    from tools.pet_shape_algebra import normalize_shape, shape_distance

    shape = normalize_shape(((),))
    assert shape_distance(shape, shape) == 0


def test_shape_distance_single_step_cases():
    from tools.pet_shape_algebra import normalize_shape, shape_distance

    assert shape_distance(normalize_shape(((),)), normalize_shape(()), max_depth=2) == 1
    assert shape_distance(normalize_shape(((),)), normalize_shape((((),),)), max_depth=2) == 1


def test_shape_distance_two_step_case():
    from tools.pet_shape_algebra import normalize_shape, shape_distance

    start = normalize_shape(())
    target = normalize_shape((((),),))
    assert shape_distance(start, target, max_depth=3) == 2


def test_shape_succ_moves_past_old_hardcoded_prefix():
    from tools.pet_shape_algebra import shape_succ

    assert shape_succ((((),),)) == ((), (), ())


def test_shape_pred_inverts_extended_successor_step():
    from tools.pet_shape_algebra import shape_pred, shape_succ

    shape = (((),),)
    assert shape_pred(shape_succ(shape)) == shape


def test_stable_path_roundtrip_on_duplicate_leaf_siblings():
    from tools.pet_shape_algebra import (
        index_path_to_stable_path,
        normalize_shape,
        stable_path_to_index_path,
    )

    shape = normalize_shape(((), (), ((),)))
    path = (1,)

    stable = index_path_to_stable_path(shape, path)

    assert stable == (((), 1),)
    assert stable_path_to_index_path(shape, stable) == path


def test_stable_path_roundtrip_on_duplicate_recursive_siblings():
    from tools.pet_shape_algebra import (
        index_path_to_stable_path,
        normalize_shape,
        stable_path_to_index_path,
    )

    shape = normalize_shape((((),), ((),), ((), ())))
    path = (1, 0)

    stable = index_path_to_stable_path(shape, path)

    assert stable == ((((),), 1), ((), 0))
    assert stable_path_to_index_path(shape, stable) == path


def test_shape_at_stable_reads_same_node_as_shape_at():
    from tools.pet_shape_algebra import (
        index_path_to_stable_path,
        normalize_shape,
        shape_at,
        shape_at_stable,
    )

    shape = normalize_shape((((),), ((),), ((), ())))
    path = (2, 1)
    stable = index_path_to_stable_path(shape, path)

    assert shape_at_stable(shape, stable) == shape_at(shape, path)


def test_shape_apply_dispatches_all_four_primitives():
    from tools.pet_shape_algebra import normalize_shape, shape_apply

    assert shape_apply(normalize_shape(((),)), "NEW") == normalize_shape(((), ()))
    assert shape_apply(normalize_shape(((),)), "DROP") == normalize_shape(())
    assert shape_apply(normalize_shape(((),)), "INC", (0,)) == normalize_shape((((),),))
    assert shape_apply(normalize_shape((((),),)), "DEC", (0,)) == normalize_shape(((),))


def test_shape_apply_rejects_bad_root_usage():
    import pytest
    from tools.pet_shape_algebra import normalize_shape, shape_apply

    shape = normalize_shape(((),))

    with pytest.raises(ValueError):
        shape_apply(shape, "NEW", (0,))

    with pytest.raises(ValueError):
        shape_apply(shape, "DROP", (0,))

    with pytest.raises(ValueError):
        shape_apply(shape, "INC", ())

    with pytest.raises(ValueError):
        shape_apply(shape, "DEC", ())


def test_shape_can_apply_reports_basic_cases():
    from tools.pet_shape_algebra import normalize_shape, shape_can_apply

    assert shape_can_apply(normalize_shape(((),)), "NEW")
    assert shape_can_apply(normalize_shape(((),)), "DROP")
    assert shape_can_apply(normalize_shape(((),)), "INC", (0,))
    assert shape_can_apply(normalize_shape((((),),)), "DEC", (0,))

    assert not shape_can_apply(normalize_shape(()), "DROP")
    assert not shape_can_apply(normalize_shape(((),)), "INC", ())
    assert not shape_can_apply(normalize_shape(((),)), "NOPE")


def test_shape_neighbors_matches_dispatcher_results():
    from tools.pet_shape_algebra import (
        normalize_shape,
        shape_apply,
        shape_can_apply,
        shape_neighbors,
        shape_paths,
    )

    shape = normalize_shape((((),),))
    got = {(row["op"], row["path"], row["result"]) for row in shape_neighbors(shape)}

    expected = set()
    candidates = [("NEW", ()), ("DROP", ())]
    candidates.extend(("INC", path) for path in shape_paths(shape))
    candidates.extend(("DEC", path) for path in shape_paths(shape))

    for op, path in candidates:
        if shape_can_apply(shape, op, path):
            expected.add((op, path, shape_apply(shape, op, path)))

    assert got == expected


def test_primitive_shape_op_sets_are_exactly_the_four_core_ops():
    from tools.pet_shape_algebra import (
        PRIMITIVE_LOCAL_OPS,
        PRIMITIVE_ROOT_OPS,
        PRIMITIVE_SHAPE_OPS,
    )

    assert PRIMITIVE_ROOT_OPS == ("NEW", "DROP")
    assert PRIMITIVE_LOCAL_OPS == ("INC", "DEC")
    assert PRIMITIVE_SHAPE_OPS == ("NEW", "DROP", "INC", "DEC")


def test_is_primitive_shape_op_accepts_only_core_ops():
    from tools.pet_shape_algebra import is_primitive_shape_op

    assert is_primitive_shape_op("NEW")
    assert is_primitive_shape_op("DROP")
    assert is_primitive_shape_op("INC")
    assert is_primitive_shape_op("DEC")
    assert not is_primitive_shape_op("new")
    assert not is_primitive_shape_op("SUCC")
    assert not is_primitive_shape_op("PRED")
    assert not is_primitive_shape_op("NOPE")


def test_shape_neighbors_emit_only_primitive_ops():
    from tools.pet_shape_algebra import (
        PRIMITIVE_SHAPE_OPS,
        normalize_shape,
        shape_neighbors,
    )

    shape = normalize_shape((((),),))
    assert {row["op"] for row in shape_neighbors(shape)} <= set(PRIMITIVE_SHAPE_OPS)


def test_normalize_partial_shape_sorts_known_children_and_holes():
    from tools.pet_shape_algebra import normalize_partial_shape

    partial = (((),), None, ())
    assert normalize_partial_shape(partial) == (None, (), ((),))


def test_partial_shape_hole_count_counts_unknown_subtrees():
    from tools.pet_shape_algebra import partial_shape_hole_count

    assert partial_shape_hole_count(None) == 1
    assert partial_shape_hole_count((None, (), (None,))) == 2


def test_shape_matches_partial_for_exact_and_unknown_cases():
    from tools.pet_shape_algebra import normalize_shape, shape_matches_partial

    assert shape_matches_partial(normalize_shape(((),)), None)
    assert shape_matches_partial(normalize_shape(((), ())), (None, ()))
    assert shape_matches_partial(normalize_shape((((),),)), ((None,),))
    assert not shape_matches_partial(normalize_shape(((),)), ((), ()))
    assert not shape_matches_partial(normalize_shape(((), ())), (((),), ()))


def test_shape_matches_partial_on_small_core_generators():
    from pet.core import encode
    from tools.pet_shape_algebra import pet_to_shape, shape_matches_partial

    assert shape_matches_partial(pet_to_shape(encode(6)), ((), ()))
    assert shape_matches_partial(pet_to_shape(encode(12)), ((), None))
    assert not shape_matches_partial(pet_to_shape(encode(8)), ((), ()))


def test_partial_shape_fill_min_handles_root_hole_and_inner_holes():
    from tools.pet_shape_algebra import partial_shape_fill_min

    assert partial_shape_fill_min(None) == ((),)
    assert partial_shape_fill_min((None,)) == ((),)
    assert partial_shape_fill_min((None, (None,))) == ((), ((),))


def test_partial_shape_is_exact_distinguishes_holes():
    from tools.pet_shape_algebra import partial_shape_is_exact

    assert partial_shape_is_exact(((),))
    assert partial_shape_is_exact(((), ((),)))
    assert not partial_shape_is_exact(None)
    assert not partial_shape_is_exact(((), None))
    assert not partial_shape_is_exact(((None,),))


def test_partial_shape_gamma_min_returns_minimal_compatible_witness():
    from tools.pet_shape_algebra import partial_shape_gamma_min

    assert partial_shape_gamma_min(None) == 2
    assert partial_shape_gamma_min(((), None)) == 6
    assert partial_shape_gamma_min(((None,),)) == 4


def test_partial_shape_completion_neighbors_of_root_hole():
    from tools.pet_shape_algebra import partial_shape_completion_neighbors

    assert partial_shape_completion_neighbors(None) == (((),),)


def test_partial_shape_completion_neighbors_dedups_symmetric_holes():
    from tools.pet_shape_algebra import partial_shape_completion_neighbors

    assert partial_shape_completion_neighbors((None, None)) == ((None, ()),)


def test_partial_shape_completion_neighbors_on_mixed_partial_shape():
    from tools.pet_shape_algebra import partial_shape_completion_neighbors

    got = set(partial_shape_completion_neighbors((None, (None,))))
    expected = {
        ((), (None,)),
        (None, ((),)),
    }

    assert got == expected


def test_partial_shape_completion_neighbors_of_exact_shape_is_empty():
    from tools.pet_shape_algebra import partial_shape_completion_neighbors

    assert partial_shape_completion_neighbors(((),)) == ()


def test_partial_shape_exact_completions_of_exact_shape():
    from tools.pet_shape_algebra import partial_shape_exact_completions

    assert partial_shape_exact_completions(((),)) == (((),),)


def test_partial_shape_exact_completions_of_root_hole():
    from tools.pet_shape_algebra import partial_shape_exact_completions

    assert partial_shape_exact_completions(None) == (((),),)


def test_partial_shape_exact_completions_of_simple_partial():
    from tools.pet_shape_algebra import partial_shape_exact_completions

    assert partial_shape_exact_completions(((), None)) == (((), ()),)


def test_partial_shape_exact_completions_of_nested_partial():
    from tools.pet_shape_algebra import partial_shape_exact_completions

    assert partial_shape_exact_completions((None, (None,))) == (
        ((), ((),)),
    )


def test_partial_shape_gamma_exact_matches_exact_completions():
    from tools.pet_shape_algebra import partial_shape_gamma_exact

    assert partial_shape_gamma_exact(None) == (2,)
    assert partial_shape_gamma_exact(((), None)) == (6,)
    assert partial_shape_gamma_exact((None, (None,))) == (12,)


def test_partial_shape_shortest_completion_path_for_root_hole():
    from tools.pet_shape_algebra import partial_shape_shortest_completion_path

    assert partial_shape_shortest_completion_path(None) == (None, ((),))


def test_partial_shape_shortest_completion_path_for_simple_partial():
    from tools.pet_shape_algebra import partial_shape_shortest_completion_path

    assert partial_shape_shortest_completion_path(((), None)) == (
        (None, ()),
        ((), ()),
    )


def test_partial_shape_completion_distance_for_nested_partial():
    from tools.pet_shape_algebra import partial_shape_completion_distance

    assert partial_shape_completion_distance((None, (None,))) == 2


def test_partial_shape_shortest_completion_path_on_exact_shape_is_trivial():
    from tools.pet_shape_algebra import partial_shape_shortest_completion_path

    assert partial_shape_shortest_completion_path(((),)) == (((),),)


def test_partial_shape_shortest_completion_gamma_matches_min_witness():
    from tools.pet_shape_algebra import partial_shape_shortest_completion_gamma

    assert partial_shape_shortest_completion_gamma(None) == 2
    assert partial_shape_shortest_completion_gamma(((), None)) == 6
    assert partial_shape_shortest_completion_gamma((None, (None,))) == 12


def test_partial_shape_shortest_completion_target_is_exact():
    from tools.pet_shape_algebra import partial_shape_shortest_completion_target

    assert partial_shape_shortest_completion_target(None) == ((),)
    assert partial_shape_shortest_completion_target(((), None)) == ((), ())
    assert partial_shape_shortest_completion_target((None, (None,))) == ((), ((),))


def test_partial_shape_shortest_completion_pet_materializes_target():
    from pet.core import decode
    from tools.pet_shape_algebra import (
        partial_shape_shortest_completion_gamma,
        partial_shape_shortest_completion_pet,
        partial_shape_shortest_completion_target,
        pet_to_shape,
    )

    samples = [None, ((), None), (None, (None,))]

    for partial in samples:
        pet = partial_shape_shortest_completion_pet(partial)
        assert decode(pet) == partial_shape_shortest_completion_gamma(partial)
        assert pet_to_shape(pet) == partial_shape_shortest_completion_target(partial)


def test_partial_shape_report_for_root_hole():
    from tools.pet_shape_algebra import partial_shape_report

    report = partial_shape_report(None)

    assert report["partial"] is None
    assert report["is_exact"] is False
    assert report["hole_count"] == 1
    assert report["fill_min"] == ((),)
    assert report["completion_distance"] == 1
    assert report["target_shape"] == ((),)
    assert report["target_gamma"] == 2


def test_partial_shape_report_for_mixed_partial():
    from tools.pet_shape_algebra import partial_shape_report

    report = partial_shape_report(((), None))

    assert report["is_exact"] is False
    assert report["hole_count"] == 1
    assert report["fill_min"] == ((), ())
    assert report["completion_distance"] == 1
    assert report["target_shape"] == ((), ())
    assert report["target_gamma"] == 6


def test_partial_shape_report_for_exact_shape():
    from tools.pet_shape_algebra import partial_shape_report

    report = partial_shape_report(((),))

    assert report["is_exact"] is True
    assert report["hole_count"] == 0
    assert report["fill_min"] == ((),)
    assert report["completion_distance"] == 0
    assert report["target_shape"] == ((),)
    assert report["target_gamma"] == 2


def test_pet_matches_partial_shape_small_cases():
    from pet.core import encode
    from tools.pet_shape_algebra import pet_matches_partial_shape

    assert pet_matches_partial_shape(encode(6), ((), ()))
    assert pet_matches_partial_shape(encode(12), ((), None))
    assert pet_matches_partial_shape(encode(8), ((None,),))
    assert not pet_matches_partial_shape(encode(8), ((), ()))


def test_n_matches_partial_shape_small_cases():
    from tools.pet_shape_algebra import n_matches_partial_shape

    assert n_matches_partial_shape(6, ((), ()))
    assert n_matches_partial_shape(12, ((), None))
    assert n_matches_partial_shape(8, ((None,),))
    assert not n_matches_partial_shape(8, ((), ()))


def test_partial_shape_report_target_matches_partial():
    from tools.pet_shape_algebra import partial_shape_report, shape_matches_partial

    partial = (None, (None,))
    report = partial_shape_report(partial)

    assert shape_matches_partial(report["target_shape"], partial)


def test_partial_shape_min_exact_names_are_the_semantic_ones():
    from tools.pet_shape_algebra import (
        partial_shape_gamma_min_exact,
        partial_shape_min_exact_completions,
    )

    assert partial_shape_min_exact_completions(None) == (((),),)
    assert partial_shape_gamma_min_exact(None) == (2,)


def test_partial_shape_completion_frontier_for_root_hole():
    from tools.pet_shape_algebra import partial_shape_completion_frontier

    assert partial_shape_completion_frontier(None, 1) == (((),),)

    got = set(partial_shape_completion_frontier(None, 2))
    expected = {
        ((),),
        ((), ()),
        (((),),),
    }
    assert got == expected


def test_partial_shape_completion_frontier_for_mixed_partial():
    from tools.pet_shape_algebra import partial_shape_completion_frontier

    got = set(partial_shape_completion_frontier(((), None), 3))
    expected = {
        ((), ()),
        ((), ((),)),
    }
    assert got == expected


def test_partial_shape_completion_gamma_frontier_small_cases():
    from tools.pet_shape_algebra import partial_shape_completion_gamma_frontier

    assert partial_shape_completion_gamma_frontier(None, 2) == (2, 4, 6)
    assert partial_shape_completion_gamma_frontier(((), None), 3) == (6, 12)


def test_partial_shape_completion_count_small_cases():
    from tools.pet_shape_algebra import partial_shape_completion_count

    assert partial_shape_completion_count(None, 0) == 0
    assert partial_shape_completion_count(None, 1) == 1
    assert partial_shape_completion_count(None, 2) == 3
    assert partial_shape_completion_count(((), None), 3) == 2


def test_partial_shape_completion_levels_for_root_hole():
    from tools.pet_shape_algebra import partial_shape_completion_levels

    levels = partial_shape_completion_levels(None, 3)

    assert levels[0] == (((),),)
    assert set(levels[1]) == {
        ((), ()),
        (((),),),
    }
    assert set(levels[2]) == {
        ((), (), ()),
        ((), ((),)),
        (((), ()),),
        ((((),),),),
    }


def test_partial_shape_completion_levels_for_mixed_partial():
    from tools.pet_shape_algebra import partial_shape_completion_levels

    levels = partial_shape_completion_levels(((), None), 3)

    assert levels[0] == ()
    assert levels[1] == (((), ()),)
    assert levels[2] == (((), ((),)),)


def test_partial_shape_completion_gamma_levels_small_cases():
    from tools.pet_shape_algebra import partial_shape_completion_gamma_levels

    assert partial_shape_completion_gamma_levels(None, 2) == (
        (2,),
        (4, 6),
    )
    assert partial_shape_completion_gamma_levels(((), None), 3) == (
        (),
        (6,),
        (12,),
    )


def test_partial_shape_completion_profile_for_root_hole():
    from tools.pet_shape_algebra import partial_shape_completion_profile

    profile = partial_shape_completion_profile(None, 3)

    assert profile["partial"] is None
    assert profile["max_mass"] == 3
    assert profile["per_mass"] == {1: 1, 2: 2, 3: 4}
    assert profile["cumulative"] == {1: 1, 2: 3, 3: 7}
    assert profile["total"] == 7


def test_partial_shape_completion_profile_for_mixed_partial():
    from tools.pet_shape_algebra import partial_shape_completion_profile

    profile = partial_shape_completion_profile(((), None), 3)

    assert profile["per_mass"] == {1: 0, 2: 1, 3: 1}
    assert profile["cumulative"] == {1: 0, 2: 1, 3: 2}
    assert profile["total"] == 2


def test_partial_shape_completion_profile_for_exact_shape():
    from tools.pet_shape_algebra import partial_shape_completion_profile

    profile = partial_shape_completion_profile(((),), 3)

    assert profile["per_mass"] == {1: 1, 2: 0, 3: 0}
    assert profile["cumulative"] == {1: 1, 2: 1, 3: 1}
    assert profile["total"] == 1


def test_partial_shape_completion_gamma_profile_for_root_hole():
    from tools.pet_shape_algebra import partial_shape_completion_gamma_profile

    profile = partial_shape_completion_gamma_profile(None, 3)

    assert profile["per_mass_count"] == {1: 1, 2: 2, 3: 4}
    assert profile["per_mass_min_gamma"] == {1: 2, 2: 4, 3: 12}
    assert profile["per_mass_gammas"] == {
        1: (2,),
        2: (4, 6),
        3: (12, 16, 30, 64),
    }


def test_partial_shape_completion_gamma_profile_for_mixed_partial():
    from tools.pet_shape_algebra import partial_shape_completion_gamma_profile

    profile = partial_shape_completion_gamma_profile(((), None), 3)

    assert profile["per_mass_count"] == {1: 0, 2: 1, 3: 1}
    assert profile["per_mass_min_gamma"] == {1: None, 2: 6, 3: 12}
    assert profile["per_mass_gammas"] == {
        1: (),
        2: (6,),
        3: (12,),
    }


def test_partial_shape_completion_gamma_profile_for_exact_shape():
    from tools.pet_shape_algebra import partial_shape_completion_gamma_profile

    profile = partial_shape_completion_gamma_profile(((),), 3)

    assert profile["per_mass_count"] == {1: 1, 2: 0, 3: 0}
    assert profile["per_mass_min_gamma"] == {1: 2, 2: None, 3: None}
    assert profile["per_mass_gammas"] == {
        1: (2,),
        2: (),
        3: (),
    }


def test_partial_shape_completion_report_for_root_hole():
    from tools.pet_shape_algebra import partial_shape_completion_report

    report = partial_shape_completion_report(None, 3, preview=3)

    assert report["partial"] is None
    assert report["max_mass"] == 3
    assert report["preview"] == 3
    assert report["is_exact"] is False
    assert report["hole_count"] == 1
    assert report["fill_min"] == ((),)
    assert report["min_target_shape"] == ((),)
    assert report["min_target_gamma"] == 2
    assert report["completion_count"] == 7
    assert report["per_mass_count"] == {1: 1, 2: 2, 3: 4}
    assert report["cumulative_count"] == {1: 1, 2: 3, 3: 7}
    assert report["per_mass_min_gamma"] == {1: 2, 2: 4, 3: 12}
    assert report["preview_exact_shapes"] == (
        ((),),
        ((), ()),
        (((),),),
    )
    assert report["preview_exact_gammas"] == (2, 4, 6)


def test_partial_shape_completion_report_for_mixed_partial():
    from tools.pet_shape_algebra import partial_shape_completion_report

    report = partial_shape_completion_report(((), None), 3, preview=5)

    assert report["is_exact"] is False
    assert report["hole_count"] == 1
    assert report["fill_min"] == ((), ())
    assert report["min_target_shape"] == ((), ())
    assert report["min_target_gamma"] == 6
    assert report["completion_count"] == 2
    assert report["per_mass_count"] == {1: 0, 2: 1, 3: 1}
    assert report["cumulative_count"] == {1: 0, 2: 1, 3: 2}
    assert report["per_mass_min_gamma"] == {1: None, 2: 6, 3: 12}
    assert report["preview_exact_shapes"] == (
        ((), ()),
        ((), ((),)),
    )
    assert report["preview_exact_gammas"] == (6, 12)


def test_partial_shape_completion_report_for_exact_shape():
    from tools.pet_shape_algebra import partial_shape_completion_report

    report = partial_shape_completion_report(((),), 3, preview=5)

    assert report["is_exact"] is True
    assert report["hole_count"] == 0
    assert report["fill_min"] == ((),)
    assert report["min_target_shape"] == ((),)
    assert report["min_target_gamma"] == 2
    assert report["completion_count"] == 1
    assert report["per_mass_count"] == {1: 1, 2: 0, 3: 0}
    assert report["cumulative_count"] == {1: 1, 2: 1, 3: 1}
    assert report["per_mass_min_gamma"] == {1: 2, 2: None, 3: None}
    assert report["preview_exact_shapes"] == (((),),)
    assert report["preview_exact_gammas"] == (2,)


def test_end_to_end_number_partial_completion_flow():
    from pet.core import encode
    from tools.pet_shape_algebra import (
        n_matches_partial_shape,
        partial_shape_completion_report,
        partial_shape_shortest_completion_gamma,
        partial_shape_shortest_completion_target,
        pet_to_shape,
        shape_matches_partial,
    )

    n = 12
    partial = ((), None)

    shape = pet_to_shape(encode(n))
    report = partial_shape_completion_report(partial, max_mass=3, preview=5)
    target = partial_shape_shortest_completion_target(partial)
    gamma = partial_shape_shortest_completion_gamma(partial)

    assert shape == ((), ((),))
    assert shape_matches_partial(shape, partial)
    assert n_matches_partial_shape(n, partial)

    assert report["partial"] == (None, ())
    assert report["hole_count"] == 1
    assert report["is_exact"] is False
    assert report["min_target_shape"] == ((), ())
    assert report["min_target_gamma"] == 6

    assert target == ((), ())
    assert gamma == 6


def test_end_to_end_exact_number_flow_is_stable():
    from pet.core import encode
    from tools.pet_shape_algebra import (
        partial_shape_completion_report,
        partial_shape_shortest_completion_gamma,
        partial_shape_shortest_completion_target,
        pet_to_shape,
    )

    n = 6
    partial = pet_to_shape(encode(n))
    report = partial_shape_completion_report(partial, max_mass=3, preview=5)

    assert partial == ((), ())
    assert report["is_exact"] is True
    assert report["hole_count"] == 0
    assert report["min_target_shape"] == ((), ())
    assert report["min_target_gamma"] == 6
    assert partial_shape_shortest_completion_target(partial) == ((), ())
    assert partial_shape_shortest_completion_gamma(partial) == 6


def test_partial_shape_forced_core_for_root_hole_is_none():
    from tools.pet_shape_algebra import partial_shape_forced_core

    assert partial_shape_forced_core(None, 3) is None


def test_partial_shape_forced_core_for_mixed_partial_recovers_known_leaf():
    from tools.pet_shape_algebra import partial_shape_forced_core

    assert partial_shape_forced_core(((), None), 3) == (None, ())


def test_partial_shape_forced_core_for_exact_shape_is_exact():
    from tools.pet_shape_algebra import partial_shape_forced_core

    assert partial_shape_forced_core(((), ()), 3) == ((), ())


def test_partial_shape_forced_core_for_singleton_bounded_family_is_exact():
    from tools.pet_shape_algebra import partial_shape_forced_core

    assert partial_shape_forced_core((None, (None,)), 3) == ((), ((),))


def test_partial_shape_forced_core_report_small_cases():
    from tools.pet_shape_algebra import partial_shape_forced_core_report

    report = partial_shape_forced_core_report(((), None), 3)

    assert report["partial"] == (None, ())
    assert report["max_mass"] == 3
    assert report["completion_count"] == 2
    assert report["forced_core"] == (None, ())
    assert report["forced_core_kind"] == "partially-structured"
    assert report["forced_hole_count"] == 1
    assert report["is_exact"] is False
    assert report["change_masses"] == (1, 2, 3)


def test_partial_shape_forced_core_trace_for_mixed_partial():
    from tools.pet_shape_algebra import partial_shape_forced_core_trace

    trace = partial_shape_forced_core_trace(((), None), 4)

    assert trace[0] == {
        "max_mass": 1,
        "completion_count": 0,
        "forced_core": None,
        "prev_forced_core": None,
        "changed": True,
        "change_kind": "start",
    }
    assert trace[1] == {
        "max_mass": 2,
        "completion_count": 1,
        "forced_core": ((), ()),
        "prev_forced_core": None,
        "changed": True,
        "change_kind": "strengthen",
    }
    assert trace[2] == {
        "max_mass": 3,
        "completion_count": 2,
        "forced_core": (None, ()),
        "prev_forced_core": ((), ()),
        "changed": True,
        "change_kind": "relax",
    }
    assert trace[3]["max_mass"] == 4
    assert trace[3]["completion_count"] > trace[2]["completion_count"]
    assert trace[3]["forced_core"] == (None, ())
    assert trace[3]["prev_forced_core"] == (None, ())
    assert trace[3]["changed"] is False
    assert trace[3]["change_kind"] == "same"


def test_partial_shape_forced_core_change_masses_small_cases():
    from tools.pet_shape_algebra import partial_shape_forced_core_change_masses

    assert partial_shape_forced_core_change_masses(None, 3) == (1, 2)
    assert partial_shape_forced_core_change_masses(((), None), 4) == (1, 2, 3)


def test_partial_shape_forced_core_stabilization_mass_small_cases():
    from tools.pet_shape_algebra import partial_shape_forced_core_stabilization_mass

    assert partial_shape_forced_core_stabilization_mass(None, 3) == 2
    assert partial_shape_forced_core_stabilization_mass(((), None), 4) == 3


def test_classify_forced_core_delta_small_cases():
    from tools.pet_shape_algebra import classify_forced_core_delta

    assert classify_forced_core_delta(None, None) == "same"
    assert classify_forced_core_delta(None, ((), ())) == "strengthen"
    assert classify_forced_core_delta(((), ()), (None, ())) == "relax"
    assert classify_forced_core_delta((None, ()), (None, ())) == "same"


def test_partial_shape_forced_core_window_helpers_small_cases():
    from tools.pet_shape_algebra import (
        partial_shape_forced_core_meets_window,
        partial_shape_forced_core_stable_window,
    )

    assert partial_shape_forced_core_stable_window(None, 6) == 5
    assert partial_shape_forced_core_meets_window(None, 6, 5)
    assert not partial_shape_forced_core_meets_window(None, 6, 6)

    assert partial_shape_forced_core_stable_window(((), None), 4) == 2
    assert partial_shape_forced_core_meets_window(((), None), 4, 2)
    assert not partial_shape_forced_core_meets_window(((), None), 4, 3)


def test_classify_forced_core_pattern_small_cases():
    from tools.pet_shape_algebra import classify_forced_core_pattern

    assert classify_forced_core_pattern(None) == "empty"
    assert classify_forced_core_pattern((None, None)) == "root-arity-only"
    assert classify_forced_core_pattern(((None,), (None,))) == "partially-structured"
    assert classify_forced_core_pattern(((), ())) == "exact"


def test_partial_shape_free_paths_small_cases():
    from tools.pet_shape_algebra import partial_shape_free_paths

    assert partial_shape_free_paths(None, 3) == ((),)
    assert partial_shape_free_paths((None, (None,)), 8) == ((0,), (1,))
    assert partial_shape_free_paths(((None,), (None,)), 9) == ((0, 0), (1, 0))


def test_partial_shape_residual_small_cases():
    from tools.pet_shape_algebra import partial_shape_residual

    r1 = partial_shape_residual(None, 3)
    assert r1["forced_core"] is None
    assert r1["forced_core_kind"] == "empty"
    assert r1["free_paths"] == ((),)
    assert r1["free_path_count"] == 1

    r2 = partial_shape_residual((None, (None,)), 8)
    assert r2["forced_core"] in ((None, (None,)), (None, None))
    assert r2["forced_core_kind"] == "root-arity-only"
    assert len(r2["free_paths"]) >= 1
    assert r2["free_path_count"] == 2

    r3 = partial_shape_residual(((None,), (None,)), 9)
    assert r3["forced_core"] is not None
    assert r3["forced_core_kind"] == "partially-structured"
    assert len(r3["free_paths"]) >= 1
    assert r3["free_path_count"] == 2


def test_shape_local_gamma_small_cases():
    from tools.pet_shape_algebra import shape_local_gamma

    assert shape_local_gamma(()) == 1
    assert shape_local_gamma(((),)) == 2
    assert shape_local_gamma(((), ())) == 6
    assert shape_local_gamma((((),),)) == 4


def test_partial_shape_residual_profile_small_cases():
    from tools.pet_shape_algebra import partial_shape_residual_profile

    r1 = partial_shape_residual_profile(((), None), 5, preview=5)
    assert r1["forced_core"] == (None, ())
    assert r1["free_paths"] == ((0,),)
    assert r1["per_path"][(0,)]["local_forced_core"] is None
    assert r1["per_path"][(0,)]["local_forced_core_kind"] == "empty"
    assert r1["per_path"][(0,)]["preview_shapes"] == ((), ((),), ((), ()), ((), (), ()), ((), ((),)))
    assert r1["per_path"][(0,)]["preview_local_gammas"] == (1, 2, 6, 12, 30)

    r2 = partial_shape_residual_profile((None, (None,)), 5, preview=5)
    assert r2["forced_core"] in ((None, (None,)), (None, None))
    assert len(r2["free_paths"]) >= 1
    assert all(row["count"] >= 1 for row in r2["per_path"].values())
    

    r3 = partial_shape_residual_profile(((None,), (None,)), 6, preview=5)
    assert r3["forced_core"] is not None
    assert len(r3["free_paths"]) >= 1
    assert all(row["preview_local_gammas"][0] == 1 for row in r3["per_path"].values())
    assert all(row["local_forced_core_kind"] in {"empty", "root-arity-only", "partially-structured", "exact"} for row in r3["per_path"].values())
    


def test_partial_shape_residual_summary_small_cases():
    from tools.pet_shape_algebra import partial_shape_residual_summary

    r1 = partial_shape_residual_summary(((), None), 5, preview=5)
    assert r1["forced_core"] == (None, ())
    assert r1["forced_core_kind"] == "partially-structured"
    assert r1["free_paths"] == ((0,),)
    assert r1["per_path_summary"][(0,)]["local_forced_core"] is None
    assert r1["per_path_summary"][(0,)]["local_forced_core_kind"] == "empty"
    assert r1["per_path_summary"][(0,)]["observed_local_gammas"] == (1, 2, 6, 12, 30)

    r2 = partial_shape_residual_summary(((None,), (None,)), 6, preview=5)
    assert r2["forced_core"] == ((None,), (None,))
    assert r2["forced_core_kind"] == "partially-structured"
    assert r2["free_paths"] == ((0, 0), (1, 0))
    assert r2["per_path_summary"][(0, 0)]["local_forced_core"] is None
    assert r2["per_path_summary"][(1, 0)]["local_forced_core"] is None


def test_partial_shape_forced_core_window_ignores_empty_prefix():
    from tools.pet_shape_algebra import (
        partial_shape_forced_core_meets_window,
        partial_shape_forced_core_stabilization_mass,
        partial_shape_forced_core_stable_window,
    )

    assert partial_shape_forced_core_stabilization_mass(((None,), (None,)), 3) is None
    assert partial_shape_forced_core_stable_window(((None,), (None,)), 3) == 0
    assert not partial_shape_forced_core_meets_window(((None,), (None,)), 3, 1)

    assert partial_shape_forced_core_stabilization_mass(((None,), (None,)), 8) == 6
    assert partial_shape_forced_core_stable_window(((None,), (None,)), 8) == 3
    assert partial_shape_forced_core_meets_window(((None,), (None,)), 8, 3)


def test_exact_shape_local_profile_fast_path_for_symmetric_partial():
    from tools.pet_shape_algebra import exact_shape_local_profile, normalize_shape

    exact = normalize_shape(((((),),), (((), ()),)))
    partial = ((None,), (None,))
    free_paths = ((0, 0), (1, 0))

    local = exact_shape_local_profile(exact, partial, free_paths)

    expected = (((),), ((), ()))
    assert local[(0, 0)] == expected
    assert local[(1, 0)] == expected


def test_partial_shape_residual_profile_root_symmetric_fast_path():
    from tools.pet_shape_algebra import partial_shape_residual_profile

    r = partial_shape_residual_profile((None, (None,)), 6, preview=5)

    assert r["forced_core"] == (None, None)
    assert r["free_paths"] == ((0,), (1,))
    assert r["per_path"][(0,)]["preview_local_gammas"] == (1, 2, 6, 12, 30)
    assert r["per_path"][(1,)]["preview_local_gammas"] == (1, 2, 6, 12, 30)


def test_partial_shape_observed_decomposition_small_cases():
    from tools.pet_shape_algebra import partial_shape_observed_decomposition

    r1 = partial_shape_observed_decomposition(((), None), 5, preview=5)
    assert r1["observed_core"] == (None, ())
    assert r1["observed_core_kind"] == "partially-structured"
    assert r1["residual_free_paths"] == ((0,),)
    assert r1["residual_local_profiles"][(0,)]["local_forced_core"] is None
    assert r1["evidence"]["max_mass"] == 5

    r2 = partial_shape_observed_decomposition((None, (None,)), 6, preview=5)
    assert r2["observed_core"] == (None, None)
    assert r2["observed_core_kind"] == "root-arity-only"
    assert r2["residual_free_paths"] == ((0,), (1,))
