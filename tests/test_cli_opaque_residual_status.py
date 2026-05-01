from pet.cli import _opaque_residual_status


def test_opaque_residual_status_uses_backbone_lookup_for_small_prime_residual():
    assert _opaque_residual_status(97, backbone_limit=90) == "probable_prime"


def test_opaque_residual_status_keeps_large_residual_opaque_outside_lookup_budget():
    residual = int("9" * 50)

    assert (
        _opaque_residual_status(residual, backbone_limit=1_000_000)
        == "composite_or_unknown"
    )
