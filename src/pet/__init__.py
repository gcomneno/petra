from .core import (
    PET,
    PETExp,
    PETNode,
    average_leaf_depth,
    leaf_depth_variance,
    branch_profile,
    decode,
    encode,
    height,
    is_prime,
    leaf_count,
    max_branching,
    metrics_dict,
    minimal_shape_representative,
    node_count,
    prime_factorization,
    recursive_mass,
    shape_generator,
    validate,
)
from .io import (
    from_jsonable,
    load_json_file,
    render,
    to_json,
    to_jsonable,
)
from .object_model import (
    compare_address,
    PETAddressComparison,
    PETAddressError,
    PETObject,
    pet_object_from_int,
    structurally_equivalent,
)
from .root_base import (
    PETRootBaseComponent,
    PETRootBase,
    exact_root_base_from_int,
    partial_root_base_components_from_int,
)


def main(argv=None):
    from .cli import main as _main
    return _main(argv)


def cli():
    from .cli import cli as _cli
    return _cli()


__all__ = [
    "PET",
    "PETExp",
    "PETNode",
    "compare_address",
    "PETAddressComparison",
    "partial_root_base_components_from_int",
    "PETRootBaseComponent",
    "exact_root_base_from_int",
    "PETRootBase",
    "PETAddressError",
    "structurally_equivalent",
    "pet_object_from_int",
    "PETObject",
    "average_leaf_depth",
    "leaf_depth_variance",
    "branch_profile",
    "cli",
    "decode",
    "encode",
    "from_jsonable",
    "height",
    "is_prime",
    "leaf_count",
    "load_json_file",
    "main",
    "max_branching",
    "metrics_dict",
    "minimal_shape_representative",
    "node_count",
    "prime_factorization",
    "recursive_mass",
    "render",
    "shape_generator",
    "to_json",
    "to_jsonable",
    "validate",
]
