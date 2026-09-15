"""Bounded structural search over PETRA canonical shapes."""

from .atlas import (
    AtlasBackedDistance,
    DistanceAtlas,
    ShapeAtlas,
    build_distance_atlas,
    build_shape_atlas,
    iter_shapes_by_size,
    load_distance_atlas,
    load_shape_atlas,
    save_distance_atlas,
    save_shape_atlas,
)
from .distance import (
    DistanceCache,
    DistanceError,
    int_to_shape,
    structural_distance_numbers,
    structural_distance_shapes,
)
from .projection import (
    PrimeKey,
    ProjectionError,
    ProjectionLimitExceeded,
    project,
)
from .search import Path, ResolverError, Step, resolve
from .structural_algebra import (
    contains,
    join,
    meet,
    structural_overlap,
)
from .verify import (
    StepFailure,
    VerificationResult,
    VerifyError,
    VerifyStep,
    verify_path,
)

__all__ = [
    "AtlasBackedDistance",
    "contains",
    "join",
    "meet",
    "structural_overlap",
    "StepFailure",
    "VerificationResult",
    "VerifyError",
    "VerifyStep",
    "verify_path",
    "DistanceAtlas",
    "DistanceCache",
    "ShapeAtlas",
    "build_distance_atlas",
    "build_shape_atlas",
    "iter_shapes_by_size",
    "load_distance_atlas",
    "load_shape_atlas",
    "save_distance_atlas",
    "save_shape_atlas",
    "DistanceError",
    "Path",
    "PrimeKey",
    "ProjectionError",
    "ProjectionLimitExceeded",
    "ResolverError",
    "Step",
    "int_to_shape",
    "project",
    "resolve",
    "structural_distance_numbers",
    "structural_distance_shapes",
]
