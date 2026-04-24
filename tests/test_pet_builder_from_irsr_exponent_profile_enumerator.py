from __future__ import annotations

from pet.builder_from_irsr import _generate_allowed_exponent_profiles_v2


def test_exponent_profile_enumerator_v2_reproduces_current_rollout() -> None:
    assert _generate_allowed_exponent_profiles_v2(
        max_support_size=2,
        max_total_weight=3,
    ) == [
        [2],
        [2, 1],
    ]


def test_exponent_profile_enumerator_v2_excludes_unwanted_profiles() -> None:
    profiles = _generate_allowed_exponent_profiles_v2(
        max_support_size=2,
        max_total_weight=3,
    )

    assert [1] not in profiles
    assert [1, 1] not in profiles
    assert [3] not in profiles
    assert [2, 2] not in profiles
