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
    PETObject,
    pet_object_from_int,
    structurally_equivalent,
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
